# Stage 8: Comment and critique

**Purpose.** Improve the draft through the person's comments and a sceptical outside read. This is where most of the quality comes from, and where most of the person's time goes after reading.

**Output.** Revised `review.md`; `07_comments_log.md`.

## The comment cycle

1. **Commit before they comment**, so their comments and your responses both show as diffs.
2. They comment in `review.md` (or a copy, or the Word file if they prefer; read comments from it with pandoc or the docx skill), in `[[double square brackets]]` next to the words concerned. Comments can be questions, objections, or instructions.
3. **For each comment:** go back to the source (not to your notes alone, if the comment questions a fact), answer what the source actually says, change the text, and remove the comment. If they recalled a source correctly, say so; if a comment refers to a source you can't identify, ask which one they mean rather than guessing.
4. **Log each answer** in `07_comments_log.md`: the comment, what the source says, what was changed, and anything still unresolved. Number them so the person can refer to them. Add a 'For other sections' list for knock-on changes elsewhere.
5. **Their rewrites are theirs.** Where they rewrote your text, fix only specific faults and show each change; don't restore your wording.
6. Commit, and tell them the diff holds the changes.

For wording changes you propose (rather than ones they asked for), the clearest way for them to review is a diff: commit a list of the current sentences with a one-line reason for each, then replace the sentences in the working copy without committing, so their editor's diff view shows before and after.

## The outside read

At briefing and full tiers, after the first comment round, get a critique from a reader who hasn't seen the drafting. Use a fresh subagent (the Agent tool) so its read isn't anchored on yours. Give it only `review.md`, `02_question.md` and this brief:

> You are a sceptical, expert reviewer for [the reader from 01_scope.md]. Read this literature review against its stated question. Report: (1) claims whose breadth goes beyond the evidence cited; (2) studies named without a finding; (3) places where interested sources (vendors, consultancies) carry a claim without independent support; (4) evidence one would expect to see that is missing; (5) whether the conclusion follows from the body; (6) structural problems, such as repetition, sections that don't serve the argument, or terms not explained for this reader. For each, give the location and a concrete suggestion. Also score the review 0 to 2 on each SANRA item (importance, aims, search description, referencing, reasoning, data presentation), with one line of justification each.

Then go through its points with the person. Make a short list in `07_comments_log.md` of each point and the agreed response (act, decline with a reason, or defer). Don't act on the critique without that discussion; some of its points will be wrong or out of scope for the tier.

## The fragmentary-claims sweep

After each round, read the whole draft for: studies named without a finding; figures without a denominator or source; terms and acronyms not explained at first use; sentences that lost their sense in editing. Fix them.

## By tier

- **Scan.** One comment round; no outside read; the sweep.
- **Briefing.** One or two rounds, the outside read, the sweep.
- **Full.** As many rounds as it takes, the outside read, the sweep, and a style pass at the end.

## Gate

The person is satisfied with the content. Update `STATUS.md` and commit.
