# Stage 7: Draft

**Purpose.** Write the review, section by section, from the agreed outline and the source notes.

**Output.** `review.md` (pandoc markdown), built to Word and HTML.

## Before writing

- Read [writing.md](writing.md). If a `house-style` skill is available, load it too; its rules take precedence over writing.md's on matters of tone.
- Re-read the agreed spine and outline in `06_outline.md`.
- Check `review.md`'s front matter (title, author, date, `bibliography: refs.json`, `csl` path). `new_review.py` fills these in.

## Drafting

- **Draft in section groups**, two or three sections at a time, then stop and show the person. Smaller batches mean comments arrive while the material is fresh, and errors don't repeat across the whole document.
- **Write every claim from `05_sources.md`**, never from memory. If a claim needs a source you haven't recorded, go back to stage 5 for it (read it, record it, then cite it).
- **Cite by key from the first sentence:** `@smithOfficeLayout2021 found...` when the author is the subject of the sentence; `... [@smithOfficeLayout2021; @leeHybrid2023]` otherwise. Never write the name and then repeat it in brackets. Mark working papers and preprints in the citation: `[@key, working paper]`.
- **Every named study states what it found**, with design or sample where it bears on the weight of the finding.
- **GREY sources** carry their interest note in the text at first citation ("..., a survey by a desk-booking software vendor [@key]").
- **PARTIAL sources** carry claims no stronger than the abstract supports.
- **Respect the budgets.** Report the word count per section against budget after each batch.
- **Leave `[[questions]]`** in the text for the person where you hit a judgement that is theirs (a contested reading, whether to include a weak source).

## After each batch

Build the review:

```
python -I <skill>/scripts/build_review.py review.md
```

It pulls the cited references from Zotero (Zotero must be running with Better BibTeX), checks every key resolves and has a status in `05_sources.md`, warns about UNVERIFIED or missing statuses and a few mechanical style faults, builds `review.docx` and `review.html`, and prints the word count. Fix what it reports before handing over.

Then run `python -I <skill>/scripts/style_check.py review.md --since HEAD` and fix or justify each flag in the new text. It is advisory; some flags will be fine as written.

Commit, and tell the person: which sections are drafted, word counts against budget, `[[questions]]` waiting for them, sources still PARTIAL that the section leans on.

## Gate

All sections drafted and built. Move to stage 8 for comments.
