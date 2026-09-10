# Tino Lunch Special

A verified lunch-special master list for Cupertino and its 10-15 mile ring, plus a verified transit plan for **Tuesday, September 8, 2026**.

**Site layout (updated 2026-09-10):** the front page (`index.html`) is the **lunch deals** - verified specials at the very top, then the full searchable table. The public-transit route plan lives on its own subpage, [`transit.html`](transit.html) - the trip-planning system itself was left untouched by this change.

* **Home:** 21st Ave & Judah St, San Francisco, CA
* **Destination:** 20387 Gillick Way, Cupertino, CA 95014
* **Required chain:** SF Muni **N Judah** → **Caltrain** (22nd St) → Caltrain to **Sunnyvale or Mountain View** → **VTA** to Cupertino
* **Return:** home by 3:30 PM, target 2:30–3:00 PM to absorb rush-hour delay

Live site: https://buffedlizard55-lab.github.io/TinoLunchSpecial/

## The answer, in four lines

| | |
|---|---|
| **Leave home** | **5:10 AM** - walk 2 min to Judah & 19th Ave, N Judah **Bus** 5:15 AM (the subway does not run yet at that hour) |
| **At the door in Cupertino** | **about 7:55 AM** - Caltrain express 6:20 AM from the SF terminal (6:24 AM from 22nd St) to Sunnyvale 7:09 AM, VTA 55 at 7:19 AM to Stevens Creek & De Anza, 18 min walk |
| **Lunch window** | 11:15 AM - 12:10 PM near Cupertino (**leave the house at 11:50 AM** for the 2:40 PM arrival; the 12:20 PM departure stretches lunch to ~12:40 PM and gets you home 3:18 PM) |
| **Cost** | **$27.20** round trip with Clipper/contactless (adult; includes the $0.50 Caltrain-to-Muni credit), $27.70 without the credit, $28.00 all cash |

Every number above is a row in `data/` with the agency page it was read from.

## What is here

```
index.html                  the lunch site front page - deals on top, full table, flags, method (no build step, works from file://)
transit.html                the public-transit trip plan subpage (outbound / return / fares / flags / sources / method)
assets/styles.css           system fonts, responsive layout, print stylesheet
assets/app.js               renders data/generated.js into the panels each page contains
data/*.json                 the source of truth - edit these, not generated.js
data/generated.js           the compiled bundle the browser loads (window.TINO_DATA)
data/summary.md             the same tables in plain markdown, easiest to read on GitHub
data/plan.json              trip definition, constraints, decision log
data/transit_outbound.json  3 outbound plans, leg by leg, with per-leg links
data/transit_return.json    3 return plans + the last-workable-train cutoff
data/fares.json             agency fare tables and six day-total scenarios
data/lunch_specials.json    523 lunch entries (27 original + 20 batch-2 + 54 batch-3 + 49 batch-4 + 101 batch-5 + 1 review-pass + 100 batch-6/7 on 2026-09-07 + 103 batch-8 on 2026-09-08 + 68 batch-9 on 2026-09-10), hours, days, prices, verification level
data/lunch_rejected.json    118 rejected/deferred candidates, each with a reason and a link
data/flags.json             39 irregularities found while verifying - all still listed
data/sources.json           73 source pages, what each one proved, and the fetch status
docs/VERIFICATION.md        how to re-check every row, and what could not be verified
docs/REVIEW_2026-09-10.md   current QA pass (the ninth lunch pass + the site split), validation results
docs/REVIEW_2026-09-08.md   the eighth pass' QA record
scripts/build_data.py       validates + rebuilds generated.js and summary.md
scripts/check_links.py      every row must link to a citable https page
scripts/merge_incoming.py   merges researched batches in data/incoming/*.json into the master list
scripts/smoke_test.js       renders every panel headlessly, fails on undefined/NaN
.github/workflows/ci.yml    validates data + runs the link check and smoke test on every push
.github/workflows/pages.yml deploys the static site (index.html + transit.html + assets + data) to GitHub Pages
```

## Rebuild and check

```bash
python3 scripts/build_data.py     # validates, writes data/generated.js + data/summary.md
python3 scripts/check_links.py    # every row has a citable HTTPS source link on an allowed host
node scripts/smoke_test.js        # the site renders without throwing
python3 -m http.server 8000       # preview at http://127.0.0.1:8000
```

