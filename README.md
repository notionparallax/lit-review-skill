# lit-review: a Claude Code skill for literature reviews

This skill takes you from the germ of an idea to a resolved, referenced literature review, one stage at a time. Each stage ends with a decision you make and a file that records it, so you can stop after any stage and pick up later.

| Stage | What happens |
|---|---|
| 0. Tools | Installs and checks Python, git, pandoc, Zotero and Better BibTeX |
| 1. Scope and budget | How much of your time, how many words, for which reader |
| 2. Question | The question, its edges, what you expect to find, and the kind of review |
| 3. Search plan | Concepts, search strings, sources for your field, inclusion rules |
| 4. Search and screen | Logged searches; you spot-check the screening and fetch PDFs |
| 5. Read and record | Notes on what each source found, how well it is known, and who funded it |
| 6. Argument and outline | The argument in three paragraphs, then sections with word budgets |
| 7. Draft | Written section by section, cited from Zotero |
| 8. Comment and critique | Your comments answered; an independent sceptical read |
| 9. Check and build | Claims spot-checked against sources; Word and HTML built |

It works at three sizes: a **scan** (an afternoon or two of your time), a **briefing** (a few days), or a **full review** (weeks). A track for reviews aimed at peer review is outlined but not yet built.

## Install

You need [Claude Code](https://claude.com/claude-code). The skill installs everything else it needs, with your permission, in stage 0.

In Claude Code:

```
/plugin marketplace add <URL or local path of this repository>
/plugin install lit-review@lit-review
```

Or copy `skills/lit-review` into `~/.claude/skills/`.

## Use

Open Claude Code in an empty folder and say something like 'I'd like to do a literature review on how acoustic privacy affects focus work in open-plan offices'. To continue later, open Claude Code in the review's folder and say 'carry on with the lit review'.

## What's in here

- `skills/lit-review/SKILL.md`: the overview Claude reads first.
- `skills/lit-review/references/`: one file per stage, plus verification rules, writing rules and a guide to choosing methods.
- `skills/lit-review/scripts/`: helpers for setting up a review folder, searching OpenAlex, talking to Zotero, building the review and checking style. Standard-library Python only.
- `skills/lit-review/assets/`: templates for each stage's file, and the APA 7 citation style (CSL, CC BY-SA 3.0).
