# Stage 3: The search plan

**Purpose.** Decide, before searching, where to look, with what words, and what counts as relevant. Writing this down first means the search can be repeated and its gaps can be stated. It also stops the review being shaped by whatever turned up first.

**Output.** `03_protocol.md`, and `search/strings.json`.

## Steps

1. **Concepts.** From the sub-questions, list the concepts to search (usually one per sub-question). For each, list the words the literature uses for it, including other fields' vocabulary and spelling variants. Practitioners' terms often differ from researchers' ("hot-desking" against "non-territorial office" or "activity-based working"); ask the person what words they use, and add the academic ones.
2. **Strings.** Write one boolean string per concept, in OpenAlex syntax (`("a" OR "b") AND (c OR d)`; quote phrases). Keep them readable; the person should be able to see what each searches for. Save them to `search/strings.json` as `{"S1_name": "string", ...}`.
3. **Test the strings against the seed papers** (briefing and full tiers). Run each string with `openalex_search.py --test-seeds` (see the script's help), and report which seed papers each string finds. A string that misses most of its seeds is using the wrong vocabulary; revise and retest, logging each version. Seeds that no string finds are usually old, books, or in another field's language: note them, because citation chasing will need to reach that kind of work.
4. **Sources.** Default: OpenAlex (broad, open and repeatable; journals, conference papers, preprints, working papers), plus targeted web searches for grey literature, plus one round of following references from the key papers. Then add the sources the field relies on (table below). Ask the person what they and their colleagues read; practitioners often know the field's real venues better than any database does.
5. **Limits.** Language, date range, document types.
6. **Inclusion and exclusion rules.** Three to five short rules each, written so that someone else would make the same call on a borderline record. Give each exclusion a code (E1, E2, ...) so that screening decisions can cite them.
7. **Screening plan.** How many records per string to screen (usually the top 50 to 200 by relevance; more at full tier), and how the person checks your screening (see stage 4).

## Sources by field

The skill works for any subject, but fields differ in where their evidence lives and how well OpenAlex covers it. Pick from this table, and say in the protocol why each source was chosen. Sources marked (library) need institutional access; if the person doesn't have it, say what is lost and lean harder on citation chasing.

| Field | Add to OpenAlex | Notes |
|---|---|---|
| Health, medicine, nursing, public health | PubMed (free; search via its E-utilities or web form), Cochrane Library, CINAHL (library) | Strong on trials and systematic reviews; check for an existing review first |
| Psychology, behaviour | PsycINFO (library), PubMed | Many validated scales; record the instrument used |
| Engineering, computing, building science | Semantic Scholar, IEEE Xplore, ACM Digital Library | Conference papers carry much of the evidence |
| Architecture, urban design, landscape | Avery Index (library), CumInCAD (computational design), Trove (Australian), practice and award publications | Much knowledge sits in books, case studies and practice reports; expect heavy citation chasing and grey literature |
| Economics, business, management | NBER, SSRN, RePEc / IDEAS | Working papers circulate for years before publication; record the version read |
| Education, social policy | ERIC, Analysis & Policy Observatory (APO, Australian and NZ grey literature) | Government evaluations are often the main evidence |
| Law and regulation | AustLII, BAILII, legislation and parliament sites, regulator guidance | Primary sources first; date everything ('as at') |
| History, humanities, theory | Library catalogues, JSTOR (library), Trove, archives | Books dominate and databases find them poorly; follow references and use seed works |
| Environment, sustainability | Scopus or Web of Science (library), agency and NGO reports | Large grey literature; note interests |

Database coverage is weakest for books, older work (before ≈1990), non-English work and grey literature. Name these limits in the protocol, and use seed papers and reference chasing to reach them. Where a database has no API the scripts can use, run the search in its web interface, copy the exact query and count into the log, and export the results (RIS or CSV) for Zotero and screening.

## By tier

- **Scan.** A short plan: three to six strings, no seed test unless it's quick, inclusion rules in a few lines. Still write it down and log it.
- **Briefing.** Everything above, with the seed test.
- **Full.** Everything above, plus a stopping rule, a second database, and a plan for screening reliability (see [publishable-track.md](publishable-track.md)).

## Gate

The person agrees the plan, including the strings. After this, changes to strings or rules are allowed but are logged with the date and reason in `03_protocol.md`, so the record shows what was planned and what changed. Update `STATUS.md` and commit.
