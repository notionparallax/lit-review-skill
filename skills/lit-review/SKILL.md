---
name: lit-review
description: Guides someone, step by step, from the germ of a research idea to a well-resolved literature review, with searches logged, sources checked against what they actually say, references managed in Zotero, and the review built to Word and HTML. Use this skill whenever someone wants to start, plan, scope, continue or finish a literature review, evidence review, state-of-knowledge briefing or "what does the research say about X" piece of writing, even if they don't call it a literature review. Also use it when a folder contains a STATUS.md written by this skill, or when someone asks to "pick up the review", "carry on with the lit review" or "what's the next step in the review".
---

# Literature review, from germ to finished draft

This skill takes a person from a half-formed idea ("I wonder what the research says about hot-desking and wellbeing") to a resolved, referenced literature review. It does this in stages. Each stage ends with a decision the person makes and a file that records it, so the work can stop and restart across many sessions without losing the thread.

The people using it are practitioners (architects, designers, researchers in a practice), not necessarily trained academics. They are technical and comfortable in a terminal, but may never have installed Zotero or pandoc, or chosen a review method. They are capable and busy. The topic can be anything; where fields differ (where their evidence is published, which databases cover them, which study designs dominate), the stage references say how to adapt. Treat them as the author and the decision-maker: you do the searching, reading, checking and drafting; they decide what the review is for, what it argues and what goes in. Explain what each stage is for in plain words, the first time it comes up.

## The stages

| # | Stage | What gets decided | File | Reference |
|---|---|---|---|---|
| 0 | Tools | Install and check Python, git, pandoc, Zotero, Better BibTeX | (`STATUS.md`) | [stage-0-setup.md](references/stage-0-setup.md) |
| 1 | Scope and budget | Time available, words wanted, reader, size tier | `01_scope.md` | [stage-1-scope.md](references/stage-1-scope.md) |
| 2 | Question | The question, what is in and out, what they already believe, seed papers, the kind of review | `02_question.md` | [stage-2-question.md](references/stage-2-question.md) |
| 3 | Search plan | Concepts, search strings, sources, inclusion rules | `03_protocol.md` | [stage-3-protocol.md](references/stage-3-protocol.md) |
| 4 | Search and screen | What is kept; which PDFs the person fetches | `04_search_log.md`, `search/`, `pdfs_needed.md` | [stage-4-search.md](references/stage-4-search.md) |
| 5 | Read and record | What each source found, how well it is known, who funded it | `05_sources.md` | [stage-5-read.md](references/stage-5-read.md) |
| 6 | Argument and outline | The spine (the argument in three paragraphs) and a section plan with word budgets | `06_outline.md` | [stage-6-outline.md](references/stage-6-outline.md) |
| 7 | Draft | Prose, section by section, cited by key | `review.md` | [stage-7-draft.md](references/stage-7-draft.md) |
| 8 | Comment and critique | The person's comments answered; a sceptical outside read | `07_comments_log.md` | [stage-8-review.md](references/stage-8-review.md) |
| 9 | Check and build | Citations resolve, statuses clean, Word and HTML built | `08_checks.md`, `review.docx` | [stage-9-finish.md](references/stage-9-finish.md) |

Read the reference file for a stage when you start that stage, not before; each one says what to do, what to ask and what the stage's file should contain. [verification.md](references/verification.md) (source statuses and interest) and [writing.md](references/writing.md) (prose rules) apply throughout, so read them before stage 5 and stage 7 respectively. [methods.md](references/methods.md) covers the two method choices a review involves: what kind of review to do (stage 2), and the research designs in the literature and for the work that follows (stages 5, 6 and 9). [publishable-track.md](references/publishable-track.md) describes extra stages for a review meant for peer review; that track is not built out yet.

Not every review needs every stage at full weight. Stage 1 sets a size tier (scan, briefing or full), and each stage reference says what to do at each tier. A scan might take an afternoon of the person's time; a full review takes weeks. The order of stages stays the same at every tier, because the order is where most of the value is (see "Lessons" below).

## Starting and resuming

**First, look for `STATUS.md`** in the working directory (and one level down). If it exists, read it, tell the person where they are in a sentence or two ("We're in stage 5, reading. 23 of 41 sources have notes; the next batch is the office-design papers."), and carry on from the next action it lists. Read the current stage's reference file before acting.

**If there is no `STATUS.md`**, this is a new review. Before your first message, run the stage 0 checks (read-only; see [stage-0-setup.md](references/stage-0-setup.md)). If Python and git are present, also create the review folder straight away with a default name, so there is somewhere to record decisions:

```
python -I <this skill's directory>/scripts/new_review.py <topic-slug> --title "<working title>"
```

It creates the folder, the stage files from templates, `STATUS.md`, and a git repository with a first commit. Use a short slug from their idea (`biophilic-workplace-review`) in the current directory; the person can rename it.

Then send **one first message** that covers, briefly:

1. A welcome and the shape of the process: about nine stages, each ending in a decision they make and a file that records it; they can stop after any stage and pick up later by asking to continue the review.
2. The tool report: what is installed, what is missing, and an offer to install what's missing (with their permission). Zotero setup inside the app (a collection, library proxy) can wait until just before stage 4.
3. Where you put the review folder, and that they can rename it or retitle it.
4. Their name, for the review's author line (pass it later with `new_review.py --author` on a new review, or edit `review.md`'s front matter).
5. Stage 1's opening questions (see [stage-1-scope.md](references/stage-1-scope.md)).

If Python or git is missing, install them (with permission) before creating the folder, and leave the folder for the second message.

