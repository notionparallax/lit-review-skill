"""Check and build a literature review written in pandoc markdown.

    python -I build_review.py review.md              # check, then build review.docx and review.html
    python -I build_review.py review.md --check-only # checks and word counts, no build
    python -I build_review.py --check-tools          # is everything installed?

Steps:
1. Find every citation key in the review ('@key', '[@a; @b]').
2. Pull the library from Zotero's Better BibTeX endpoint (Zotero must be
   running), keep only the cited items, and write refs.json beside the review.
   If Zotero is not reachable, use the existing refs.json and say so.
3. Report keys that are cited but not in the library.
4. Compare the cited keys with the source notes (05_sources.md beside the
   review, entries headed '### @key' with a '**Status:**' line): cited keys
   with no note, and cited keys marked UNVERIFIED.
5. Lint for faults pandoc does not report (plain-text citations, '~' for
   approximately, hand-typed cross-references to missing labels, unresolved
   [[comments]]).
6. Build Word and HTML with citeproc and the APA style. If review.defaults.yaml
   exists beside the review, pandoc takes its options from there instead
   (for a Word template, pandoc-crossref and so on).
7. Print word counts per top-level section, leaving out references, tables,
   comments and front matter.
Exit status is 0 unless the build itself fails (--check-tools: 1 if anything
is missing or Zotero is not reachable).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
SKILL = Path(__file__).resolve().parent.parent
ZOTERO_EXPORT = "http://127.0.0.1:23119/better-bibtex/export/library?/1/library.json"
DROP_FIELDS = {"abstract", "note", "file", "keyword"}
CROSSREF_PREFIXES = ("sec:", "tbl:", "fig:", "eq:", "lst:")

LINT_RULES = [
    (r"(?<![\w/])~ ?\d", 0, "use '≈' for 'approximately'"),
    (r"\b[A-Z][\w'-]+ (?:et al\.|and [A-Z][\w'-]+|& [A-Z][\w'-]+) \(\d{4}", 0, "plain-text citation; cite by key"),
    (r"\[\[", 0, "unresolved [[comment]]"),
    (r"\b(?:Sections?|Tables?|Figures?) \d", 0, "hand-typed number; fine without pandoc-crossref, but check it"),
]


def strip_non_prose(text: str) -> str:
    """Blank out front matter, comments and code, keeping line numbers."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))  # noqa: E731
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\A---\n.*?\n(---|\.\.\.)\n", blank, text, flags=re.S)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    text = re.sub(r"^(```|~~~).*?^\1", blank, text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", blank, text)


def cited_keys(text: str) -> set[str]:
    text = re.sub(r"\[\[.*?\]\]", " ", strip_non_prose(text), flags=re.S)
    found = re.findall(r"(?<![A-Za-z0-9_.@-])-?@([A-Za-z0-9_][A-Za-z0-9_:.#$%&+?<>~/-]*)", text)
    keys = {k.rstrip(".:-+/?") for k in found}
    return {k for k in keys if not k.startswith(CROSSREF_PREFIXES)}


def lint(text: str) -> list[str]:
    lines = strip_non_prose(text).split("\n")
    problems = []
    for pattern, flags, message in LINT_RULES:
        for n, line in enumerate(lines, 1):
            for m in re.finditer(pattern, line, flags):
                problems.append(f"line {n}: '{m.group(0)}': {message}")
    defined = {lab for line in lines for lab in re.findall(r"\{#((?:sec|tbl|fig|eq|lst):[\w-]+)", line)}
    for n, line in enumerate(lines, 1):
        for lab in re.findall(r"(?<![\w{#])-?@((?:sec|tbl|fig|eq|lst):[\w-]*\w)", line):
            if lab not in defined:
                problems.append(f"line {n}: '@{lab}': no such label")
    return problems


def statuses(notes: Path) -> dict[str, str]:
    """Map key -> status line from 05_sources.md ('### @key' then '**Status:** ...')."""
    out, key = {}, None
    for line in notes.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{2,4}\s+@([^\s]+)", line)
        if m:
            key = m.group(1).rstrip(".:,")
            out.setdefault(key, "")
            continue
        m = re.search(r"\*\*Status:\*\*\s*(.*)", line)
        if key and m:
            out[key] = m.group(1).strip()
    return out


def load_library(refs_path: Path, offline: bool) -> tuple[list[dict], str]:
    if not offline:
        try:
            with urllib.request.urlopen(ZOTERO_EXPORT, timeout=60) as resp:
                return json.load(resp), "Zotero (live library)"
        except Exception as exc:  # noqa: BLE001 - Zotero closed, plugin missing, timeout
            print(f"Zotero not reachable ({exc}).")
    if refs_path.exists():
        print(f"Using the saved {refs_path.name}; references added to Zotero since it was written are missing.")
        return json.loads(refs_path.read_text(encoding="utf-8")), refs_path.name
    print("No refs.json either: citations will not resolve. Start Zotero and rebuild.")
    return [], "nothing"


def word_counts(text: str) -> list[tuple[str, int]]:
    text = strip_non_prose(text)
    text = re.sub(r"\[\[.*?\]\]", " ", text, flags=re.S)
    sections, title, words = [], "(before first heading)", 0
    for line in text.split("\n"):
        h = re.match(r"^#\s+(.*?)\s*(\{.*\})?\s*$", line)
        if h:
            if words or sections:
                sections.append((title, words))
            title, words = h.group(1), 0
            continue
        if line.lstrip().startswith(("|", "#", "![", ":::", "Table:")):
            continue
        line = re.sub(r"\[[^\]]*@[^\]]*\]", " ", line)  # bracketed citations
        line = re.sub(r"-?@[\w:.-]+", "Author", line)  # narrative citations count as a word
        words += len(re.findall(r"[A-Za-z0-9≈%'’-]+", line))
    sections.append((title, words))
    return [s for s in sections if s[0].lower() not in ("references", "bibliography")]


def check_tools() -> bool:
    """Report each tool; return True if everything needed is installed and reachable."""
    ok = True
    for name, args in (("python", None), ("git", ["--version"]), ("pandoc", ["--version"])):
        exe = sys.executable if name == "python" else shutil.which(name)
        if not exe:
            print(f"{name}: NOT FOUND")
            ok = False
            continue
        if name == "python":
            ver = sys.version.split()[0]
        else:
            ver = subprocess.run([exe, *args], capture_output=True, text=True).stdout.split("\n")[0]
        print(f"{name}: {ver}")
    if shutil.which("git"):
        who = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
        print("git identity: " + (who or "NOT SET (the person should set user.name and user.email)"))
        ok = ok and bool(who)
    try:
        with urllib.request.urlopen(ZOTERO_EXPORT, timeout=30) as r:
            print(f"Zotero + Better BibTeX: running, OK ({len(json.load(r))} items)")
    except Exception:  # noqa: BLE001 - closed, not installed, or plugin missing
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from zotero import describe_install, running  # noqa: E402
        state = "running, but Better BibTeX not answering" if running() else "not running"
        print(f"Zotero: {state}. {describe_install()}.")
        ok = False
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("review", nargs="?")
    ap.add_argument("--check-only", action="store_true", help="checks and word counts; don't build")
    ap.add_argument("--offline", action="store_true", help="don't contact Zotero; use the saved refs.json")
    ap.add_argument("--notes", help="source notes file (default: 05_sources.md beside the review)")
    ap.add_argument("--check-tools", action="store_true", help="report which tools are installed, then stop")
    a = ap.parse_args()
    if a.check_tools or a.review is None:
        sys.exit(0 if check_tools() else 1)

    md = Path(a.review).resolve()
    folder = md.parent
    text = md.read_text(encoding="utf-8")
    keys = cited_keys(text)
    refs_path = folder / "refs.json"

    library, source = load_library(refs_path, a.offline)
    by_key = {item.get("citation-key") or item.get("id"): item for item in library}
    wanted = {k: by_key[k] for k in sorted(keys) if k in by_key}
    missing = sorted(keys - set(wanted))
    if source != refs_path.name and library:
        slim = [{k: v for k, v in item.items() if k not in DROP_FIELDS} for item in wanted.values()]
        refs_path.write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nCitations: {len(keys)} keys cited; {len(wanted)} found in {source}.")
    if missing:
        print("  NOT IN THE LIBRARY (add to Zotero, or fix the key):\n    " + "\n    ".join(missing))

    notes = Path(a.notes) if a.notes else folder / "05_sources.md"
    if notes.exists():
        st = statuses(notes)
        no_note = sorted(k for k in keys if k not in st)
        blank = sorted(k for k in keys if k in st and not st[k])
        unver = sorted(k for k in keys if "UNVERIFIED" in st.get(k, "").upper())
        partial = sorted(k for k in keys if "PARTIAL" in st.get(k, "").upper())
        print(f"\nSource notes ({notes.name}): {len(keys) - len(no_note)} of {len(keys)} cited keys have a note; "
              f"{len(partial)} PARTIAL.")
        if no_note:
            print("  CITED WITH NO NOTE (write one in stage 5 before relying on it):\n    " + "\n    ".join(no_note))
        if blank:
            print("  NOTE BUT NO STATUS:\n    " + "\n    ".join(blank))
        if unver:
            print("  CITED BUT UNVERIFIED (remove, or verify and update the status):\n    " + "\n    ".join(unver))
    else:
        print(f"\nNo source notes found at {notes}; statuses not checked.")

    problems = lint(text)
    print(f"\nLint: {len(problems)} warning(s)")
    for p in problems:
        print("  " + p)

    print("\nWords per section (excluding tables, citations in brackets, comments):")
    total = 0
    for title, n in word_counts(text):
        print(f"  {n:6,}  {title}")
        total += n
    print(f"  {total:6,}  total")

    if a.check_only:
        return
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("\npandoc not found on PATH; install it from https://pandoc.org/installing.html")
    defaults = md.with_name(md.stem + ".defaults.yaml")
    csl = folder / ".csl" / "apa.csl"
    if not csl.exists():
        csl = SKILL / "assets" / "apa.csl"
    if defaults.exists():
        options = ["--defaults", str(defaults)]
    else:
        options = ["--citeproc"]
    common = [pandoc, str(md), "--from", "markdown", *options, "--bibliography", str(refs_path),
              "--csl", str(csl), "--resource-path", str(folder)]
    html, docx = md.with_suffix(".html"), md.with_suffix(".docx")
    sys.stdout.flush()
    subprocess.run(common + ["--standalone", "--embed-resources", "-o", str(html)], check=True, cwd=folder)
    ref_doc = folder / "templates" / "reference.docx"
    extra = ["--reference-doc", str(ref_doc)] if ref_doc.exists() and not defaults.exists() else []
    subprocess.run(common + extra + ["-o", str(docx)], check=True, cwd=folder)
    print(f"\nBuilt {docx.name} and {html.name}")


if __name__ == "__main__":
    main()
