"""Logged searches in OpenAlex, written to a CSV for screening.

    # Run every string in strings.json; top 100 each by relevance, from 2000, English
    python -I openalex_search.py search search/strings.json --per-string 100 --from 2000 --out search/

    # Which seed papers does each string find? (seeds: a text file, one DOI per line)
    python -I openalex_search.py seeds search/strings.json search/seeds.txt --from 2000

    # Follow references from included papers: backward (what they cite), forward (what cites them)
    python -I openalex_search.py chase 10.1037/0021-9010.80.3.339 W2910366792 --out search/ [--forward-limit 100]

strings.json maps a short name to an OpenAlex boolean string, e.g.
    {"S1_hotdesking": "(\"hot desking\" OR \"desk sharing\") AND (wellbeing OR satisfaction)"}
Strings search titles and abstracts (filter title_and_abstract.search).

Outputs, in --out:
  records.csv      one row per unique record. Re-running merges: rows already
                   there keep their screening columns (decision, code, reason).
  query_log.json   every query run: date, name, exact URL, total count.
If a refs.json (CSL JSON from Zotero) is found next to the review, records
already in the library are marked in held_key.

Set OPENALEX_API_KEY for higher rate limits (optional).
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
API = "https://api.openalex.org/works"
SELECT = ("id,doi,title,publication_year,type,primary_location,abstract_inverted_index,"
          "authorships,open_access,cited_by_count")
FIELDS = ["openalex_id", "found_by", "rank", "doi", "year", "type", "title", "authors", "venue",
          "cited_by", "oa_url", "abstract", "held_key", "decision", "code", "reason"]
KEEP = ("decision", "code", "reason")


def get(url: str) -> dict:
    key = os.environ.get("OPENALEX_API_KEY")
    full = url + (f"&api_key={key}" if key else "")
    for attempt in range(6):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": "lit-review-skill/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503):
                raise SystemExit(f"OpenAlex error {e.code} for {url}\n{e.read()[:300]!r}")
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(5 * (attempt + 1))
    raise SystemExit(f"OpenAlex did not respond: {url}")


def abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = {p: w for w, ps in inv.items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))


def norm(t: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:60]


def bare_doi(d: str | None) -> str:
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", (d or "").strip().lower())


def search_filter(q: str, year_from: int | None, lang: str | None) -> str:
    # Commas separate OpenAlex filters, so they can't appear inside the string.
    f = "title_and_abstract.search:" + urllib.parse.quote(q.replace(",", " "))
    if year_from:
        f += f",from_publication_date:{year_from}-01-01"
    if lang:
        f += f",language:{lang}"
    return f


def to_row(w: dict, found_by: str, rank: int | str) -> dict:
    loc = (w.get("primary_location") or {}).get("source") or {}
    authors = [a["author"]["display_name"] for a in (w.get("authorships") or [])]
    au = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
    return {"openalex_id": w["id"].rsplit("/", 1)[-1], "found_by": found_by, "rank": rank,
            "doi": bare_doi(w.get("doi")), "year": w.get("publication_year") or "", "type": w.get("type") or "",
            "title": w.get("title") or "", "authors": au, "venue": loc.get("display_name") or "",
            "cited_by": w.get("cited_by_count") or 0, "oa_url": (w.get("open_access") or {}).get("oa_url") or "",
            "abstract": abstract(w.get("abstract_inverted_index"))}


def find_refs_json(out: Path) -> Path | None:
    for p in (out / "refs.json", out.parent / "refs.json", Path("refs.json")):
        if p.exists():
            return p
    return None


class Store:
    """records.csv and query_log.json in one folder, merged on each run."""

    def __init__(self, out: Path):
        self.out = out
        out.mkdir(parents=True, exist_ok=True)
        self.path, self.log_path = out / "records.csv", out / "query_log.json"
        self.rows: dict[str, dict] = {}
        if self.path.exists():
            with open(self.path, encoding="utf-8", newline="") as fh:
                self.rows = {r["openalex_id"]: r for r in csv.DictReader(fh)}
        self.log = json.loads(self.log_path.read_text(encoding="utf-8")) if self.log_path.exists() else []
        self.held_doi, self.held_title = {}, {}
        refs = find_refs_json(out)
        if refs:
            for r in json.loads(refs.read_text(encoding="utf-8")):
                if r.get("DOI"):
                    self.held_doi[bare_doi(r["DOI"])] = r["id"]
                if r.get("title"):
                    self.held_title[norm(r["title"])] = r["id"]
        self.new = 0

    def add(self, row: dict):
        rid = row["openalex_id"]
        if rid in self.rows:
            old = self.rows[rid]
            tags = set(filter(None, old.get("found_by", "").split(";")))
            if row["found_by"] not in tags:
                old["found_by"] = ";".join(sorted(tags | {row["found_by"]}))
            return
        row["held_key"] = self.held_doi.get(row["doi"]) or self.held_title.get(norm(row["title"])) or ""
        for k in KEEP:
            row.setdefault(k, "")
        self.rows[rid] = row
        self.new += 1

    def note(self, name: str, url: str, count: int, fetched: int):
        self.log.append({"date": dt.date.today().isoformat(), "name": name, "count": count,
                         "fetched": fetched, "url": url})

    def save(self):
        with open(self.path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(self.rows.values())
        self.log_path.write_text(json.dumps(self.log, indent=1, ensure_ascii=False), encoding="utf-8")


def fetch(url_base: str, limit: int) -> tuple[list[dict], int]:
    """Up to `limit` results, using cursor paging."""
    out, cursor, total = [], "*", 0
    while cursor and len(out) < limit:
        res = get(f"{url_base}&per-page={min(200, limit)}&cursor={cursor}")
        total = res["meta"]["count"]
        out += res["results"]
        cursor = res["meta"].get("next_cursor")
        if not res["results"]:
            break
        time.sleep(0.2)
    return out[:limit], total


def cmd_search(a):
    strings = json.loads(Path(a.strings).read_text(encoding="utf-8"))
    store = Store(Path(a.out))
    for name, q in strings.items():
        base = f"{API}?filter={search_filter(q, a.year_from, a.lang)}&sort=relevance_score:desc&select={SELECT}"
        results, total = fetch(base, a.per_string)
        for rank, w in enumerate(results, 1):
            store.add(to_row(w, name, rank))
        store.note(name, base, total, len(results))
        print(f"{name}: {total:,} records in OpenAlex; top {len(results)} fetched")
    store.save()
    held = sum(1 for r in store.rows.values() if r.get("held_key"))
    todo = sum(1 for r in store.rows.values() if not r.get("held_key") and not r.get("decision"))
    print(f"\n{len(store.rows)} unique records in {store.path} ({store.new} new); "
          f"{held} already in the library; {todo} to screen")


def cmd_seeds(a):
    strings = json.loads(Path(a.strings).read_text(encoding="utf-8"))
    seeds = [bare_doi(l) for l in Path(a.seeds).read_text(encoding="utf-8").split() if "10." in l]
    if not seeds:
        raise SystemExit("No DOIs found in the seeds file (one DOI per line).")
    found_any: set[str] = set()
    print(f"{len(seeds)} seeds\n")
    for name, q in strings.items():
        hits = set()
        for i in range(0, len(seeds), 50):
            chunk = "|".join("https://doi.org/" + d for d in seeds[i:i + 50])
            url = f"{API}?filter={search_filter(q, a.year_from, a.lang)},doi:{chunk}&select=doi&per-page=50"
            hits |= {bare_doi(w["doi"]) for w in get(url)["results"]}
        found_any |= hits
        print(f"{name}: finds {len(hits)} of {len(seeds)} seeds ({100 * len(hits) // len(seeds)}%)")
        for d in seeds:
            if d not in hits:
                print(f"    misses {d}")
    missed = [d for d in seeds if d not in found_any]
    print(f"\nAll strings together find {len(seeds) - len(missed)} of {len(seeds)}.")
    if missed:
        print("Found by no string (check vocabulary, date limit, or whether OpenAlex has an abstract):")
        for d in missed:
            print("   ", d)


def work_id(ident: str) -> str:
    ident = ident.strip()
    if re.match(r"^W\d+$", ident):
        return ident
    res = get(f"{API}/https://doi.org/{urllib.parse.quote(bare_doi(ident))}?select=id")
    return res["id"].rsplit("/", 1)[-1]


def cmd_chase(a):
    store = Store(Path(a.out))
    for ident in a.ids:
        wid = work_id(ident)
        w = get(f"{API}/{wid}?select=id,title,referenced_works")
        refs = [r.rsplit("/", 1)[-1] for r in w.get("referenced_works", [])]
        got = 0
        for i in range(0, len(refs), 50):
            res = get(f"{API}?filter=openalex:{'|'.join(refs[i:i + 50])}&select={SELECT}&per-page=50")
            for x in res["results"]:
                store.add(to_row(x, f"back:{wid}", ""))
                got += 1
        store.note(f"back:{wid}", f"{API}/{wid} referenced_works", len(refs), got)
        base = f"{API}?filter=cites:{wid}&sort=cited_by_count:desc&select={SELECT}"
        fwd, total = fetch(base, a.forward_limit)
        for x in fwd:
            store.add(to_row(x, f"fwd:{wid}", ""))
        store.note(f"fwd:{wid}", base, total, len(fwd))
        print(f"{wid} {(w.get('title') or '')[:60]}: {len(refs)} references; "
              f"{total} citing works, {len(fwd)} most-cited fetched")
    store.save()
    print(f"\n{store.new} new records added to {store.path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("search", "seeds"):
        p = sub.add_parser(name)
        p.add_argument("strings")
        if name == "seeds":
            p.add_argument("seeds")
        p.add_argument("--from", dest="year_from", type=int, default=None)
        p.add_argument("--lang", default="en")
        if name == "search":
            p.add_argument("--per-string", type=int, default=100)
            p.add_argument("--out", default="search")
        p.set_defaults(f=cmd_search if name == "search" else cmd_seeds)
    p = sub.add_parser("chase")
    p.add_argument("ids", nargs="+", help="DOIs or OpenAlex work IDs (W...)")
    p.add_argument("--forward-limit", type=int, default=100)
    p.add_argument("--out", default="search")
    p.set_defaults(f=cmd_chase)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
