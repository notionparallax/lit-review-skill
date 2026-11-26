"""Work with the local Zotero library (Zotero desktop + Better BibTeX).

    python -I zotero.py status                       # is Zotero running? which collection is selected?
    python -I zotero.py find 10.1037/0021-9010.80.3.339
    python -I zotero.py find hot desking wellbeing   # words in the title
    python -I zotero.py export --out refs.json       # whole library as CSL JSON
    python -I zotero.py add 10.1234/a 10.5678/b --tag needs-pdf [--dry-run]
    python -I zotero.py attachments smithOfficeLayout2021

`add` looks each DOI up in Crossref, skips any already in the library, and
saves the rest through the Zotero connector into the collection currently
selected in the Zotero window. Citation keys are assigned by Better BibTeX;
`add` prints them once they appear.

Only the standard library is used. Zotero must be running.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ZOTERO = "http://127.0.0.1:23119"
EXPORT = ZOTERO + "/better-bibtex/export/library?/1/library.json"
RPC = ZOTERO + "/better-bibtex/json-rpc"
UA = {"User-Agent": "lit-review-skill/1.0"}

CROSSREF_TYPES = {
    "journal-article": "journalArticle", "proceedings-article": "conferencePaper",
    "book-chapter": "bookSection", "book": "book", "monograph": "book", "edited-book": "book",
    "report": "report", "posted-content": "preprint", "dissertation": "thesis",
    "reference-entry": "encyclopediaArticle", "dataset": "dataset", "standard": "standard",
}
CONTAINER_FIELD = {"journalArticle": "publicationTitle", "conferencePaper": "proceedingsTitle",
                   "bookSection": "bookTitle", "encyclopediaArticle": "encyclopediaTitle",
                   "preprint": "repository", "report": "institution"}
VALID_FIELDS = {
    "journalArticle": {"volume", "issue", "pages", "ISSN"},
    "conferencePaper": {"volume", "pages", "publisher", "ISBN"},
    "bookSection": {"volume", "pages", "publisher", "ISBN"},
    "book": {"volume", "publisher", "ISBN"},
    "encyclopediaArticle": {"volume", "pages", "publisher", "ISBN"},
    "report": {"pages"},
    "preprint": set(),
    "thesis": set(),
    "dataset": {"publisher"},
    "standard": {"publisher"},
}


def http(url, data=None, headers=None, timeout=30):
    body = json.dumps(data).encode() if data is not None else None
    h = dict(UA, **(headers or {}))
    if body is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return r.status, raw.decode("utf-8") if raw else ""


def running() -> bool:
    try:
        return http(ZOTERO + "/connector/ping", timeout=3)[0] == 200
    except (urllib.error.URLError, OSError):
        return False


def installed() -> tuple[bool | None, bool | None]:
    """(Zotero installed?, Better BibTeX installed?) from the file system, for when
    Zotero isn't running. None means 'couldn't tell'."""
    import os
    from pathlib import Path
    home = Path.home()
    apps = [Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Zotero",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Zotero",
            Path(os.environ.get("LOCALAPPDATA", str(home))) / "Programs" / "Zotero",
            Path("/Applications/Zotero.app"), home / "Applications" / "Zotero.app",
            Path("/usr/lib/zotero"), Path("/opt/zotero"), home / "Zotero_linux-x86_64"]
    app = any(p.exists() for p in apps)
    profiles = [Path(os.environ.get("APPDATA", str(home))) / "Zotero" / "Zotero" / "Profiles",
                home / "Library" / "Application Support" / "Zotero" / "Profiles", home / ".zotero" / "zotero"]
    seen_profile, bbt = False, False
    for root in profiles:
        if root.exists():
            seen_profile = True
            bbt = bbt or any(root.glob("*/extensions/better-bibtex*"))
    return (app or None) if not seen_profile else True, bbt if seen_profile else None


def describe_install() -> str:
    app, bbt = installed()
    yn = {True: "yes", False: "no", None: "can't tell"}
    return f"Zotero installed: {yn[app]}; Better BibTeX installed: {yn[bbt]}"


def need_zotero():
    if not running():
        sys.exit("Zotero is not reachable at 127.0.0.1:23119. Start Zotero desktop and try again.")


def library() -> list[dict]:
    try:
        return json.loads(http(EXPORT, timeout=120)[1])
    except urllib.error.HTTPError as e:
        sys.exit(f"Better BibTeX export failed ({e.code}). Is Better BibTeX installed?")


def norm_doi(d: str) -> str:
    d = (d or "").strip().lower()
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", d)


def selected_collection() -> str:
    try:
        _, body = http(ZOTERO + "/connector/getSelectedCollection", data={})
        j = json.loads(body)
        return j.get("name") or j.get("libraryName") or "(unknown)"
    except Exception as e:  # noqa: BLE001 - report, don't crash
        return f"(could not read: {e})"


def cmd_status(_):
    if not running():
        print("Zotero: NOT running. " + describe_install() +
              ". If installed, start Zotero desktop; otherwise see stage 0.")
        sys.exit(1)
    print("Zotero: running")
    print("Selected collection:", selected_collection())
    try:
        lib = library()
        print(f"Better BibTeX: OK, {len(lib)} items in the library")
    except SystemExit as e:
        print("Better BibTeX:", e)
        sys.exit(1)


def cmd_find(a):
    need_zotero()
    lib = library()
    q = " ".join(a.query)
    doi = norm_doi(q) if re.match(r"^(https?://|doi:)?(dx\.)?(doi\.org/)?10\.", q.strip(), re.I) else None
    words = [w.lower() for w in re.findall(r"\w+", q)]
    hits = []
    for it in lib:
        if doi:
            if norm_doi(it.get("DOI")) == doi:
                hits.append(it)
        else:
            hay = " ".join([it.get("title", ""), it.get("id", "")] +
                           [c.get("family", "") for c in it.get("author", [])]).lower()
            if all(w in hay for w in words):
                hits.append(it)
    for it in hits[:30]:
        year = (it.get("issued", {}).get("date-parts") or [[""]])[0][0]
        print(f"{it['id']}\t{year}\t{it.get('title', '')[:90]}\t{it.get('DOI', '')}")
    print(f"{len(hits)} match(es)" + (" (first 30 shown)" if len(hits) > 30 else ""))


def cmd_export(a):
    need_zotero()
    lib = library()
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(lib, fh, ensure_ascii=False, indent=1)
    print(f"Wrote {len(lib)} items to {a.out}")


CSL_TYPES = {"article-journal": "journal-article", "paper-conference": "proceedings-article",
             "chapter": "book-chapter", "book": "book", "report": "report", "thesis": "dissertation",
             "dataset": "dataset", "article": "posted-content", "entry-encyclopedia": "reference-entry"}


def crossref(doi: str) -> dict | None:
    """Metadata for a DOI: Crossref first, then doi.org content negotiation
    (which also covers DataCite DOIs such as arXiv and Zenodo)."""
    try:
        _, body = http("https://api.crossref.org/works/" + urllib.parse.quote(doi), timeout=30)
        return json.loads(body)["message"]
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        pass
    try:
        _, body = http("https://doi.org/" + urllib.parse.quote(doi),
                       headers={"Accept": "application/vnd.citationstyles.csl+json"}, timeout=30)
        c = json.loads(body)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return None
    # Reshape CSL JSON into the Crossref layout that to_zotero() reads.
    as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])  # noqa: E731
    return {"type": CSL_TYPES.get(c.get("type"), "journal-article"), "title": as_list(c.get("title")),
            "author": c.get("author", []), "editor": c.get("editor", []), "issued": c.get("issued", {}),
            "container-title": as_list(c.get("container-title")), "volume": c.get("volume"),
            "issue": c.get("issue"), "page": c.get("page"), "publisher": c.get("publisher"),
            "DOI": c.get("DOI", doi), "URL": c.get("URL", "https://doi.org/" + doi),
            "abstract": c.get("abstract"), "ISSN": as_list(c.get("ISSN")), "ISBN": as_list(c.get("ISBN"))}


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def to_zotero(m: dict, tags: list[str]) -> dict:
    itype = CROSSREF_TYPES.get(m.get("type"), "journalArticle")
    item = {"itemType": itype, "title": clean((m.get("title") or [""])[0]),
            "creators": [], "DOI": m.get("DOI", ""), "url": m.get("URL", ""),
            "tags": [{"tag": t} for t in tags], "attachments": [], "notes": []}
    for role, key in (("author", "author"), ("editor", "editor")):
        for p in m.get(key, []):
            if "family" in p:
                item["creators"].append({"creatorType": role, "lastName": p["family"], "firstName": p.get("given", "")})
            elif "name" in p:
                item["creators"].append({"creatorType": role, "name": p["name"], "fieldMode": 1})
    parts = (m.get("published") or m.get("issued") or {}).get("date-parts") or [[]]
    item["date"] = "-".join(f"{x:02d}" if i else str(x) for i, x in enumerate(parts[0]) if x)
    cont = (m.get("container-title") or [""])[0]
    if cont and itype in CONTAINER_FIELD:
        item[CONTAINER_FIELD[itype]] = clean(cont)
    if itype == "preprint" and not cont:
        item["repository"] = m.get("publisher", "")
    # Only fields valid for the item type; the connector rejects others.
    allowed = VALID_FIELDS.get(itype, set())
    values = {"volume": m.get("volume"), "issue": m.get("issue"), "pages": m.get("page"),
              "publisher": m.get("publisher"), "ISSN": (m.get("ISSN") or [None])[0],
              "ISBN": (m.get("ISBN") or [None])[0]}
    for field, value in values.items():
        if value and field in allowed:
            item[field] = value
    if itype == "report" and not item.get("institution") and m.get("publisher"):
        item["institution"] = m["publisher"]
    if itype == "thesis" and m.get("publisher"):
        item["university"] = m["publisher"]
    if m.get("abstract"):
        item["abstractNote"] = clean(m["abstract"])
    item["id"] = "lr" + re.sub(r"\W", "", item["DOI"])[-20:]
    return item


def cmd_add(a):
    dois = [norm_doi(d) for d in a.dois]
    held = {}
    if running():
        held = {norm_doi(it.get("DOI")): it["id"] for it in library() if it.get("DOI")}
    elif not a.dry_run:
        need_zotero()
    items, report = [], []
    for d in dois:
        if d in held:
            report.append(f"{d}\talready in library as {held[d]}")
            continue
        m = crossref(d)
        if not m:
            report.append(f"{d}\tNOT FOUND at Crossref or doi.org; add it by hand (Zotero 'Add item by identifier' or the browser connector)")
            continue
        items.append(to_zotero(m, a.tag))
        time.sleep(0.2)
    if a.dry_run:
        print(json.dumps(items, indent=1, ensure_ascii=False))
    elif items:
        print("Saving into collection:", selected_collection())
        http(ZOTERO + "/connector/saveItems",
             data={"sessionID": f"lr-{time.time():.0f}", "uri": "https://doi.org/", "items": items}, timeout=60)
        time.sleep(3)  # Better BibTeX assigns keys asynchronously
        now = {norm_doi(it.get("DOI")): it["id"] for it in library() if it.get("DOI")}
        for it in items:
            d = norm_doi(it["DOI"])
            report.append(f"{d}\tadded as {now.get(d, '(key not assigned yet; run find later)')}\t{it['title'][:70]}")
    for line in report:
        print(line)


def cmd_attachments(a):
    need_zotero()
    try:
        _, body = http(RPC, data={"jsonrpc": "2.0", "method": "item.attachments", "params": [a.key]})
        res = json.loads(body)
    except urllib.error.HTTPError as e:
        sys.exit(f"Better BibTeX JSON-RPC failed ({e.code})")
    if "error" in res:
        sys.exit(f"{a.key}: {res['error'].get('message')}")
    paths = [r.get("path") for r in res.get("result", []) if r.get("path")]
    print("\n".join(paths) if paths else f"{a.key}: no file attachments")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(f=cmd_status)
    p = sub.add_parser("find"); p.add_argument("query", nargs="+"); p.set_defaults(f=cmd_find)
    p = sub.add_parser("export"); p.add_argument("--out", default="refs.json"); p.set_defaults(f=cmd_export)
    p = sub.add_parser("add"); p.add_argument("dois", nargs="+")
    p.add_argument("--tag", action="append", default=[]); p.add_argument("--dry-run", action="store_true")
    p.set_defaults(f=cmd_add)
    p = sub.add_parser("attachments"); p.add_argument("key"); p.set_defaults(f=cmd_attachments)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