Longer installs (Zotero, Better BibTeX) can be finished while stages 1 to 3 go ahead, since those don't need them; they must be working before stage 4.

## How to run each stage

The person should always know where they are, what you need from them and roughly how long it will take. For each stage:

1. **Orient.** Say which stage this is (for example "Stage 3 of 9: the search plan"), what it is for in one or two sentences, what you will ask of them, and roughly how long it takes at their tier.
2. **Do the work and ask the questions.** Ask one or two decisions at a time, each with a recommendation and the reason for it. Use the AskUserQuestion tool when it is available, since it lets them pick quickly; otherwise give lettered options, with your recommendation marked. Don't re-ask what they have already told you; confirm it in a line instead ("You said a client asked, so I've assumed the reader is the client"). Never invent their answer to a question that is theirs to make: purpose, reader, scope, what they believe, what the review argues.
3. **Write the stage file** and ask them to read it. They can mark it up anywhere with comments in `[[double square brackets]]`; you answer each comment, change the file, and remove the comment once it is resolved.
4. **Close the gate.** When they agree, record the decisions in the stage file with the date (written as 26 November 2026, in every file), update `STATUS.md` (stage, decisions, next action, open questions), and commit (`git add -A && git commit -m "Stage N: <what was agreed>"`). Tell them what is next and that it is a fine place to stop.

Do not move past a gate without the person's agreement. If they want to skip a stage, say briefly what it protects against (from "Lessons" below), and then do what they decide; record the skip in `STATUS.md`.

Before any large rewrite (a style pass, restructure or round of comments), snapshot the review: `git commit` first, so the person can see your changes as a diff in their editor. Diffs are the easiest way for them to check your edits.

## Principles that hold at every stage

**Never fill a gap from memory.** Every claim about a source comes from the source itself (full text, or at least the abstract), retrieved in this project. Figures remembered from training, or quoted in press coverage of a paper, are not used; if the source can't be read, either say only what the abstract supports, or leave it out. This is the rule that makes the review trustworthy. A fluent review with invented findings or keys is worse than no review, because it is believed. See [verification.md](references/verification.md).

**Every source has a status.** VERIFIED, PARTIAL, GREY or UNVERIFIED, recorded in `05_sources.md` from the moment the source is first noted. UNVERIFIED sources are not cited.

**Zotero is the source of truth for references.** Citation keys come from Better BibTeX and are copied, never typed from memory or invented. Cite in pandoc syntax (`@key`, `[@key]`) from the first sentence of the draft.

**Log as you go.** Every search (exact string, engine, date, count, what was kept) goes in `04_search_log.md` when it is run. A review whose searches were not logged cannot show what it might have missed.

**The person's words are theirs.** When they rewrite something you drafted, treat their version as deliberate. Fix only a specific fault in it (grammar, an unclear referent, a claim stronger than the evidence) and show what you changed. Never quietly restore your earlier wording.

**Look for evidence against.** Stage 2 records what the person already believes. Search deliberately for studies that would contradict it, and give them space in the review.

**Findings go into the work, not into reports.** When a check turns something up, fix it in the relevant file, or leave a `[[comment]]` at the spot where the person has to decide. Don't produce separate findings documents they have to cross-reference.

**Be honest in reporting back.** At the end of each working session, say what changed, what is still unverified or unread, and what you could not do (a paywalled PDF, a page that wouldn't load). Never describe a section as checked when it rests on search snippets.

## Lessons from the review this skill came from

This skill was distilled from a long review in which several steps were done late and had to be repaired. The stage order above puts them where they belong.

- **The search was logged after the fact.** Early searches went unrecorded, so coverage could only be checked by running a structured search weeks later. Log from the first query.
- **The argument came after the prose.** About a dozen drafts were written before the spine was agreed, and the restructure cost more than the drafting. Agree the spine (stage 6) before writing paragraphs.
- **Citations and statuses were retrofitted.** Converting plain-text citations to keys, and tracing how each claim was known, took several passes. Do both from the start.
- **Style rules arrived as a cleanup pass.** Load the writing rules before drafting, not after.
- **Named studies without findings.** Drafts repeatedly named a study ("Smith et al. also studied this") without saying what it found. Every named study states its design and finding.
- **Remembered figures were wrong.** Several widely quoted statistics turned out not to be in the source they were attributed to. Check the number against the page.
- **Vendor data looked like evidence.** Much of the data in practice-facing fields comes from firms that sell into the market. Note who produced each source and what they sell, at first citation.

## Files at a glance

```
<review folder>/
  STATUS.md             where we are, decisions so far, next action
  01_scope.md ... 08_checks.md   one file per stage (see table)
  search/               strings, query logs and screened records (CSV)
  pdfs_needed.md        PDFs for the person to fetch into Zotero
  review.md             the review itself (pandoc markdown)
  refs.json             generated by the build from Zotero; don't edit
  review.docx, review.html   generated by the build
```

## Scripts

All in `scripts/` in this skill's directory. Run them with `python -I`.

- `new_review.py <folder>`: create a new review folder from the templates.
- `openalex_search.py`: run logged searches in OpenAlex and write screenable records (stage 4).
- `zotero.py`: check Zotero is running, find keys, export the library, add records by DOI through the Zotero connector (stages 4, 5, 7).
- `build_review.py`: pull cited references from Zotero, check every citation resolves and has a status, lint, and build Word and HTML (stages 7 and 9).
- `style_check.py`: advisory check for prose patterns in [writing.md](references/writing.md) (stages 7 to 9).

Each prints `--help`.
