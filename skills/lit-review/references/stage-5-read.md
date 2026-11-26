# Stage 5: Read and record

**Purpose.** Build a record of what each source actually found, how well that is known, and who stands behind it. The draft is only ever as good as these notes, because every sentence in it is written from them. Read [verification.md](verification.md) before starting.

**Output.** `05_sources.md`, and a short reading list for the person.

## For each source

Read the full text where you have it (PDF attached in Zotero, an open-access copy, or a working-paper version), otherwise the abstract and record. Then write an entry in `05_sources.md`:

```markdown
### @citationKey
- **Status:** VERIFIED (full text) | PARTIAL (abstract only; ...) | GREY (...) | UNVERIFIED
- **Interest:** independent | <type>: <who, what they sell or stand to gain, likely direction of bias>
- **What it is:** design (in the terms of the Part B table in methods.md), sample, setting, country, period (e.g. 'longitudinal / panel: survey, 3,200 UK office workers, 2021-2023')
- **Found:** the findings relevant to this review, with numbers and what each number is a share of; page numbers for key figures
- **Doesn't show:** what it did not measure or cannot support, in a few words
- **Use for:** sub-question(s) / theme(s)
- **Quote:** (optional) a short verbatim sentence for anything you expect to paraphrase closely, with page
```

Get the citation key from Zotero (`zotero.py find <DOI or title words>`), never by guessing its format. If the source is not in Zotero yet, add it (`zotero.py add <DOI>`) or, failing that, give it a provisional key marked `(not in Zotero)` and list it in `pdfs_needed.md` for the person to add.

Work in batches by theme (five to fifteen sources), so that sources are compared while they are fresh. After each batch, write three or four lines at the top of that theme's section in `05_sources.md`: where the studies agree, where they disagree, and what nobody has measured. These lines become the bones of the outline.

## Things to watch for while reading

- **The number is not in the paper.** Popular figures attributed to a study are often from press coverage, a different version or a different paper. Use what the paper says.
- **Self-reported against observed.** Note which a study used; surveys and sensor or log data often disagree on levels.
- **Denominators.** 'Forty per cent' of whom? Note it.
- **Versions.** Working papers change between versions and on publication. Record which version you read.
- **Disagreement between sources** on a date, an author or a figure: record both and the primary source.
- **Evidence against the person's hypotheses** (from `02_question.md`): mark it clearly; it needs to reach the draft.

## The person's reading list

From the notes, pick the papers the person should read themselves (the number agreed in stage 1), in an order that follows the argument: a few orientation papers first, then the key study for each theme. Give each a reason in one line and say whether to read, skim or dip. Put this at the top of `05_sources.md` or in its own file. A review its author hasn't read any of is hard for them to defend.

## By tier

- **Scan.** Abstract-level reading is acceptable for most sources, so most will be PARTIAL; full text for the three to five the argument rests on.
- **Briefing.** Full text for every source the argument leans on; abstract level is fine for sources cited only in passing.
- **Full.** Full text wherever it can be got, plus an extraction table (see [publishable-track.md](publishable-track.md)).

## Gate

Notes exist for every source to be cited, each with a status. The person has their reading list. Report how many sources are VERIFIED, PARTIAL and GREY, and which PDFs are still missing. Update `STATUS.md` and commit.
