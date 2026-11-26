"""Flag prose patterns to avoid in a literature review (see references/writing.md).

    python -I style_check.py review.md               # whole file
    python -I style_check.py review.md --since HEAD  # only paragraphs changed since a git ref
    python -I style_check.py review.md --rules opener,agent

Advisory, not a gate: every hit is a prompt to reread the sentence, and some
will be fine as written. Rules come from an author's comments on drafts (in
the review this skill came from) and the house-style skill. Each rule has a short
name so it can be selected with --rules. Exits 0 unless --strict is given and
there are hits.

Only prose paragraphs are checked: headings, tables, lists of references,
images, fenced divs, YAML and HTML comments are skipped. Citation keys and
cross-references are removed before matching, so they cannot trigger a rule.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# Abstract nouns acting as agents ("the choice has consequences").
AGENT_NOUNS = r"(?:choice|decision|evidence|data|literature|framework|instrument|record|figure)s?"
AGENT_VERBS = (r"(?:has consequences|have consequences|does to|do to|wants?|tells?|speaks?|leaves?|"
               r"decides?|knows?|believes?|cares?|chooses?|thinks?|feels?|asks? for|demands?|"
               r"reveals?|insists?|argues?|admits?|hides?)")

BLOCK = [
    "interestingly", "notably", "importantly", "crucially", "significantly,", "remarkably",
    "it is worth noting", "it bears mentioning", "clearly", "it is clear that", "in order to",
    "leverage", "utilise", "utilize", "holistic", "going forward", "moving forward", "best practice",
    "world class", "transformational", "stakeholder", "underscores", "belies", "testament to",
    "at its core", "at heart", "throughline", "in lockstep", "delve", "navigate the", "landscape of",
    "realm", "illuminate", "load-bearing", "a masterclass", "a study in", "moreover", "furthermore",
    "perhaps unsurprisingly", "what emerges", "the real story",
]
AMERICAN = re.compile(r"\b\w+(?:iz(?:e|es|ed|ing|ation|ations)|yz(?:e|es|ed|ing))\b", re.I)
AMERICAN_OK = {"size", "sizes", "sized", "sizing", "prize", "prizes", "seize", "seized", "seizes",
               "seizing", "capsize", "citizen", "citizens", "bronze", "downsizing", "humanyze"}
# Quoted words and titles keep their own spelling: skip text inside single quotes or italics.
QUOTED = re.compile(r"'[^']{0,200}'|\*[^*]{0,200}\*")

RULES = {
    "agent": (re.compile(rf"\b(?:the|this|that|these|each|every|its|their) {AGENT_NOUNS} {AGENT_VERBS}\b", re.I),
              "abstract noun acting as an agent; say who acts ('where people work has consequences')"),
    "agent2": (re.compile(rf"\b(?:the|this|that|a) (?:choice|decision)\b[^.;:]{{0,50}}?\b(?:has|have|had) consequences\b|"
                          r"\bwhat the (?:choice|decision) does\b", re.I),
               "the choice itself has no consequences; making it does ('where people work has consequences')"),
    "matters": (re.compile(r"\b(?:it|this|that|which|what) matters?\b|\bmatters (?:here|again|most)\b", re.I),
                "'matters' as a hand-wave; say the specific consequence"),
    "notxy": (re.compile(r"\b(?:is|are|was|were) not [^.;:]{1,60}?(?:, but |; it is |\. It is |, it is )", re.I),
              "'not X, but Y' pendulum; state the positive claim on its own"),
    "cleft": (re.compile(r"(?:^|(?<=[.;:] ))What [^.]{3,80}? (?:is|are|was|were) (?:that|why|how|whether)\b"),
              "pseudo-cleft ('What the part cannot show is...'); say it directly"),
    "vague": (re.compile(r"\b(?:one or two|a few|several|various|some) (?:firms|studies|sources|countries|organisations)\b", re.I),
              "vague count; give the number if the data have it"),
    "tilde": (re.compile(r"(?<![\w/])~\s?\d"), "use '≈' for 'approximately'"),
    "emdash": (re.compile(r"—"), "em dash in prose; use a comma, colon, semicolon or brackets"),
    "dquote": (re.compile(r"(?<![=\w])\"[^\"]{2,80}\""), "double quotation marks; use single quotes"),
}


def strip_markup(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"\[\[.*?\]\]", "", text, flags=re.S)                # author comments
    text = re.sub(r"\{[#.][^}]*\}", "", text)                           # pandoc attributes
    text = re.sub(r"\[-?@[^\]]*\]", "[cite]", text)                      # bracketed citations
    text = re.sub(r"-?@(?:sec|fig|tbl|eq):[\w-]+", "§", text)            # cross-references
    text = re.sub(r"@[\w:-]+", "Author", text)                          # narrative citations
    text = re.sub(r"`[^`]*`", "code", text)
    return text


def prose_paragraphs(lines):
    """Yield (first line, last line, text) for each prose paragraph."""
    in_yaml, in_div, buf, start = False, 0, [], None
    for n, line in enumerate(lines, 1):
        st = line.strip()
        if n == 1 and st == "---":
            in_yaml = True
            continue
        if in_yaml:
            in_yaml = st not in ("---", "...")
            continue
        if st.startswith(":::"):
            in_div += -1 if st == ":::" else 1
            continue
        skip = (not st or st.startswith(("#", "|", "![", "<!--", "Table:", "[^", "    _")) or in_div > 0
                and st.startswith("|") or re.match(r"^\s*(\d+\.|[-*])\s", line))
        if not st or skip:
            if buf:
                yield start, n - 1, " ".join(buf)
                buf = []
            continue
        if not buf:
            start = n
        buf.append(st)
    if buf:
        yield start, len(lines), " ".join(buf)


def changed_lines(path, ref):
    out = subprocess.run(["git", "diff", "-U0", ref, "--", path], capture_output=True, text=True,
                         encoding="utf-8").stdout
    keep = set()
    for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", out, re.M):
        a, b = int(m.group(1)), int(m.group(2) or 1)
        keep.update(range(a, a + b))
    return keep


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z@§\[(])", text) if s]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--since", help="only check paragraphs changed since this git ref")
    ap.add_argument("--rules", help="comma-separated subset of: " + ", ".join(list(RULES) + ["opener", "block", "spelling"]))
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything is flagged")
    a = ap.parse_args()
    wanted = set(a.rules.split(",")) if a.rules else None
    lines = Path(a.path).read_text(encoding="utf-8").split("\n")
    changed = changed_lines(a.path, a.since) if a.since else None
    hits = []

    def flag(rule, n, msg, excerpt):
        if wanted is None or rule in wanted:
            hits.append((n, rule, msg, excerpt.strip()))

    for n, end, raw in prose_paragraphs(lines):
        if changed is not None and not (changed & set(range(n, end + 1))):
            continue
        text = strip_markup(raw)
        sents = sentences(text)
        # A short, punchy first sentence that opens a paragraph of several sentences.
        if len(sents) > 2 and len(sents[0].split()) < 10 and not sents[0].startswith(("Author", "§", "[cite]")):
            flag("opener", n, "short opening sentence; fold the point into a sentence that carries content", sents[0])
        for rule, (rx, msg) in RULES.items():
            for m in rx.finditer(text):
                flag(rule, n, msg, text[max(0, m.start() - 40): m.end() + 40])
        low = text.lower()
        for w in BLOCK:
            for m in re.finditer(rf"\b{re.escape(w)}", low):
                flag("block", n, f"blocklist: '{w}'", text[max(0, m.start() - 40): m.end() + 40])
        for m in AMERICAN.finditer(QUOTED.sub("", text)):
            if m.group(0).lower() not in AMERICAN_OK:
                flag("spelling", n, "American spelling? (-ize/-yze)", m.group(0))

    for n, rule, msg, ex in sorted(hits):
        print(f"{a.path}:{n}: [{rule}] {msg}\n    … {ex} …")
    counts = {}
    for _, rule, _, _ in hits:
        counts[rule] = counts.get(rule, 0) + 1
    print(f"\n{len(hits)} flags" + (": " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) if hits else ""))
    sys.exit(1 if a.strict and hits else 0)


if __name__ == "__main__":
    main()
