# Stage 4: Search and screen

**Purpose.** Run the planned searches, record everything, and decide which records to keep. The person's job here is small but important: spot-check your screening, and fetch the PDFs you can't reach.

**Output.** `search/records.csv` and `search/query_log.json` (from the script), `04_search_log.md` (the human-readable log), entries in Zotero, and `pdfs_needed.md`.

## 0. Zotero ready

Finish the in-app setup from [stage-0-setup.md](stage-0-setup.md) §3 (a collection for the review, library proxy), and check `zotero.py status` reports Zotero running with that collection selected.

## 1. Database search

Run the strings:

```
python -I <skill>/scripts/openalex_search.py search/strings.json --per-string 100 --from 2000 --out search/
```

The script logs every query (string, URL, date, total count) and writes one row per unique record with its abstract. If `refs.json` exists, records already in the library are marked as held. Copy the counts into `04_search_log.md` as a new pass.

## 2. Screen

Screen each record from its title and abstract against the rules in `03_protocol.md`. Record in `search/records.csv` (add columns `decision`, `code`, `reason`): `include`, `exclude` with its code, or `unsure`. Keep reasons short and specific.

For large sets, a cheaper model can make a first pass, but you (the main model) review every `include` and `unsure`, and a random 20% of the `exclude` decisions. If that sample turns up wrongly excluded records, re-screen all the exclusions.

**The person's check.** Give them a random sample (≈10%, at least 20 records) to screen blind, without your decisions, in a small markdown table. Compare, report the agreement, and talk through disagreements; they often show that a rule needs clarifying. Write clarified rules into `03_protocol.md` and apply them to all records. At scan tier, show them a list of the included titles instead and ask what looks wrong or missing.

## 3. Follow references

From the included records and the seed papers, follow references once in each direction: backward (what they cite) and forward (what cites them). OpenAlex gives both (`referenced_works`, and `cites:` filter). Screen what you find with the same rules, and log it as its own pass. This is how older work, books and other fields' vocabulary get found.

## 4. Grey literature and the web

Run targeted web searches for reports from government, industry bodies and standards organisations. Log each query exactly, with the date, the number of results scanned, and what was kept and why. Vendor and consultancy reports go in only as data, with their interest noted (see [verification.md](verification.md)).

## 5. Into Zotero

For included records with a DOI, add them to Zotero through the connector:

```
python -I <skill>/scripts/zotero.py status        # Zotero running? Which collection is selected?
python -I <skill>/scripts/zotero.py add 10.1234/abcd 10.5678/efgh --tag review-new --tag needs-pdf
```

Check the selected collection with the person first; items go into whichever collection is selected in the Zotero window. The script skips DOIs already in the library. For records without a DOI (reports, web pages, books), list them in `pdfs_needed.md` with a full reference and URL, and ask the person to add them using the Zotero browser connector, which captures web pages and reports well.

## 6. PDFs

You cannot get past paywalls. Write `pdfs_needed.md` as a short, practical list for the person: for each item, the reference, the DOI link, whether an open-access copy exists (OpenAlex `open_access.oa_url`), and its priority (the papers the argument will lean on first). Tell them to attach each PDF to its Zotero item, where you can then find it (`zotero.py` reports attachment paths). Open-access PDFs you may download yourself into the Zotero item's folder, or just read them online.

## 7. Write up the pass in `04_search_log.md`

For each pass: question, date, exact queries with engine and counts, records screened, included, excluded by code, added to Zotero, and anything that could not be done. Also note what the search did *not* find that you expected, and which seed papers it missed; that is the honest statement of coverage.

## By tier

- **Scan.** Top 30 to 50 per string; no blind sample (show the person the included list); references followed from the two or three most central papers only.
- **Briefing.** As above.
- **Full.** Larger screening depth, stopping rule, a second database, and a reported agreement figure.

## Gate

The person has checked the screening sample (or list), and knows which PDFs to fetch. Reading (stage 5) can start on open-access and already-held papers while they fetch the rest. Update `STATUS.md` and commit.
