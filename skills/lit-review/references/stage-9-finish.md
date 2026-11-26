# Stage 9: Check and build

**Purpose.** Make sure the finished review says only what its sources support, every citation resolves, and the Word and HTML builds are clean.

**Output.** `08_checks.md`; final `review.docx` and `review.html`.

## Checks

Record each in `08_checks.md` with the date and result. Fix problems in `review.md` directly, or leave a `[[comment]]` where the person must decide.

1. **Build clean.** `build_review.py review.md` reports no unresolved keys, no cited source without a status, and no UNVERIFIED source cited.
2. **Spot-check claims against sources.** Take a random sample of citing sentences (10 at scan tier, 20 at briefing, more at full; use a fixed seed and record it). For each, split it into claims, find the supporting passage in the source's full text, and give a verdict: supported, loose, not found, or contradicted. Record the passage and page. Fix every problem found, and if more than one in ten is wrong, widen the check to the whole section where the errors cluster. A known small error rate is worth stating; an unknown one isn't.
3. **PARTIAL sources.** List every PARTIAL source the review relies on and what claim it supports. For each, either get the full text, soften the claim to what the abstract supports, or accept it and say so in the method paragraph.
4. **Time-sensitive claims** carry the 'as at' date; pending items are labelled pending.
5. **References.** Every reference in the built list is cited and vice versa (the build guarantees this when citing by key). Spot-check five entries in the built reference list against their Zotero records for obvious metadata errors (wrong year, missing journal, title in capitals).
6. **Style.** Run `style_check.py review.md` over the whole document and work through the flags.
7. **Method paragraph.** Make sure the review says, briefly and accurately: what type of review it is (citing the methodological source from [methods.md](methods.md)) and that it did what that type promises; where and when sources were searched, how many were screened and included, how claims were checked, what tools were used (including AI, and for what), and the limits (language, what wasn't read in full).

## Hand over

Tell the person:

- where `review.docx` and `review.html` are;
- what was checked, what the spot-check found, and what is still PARTIAL;
- the open `[[comments]]`, if any;
- the gap list, if they plan further work.

Update `STATUS.md` to "complete", with the date, and commit. If they want to take the review further toward publication, point them to [publishable-track.md](publishable-track.md).