`build_data.py` exits 1 if a time is not `HH:MM AM/PM`, a fare total does not add up, a lunch row has no source link, a price is implausible, or a stated distance disagrees with the coordinates. That is why the tables can be trusted line by line: the checks run on every commit.

## Verification policy used here

1. **Transit:** times, stops and fares come only from `sfmta.com`, `caltrain.com` and `vta.org`. Third-party trip planners and blog posts were not used for any transit number. Walk distances use OpenStreetMap routing and are labelled as estimates.
2. **Lunch:** a price is only printed if it appears on the restaurant's own website or published menu; hours may come from Yelp/Google/TripAdvisor. Anything seen only on a menu aggregator or delivery app is recorded as a lead and flagged, never presented as verified.
3. **Absence is a result.** "No lunch special published" and "closed on Tuesdays" are rows of their own, so a gap in the data is visible instead of silently dropped.
4. **Conflicts stay visible.** Where two sources disagree (Muni headway text vs timetable, OSM hours vs the restaurant's own site) both values are shown and the choice is explained in `data/flags.json`.
5. **Nothing was backfilled by hand.** The first search pass ran 28 queries over 51 candidates; 27 survived into the master list and the rest were rejected, each with a reason and a link. Later passes added 496 more rows the same way (the seventh pass added 100, the eighth 103 - each searched and verified line by line before adding - and the ninth pass on 2026-09-10 searched ~100 new candidates Cupertino-first, then a 10-15 mile ring that now also covers Fremont, Newark, Union City, San Mateo, Redwood City, San Carlos and Foster City: 68 rows survived, 30 candidates were rejected or deferred with links, ~341 hits were deduped against the master list, four were confirmed closed (Pot Sticker King, Su Zhe Eatery, La Strada, China Delight), one new entry superseded its own earlier deferral twice over via `supersedes_rejection`, and a would-be duplicate (The Diner of Los Gatos) was caught by the address check); the master list is now 523 rows with 118 rejects in `data/lunch_rejected.json`. See `docs/REVIEW_2026-09-10.md`.

GitHub Pages is enabled at https://buffedlizard55-lab.github.io/TinoLunchSpecial/. The repo also includes `.github/workflows/pages.yml` for Action-based deployment if the Pages source is switched from `main /` to **GitHub Actions** later.

## Flagged irregularities (39)

Fourteen transit, twenty-five lunch. Headlines:

* **N Judah does not stop at 22nd St Caltrain.** The metro line ends at King St & 4th St; Caltrain's own station page lists "Muni N-Judah" there. Plans board at the terminal and still publish the 22nd St times in the same rows for reference (same Zone 1 fare).
* **SFMTA's own pages disagree** about the pre-6:15 AM N Bus frequency: the route page says every 60 minutes, the timetable says every 15. The timetable (with the date `20260908`) was used, and both readings still make the 6:20 train.
* **The Caltrain weekday PDF could not be downloaded** from the build environment, so minute-level times were read from Caltrain's live per-station tables; the holiday/weekend PDFs were checked and do not cover Sept 8.
* **The VTA stop closest to the destination** (`Stevens Creek & De Anza`) is 1.4 km / 18 min on foot - there is no closer stop, and the 7:26 AM school-only trip is not usable.
* **Nine lunch entries remain unverified leads** and many more are listing/review-level only; the lunch front page keeps those rows visible instead of promoting them to verified specials.
* **Pass-9 additions (2026-09-10, LUNCH-FLAG-21..25):** Sankranti's Sunnyvale address shows up under the name "Bombay to Goa" in 2026 listings while 2023/2025 sources still price its lunch buffet - the row stays `conflicting` with no asserted price; four new businesses are **closed on Tuesdays** (Sala Thai Fremont, No 5 House San Mateo, Takahashi Market, plus Rin-Tei's Tuesday-closed block) and four more have disputed Tuesday lunch (Hula Plate's own site vs Yelp, Restaurant Silla's three different hours blocks, Willow Street Pizza's contradictory own pages, and the tiny Urban Kitchen entry); "Saratoga lunch special" searches keep returning Saratoga Springs NY - those were rejected with the proving links; and reviewer-quoted prices ($1 tacos, $14.99 rolls, $9.99/$14.99 Early Dine) are kept in flags, never in the price column.

Full text of every flag, with the link to re-check it, is in `data/flags.json` - lunch flags on the front page, transit flags on the transit subpage.
