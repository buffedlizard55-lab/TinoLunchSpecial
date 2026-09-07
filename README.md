# Tino Lunch Special

A verified transit plan and a verified lunch-special list for **Tuesday, September 8, 2026**.

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
| **Lunch window** | 11:15 AM - 1:30 PM near Cupertino; **leave the house at 11:50 AM** and the 12:42 PM Caltrain gets you home by 2:40 PM |
| **Cost** | **$27.20** round trip with Clipper/contactless (adult; includes the $0.50 Caltrain-to-Muni credit), $27.70 without the credit, $31.00 all cash |

Every number above is a row in `data/` with the agency page it was read from.

## What is here

```
index.html                  the site (no build step, no dependencies, works from file://)
assets/styles.css           system fonts, light/dark-safe layout, print stylesheet
assets/app.js               renders data/generated.js into 8 tabs
data/*.json                 the source of truth - edit these, not generated.js
data/generated.js           the compiled bundle the browser loads (window.TINO_DATA)
data/summary.md             the same tables in plain markdown, easiest to read on GitHub
data/plan.json              trip definition, constraints, decision log
data/transit_outbound.json  3 outbound plans, leg by leg, with per-leg links
data/transit_return.json    3 return plans + the last-workable-train cutoff
data/fares.json             agency fare tables and six day-total scenarios
data/lunch_specials.json    101 lunch entries (27 original + 20 batch-2 + 54 batch-3, all 2026-09-07), hours, days, prices, verification level
data/lunch_rejected.json    28 rejected/deferred candidates (17 rows), each with a reason and a link
data/flags.json             23 irregularities found while verifying - all still listed
data/sources.json           37 source pages, what each one proved, and the fetch status
docs/VERIFICATION.md        how to re-check every row, and what could not be verified
scripts/build_data.py       validates + rebuilds generated.js and summary.md
scripts/check_links.py      every row must link to a citable https page
scripts/smoke_test.js       renders all 8 panels headlessly, fails on undefined/NaN
.github/workflows/deploy.yml
```

## Rebuild and check

```bash
python3 scripts/build_data.py     # validates, writes data/generated.js + data/summary.md
python3 scripts/check_links.py    # every row links to a real page
node scripts/smoke_test.js        # the site renders without throwing
python3 -m http.server 8000       # preview at http://127.0.0.1:8000
```

`build_data.py` exits 1 if a time is not `HH:MM AM/PM`, a fare total does not add up, a lunch row has no source link, a price is implausible, or a stated distance disagrees with the coordinates. That is why the tables can be trusted line by line: the checks run on every commit.

## Verification policy used here

1. **Transit:** times, stops and fares come only from `sfmta.com`, `caltrain.com` and `vta.org`. Third-party trip planners and blog posts were not used for any transit number. Walk distances use OpenStreetMap routing and are labelled as estimates.
2. **Lunch:** a price is only printed if it appears on the restaurant's own website or published menu; hours may come from Yelp/Google/TripAdvisor. Anything seen only on a menu aggregator or delivery app is recorded as a lead and flagged, never presented as verified.
3. **Absence is a result.** "No lunch special published" and "closed on Tuesdays" are rows of their own, so a gap in the data is visible instead of silently dropped.
4. **Conflicts stay visible.** Where two sources disagree (Muni headway text vs timetable, OSM hours vs the restaurant's own site) both values are shown and the choice is explained in `data/flags.json`.
5. **Nothing was backfilled by hand.** The 20-entry search requirement was met by 28 queries over 51 candidates; 27 survived into the master list and 24 were rejected, each with a reason and a link (14 rows in `data/lunch_rejected.json`).

GitHub Pages: `.github/workflows/pages.yml` deploys `index.html` + `assets/` + `data/generated.js`. Set the repo Pages source to **GitHub Actions**. Live URL once enabled: https://buffedlizard55-lab.github.io/TinoLunchSpecial/

## Flagged irregularities (23)

Twelve transit, eleven lunch. Headlines:

* **N Judah does not stop at 22nd St Caltrain.** The metro line ends at King St & 4th St; Caltrain's own station page lists "Muni N-Judah" there. Two options are priced and timed in the data (ride the 6:20 express from the terminal, or transfer at Castro and board at 22nd St on the 6:30 local).
* **SFMTA's own pages disagree** about the pre-6:15 AM N Bus frequency: the route page says every 60 minutes, the timetable says every 15. The timetable (with the date `20260908`) was used, and both readings still make the 6:20 train.
* **The Caltrain weekday PDF could not be downloaded** from the build environment, so minute-level times were read from Caltrain's live per-station tables; the holiday/weekend PDFs were checked and do not cover Sept 8.
* **The VTA stop closest to the destination** (`Stevens Creek & De Anza`) is 1.4 km / 18 min on foot - there is no closer stop, and the 7:26 AM school-only trip is not usable.
* **Four lunch entries could not be pinned to a published price** (Kizuna, Master Oh's, Gardenia hours conflict, Sizzling Lunch has no lunch line) and are marked as such.

Full text of every flag, with the link to re-check it, is in `data/flags.json` and the **Flags** tab.
