# Stage 0: Tools

**Purpose.** Get the person's machine ready, assuming nothing is installed. They are technical enough to use a terminal and git, but may not have used Zotero or pandoc. Do this at the very start, so that nothing breaks halfway through stage 4. Checking takes a minute; installing everything from scratch takes ≈20 to 40 minutes, most of it downloads.

**Output.** A working setup, checked; a line in `STATUS.md`.

## 1. Check what's there

Stage 1 can run while installs finish, but check first. `new_review.py` needs only Python and git; if Python is missing, install it before anything else.

```sh
python --version
git --version
pandoc --version
python -I <skill>/scripts/build_review.py --check-tools
```

`--check-tools` reports Python, git, pandoc, the git identity, and Zotero: running, or installed but closed, or not installed (it looks for the app and for Better BibTeX in the Zotero profile). It exits with 1 if anything needs attention. Don't offer to install Zotero or Better BibTeX if it reports them installed; ask the person to start Zotero instead.

## 2. Install what's missing

Explain each item in a line (what it is for in this review), then run the command for their platform with their permission. Some steps need them to click through an installer or app; tell them exactly what to click, and wait for them to confirm.

| Tool | What it's for | Windows | macOS |
|---|---|---|---|
| Python 3.10+ | Runs the skill's scripts (standard library only, no packages) | `winget install Python.Python.3.12` | `brew install python` |
| git | Saves each stage; shows changes as diffs | `winget install Git.Git` | `xcode-select --install` or `brew install git` |
| pandoc | Turns `review.md` into Word and HTML with formatted references | `winget install JohnMacFarlane.Pandoc` | `brew install pandoc` |
| Zotero (desktop) | Reference library: holds every source, its PDF, and its citation key | `winget install DigitalScholar.Zotero` | `brew install --cask zotero` |
| Better BibTeX | Zotero plugin that gives each item a stable citation key and serves the library to the scripts | See below | See below |
| Zotero Connector | Browser extension: saves web pages, reports and papers to Zotero in one click | zotero.org/download | zotero.org/download |

On Linux, use the distribution's package manager, and Zotero's tarball from zotero.org.

If `winget` or `brew` isn't available, give them the download page instead (python.org, git-scm.com, pandoc.org/installing.html, zotero.org/download). Open a new terminal after installing, so the new commands are on the PATH.

**git identity.** If `git config user.name` is empty, ask them to set their name and email themselves (`git config --global user.name "..."`, `git config --global user.email "..."`). Don't fill these in for them.

**Better BibTeX.** Download the latest `.xpi` from the releases page (github.com/retorquere/zotero-better-bibtex/releases) into their Downloads folder. Then they: open Zotero → Tools → Plugins (called Add-ons in some versions) → gear icon → Install Plugin From File → choose the `.xpi` → restart Zotero. If the menus differ in their version, check the install page linked from the releases page. Keep the default citation key format; don't change it once the review has started, or keys in the text will break.

## 3. Set Zotero up for the review (just before stage 4)

This can wait until the search starts. Talk them through these in Zotero:

1. **A collection for this review** (File → New Collection), named for the topic. Select it before you add items: the scripts add to whichever collection is selected.
2. **PDF access.** If their organisation or a university gives them library access, set up the library proxy (Settings → General → 'Use library proxy', or follow the library's Zotero instructions), so Zotero can fetch PDFs behind paywalls. 'Find Available PDF' (right-click an item) gets open-access copies.
3. **Sync** (optional): a free Zotero account backs up the library and lets them use it on other machines. PDF storage beyond 300 MB is paid; most briefings fit.

## 4. Optional

- **OpenAlex API key.** Searches work without one. A free key (openalex.org) raises the rate limit; set it as the environment variable `OPENALEX_API_KEY`.
- **A Word template.** To build in their organisation's Word styles, save a `reference.docx` with those styles into a `templates/` folder in the review folder (create it); the build uses it automatically.

## 5. Gate

Stage 0 has no file of its own. Record the result on the **Tools** line of `STATUS.md` (installed, and anything pending, such as Zotero to start, the collection to make, or a library proxy waiting on IT), and commit it with stage 1's gate. Stage 0 is done when Python, git and pandoc work and Zotero with Better BibTeX is installed; the in-app setup in §3 is finished just before stage 4, when `zotero.py status` should report Zotero running with the review's collection selected.

If something can't be installed (a locked-down machine), stages 1 to 3 still work. Say plainly what won't work without it: without Zotero, keys can't be checked and references can't be built, so don't start drafting until it is in place.
