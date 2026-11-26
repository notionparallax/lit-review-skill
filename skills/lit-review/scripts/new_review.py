"""Create a new literature review folder from the skill's templates.

    python -I new_review.py <folder> --title "Working title" [--author "Name"]

Creates the folder (it must not exist, or be empty), copies the stage files,
STATUS.md, review.md and the APA style, and makes a git repository with a
first commit. Prints what it made.
"""
import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL / "assets" / "templates"


def git(folder: Path, *args: str) -> bool:
    try:
        r = subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True)
    except FileNotFoundError:
        return False
    return r.returncode == 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", default="")
    ap.add_argument("--no-git", action="store_true", help="don't create a git repository")
    a = ap.parse_args()

    folder = Path(a.folder).resolve()
    if folder.exists() and any(p.name != ".git" for p in folder.iterdir()):
        sys.exit(f"{folder} exists and is not empty; choose a new folder.")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "search").mkdir(exist_ok=True)
    (folder / ".csl").mkdir(exist_ok=True)
    shutil.copy(SKILL / "assets" / "apa.csl", folder / ".csl" / "apa.csl")

    today = dt.date.today()
    subs = {"{{TITLE}}": a.title.replace('"', "'"), "{{AUTHOR}}": a.author,
            "{{DATE}}": f"{today.day} {today:%B %Y}", "{{CSL}}": ".csl/apa.csl"}
    made = []
    for src in sorted(TEMPLATES.iterdir()):
        name = {"gitignore": ".gitignore", "strings.json": "search/strings.json"}.get(src.name, src.name)
        text = src.read_text(encoding="utf-8")
        for k, v in subs.items():
            text = text.replace(k, v)
        (folder / name).write_text(text, encoding="utf-8")
        made.append(name)

    committed = False
    if not a.no_git:
        if not (folder / ".git").exists():
            git(folder, "init", "-q")
        committed = git(folder, "add", "-A") and git(folder, "commit", "-q", "-m", f"Start literature review: {a.title}")

    print(f"Created {folder}")
    for m in made:
        print(f"  {m}")
    print("  .csl/apa.csl")
    print("git: " + ("first commit made" if committed else "no commit made (git missing, or user.name/email not set)"))


if __name__ == "__main__":
    main()
