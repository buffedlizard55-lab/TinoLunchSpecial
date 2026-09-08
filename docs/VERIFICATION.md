# How to verify every row by hand

`data/summary.md` prints each table with its links inline, so the fastest review is to open
[the live site](https://buffedlizard55-lab.github.io/TinoLunchSpecial/) (or `data/summary.md`) and click a row's source.
This page explains what was and was not possible to verify from the build environment, and gives a short pre-trip checklist.

## Transit - 10 links that cover every number

| # | What it proves | Page |
|---|---|---|
| 1 | Earliest N Judah Bus trips and the 5:53 AM arrival at Townsend & 5th / Caltrain | https://www.sfmta.com/routes/schedule/NBUS?direction_id=1&date=20260908 |
| 2 | Midday N Judah metro (subway) westbound pairs, including 1:56 PM -> 2:38 PM | https://www.sfmta.com/routes/schedule/N?direction_id=0&date=20260908 |
| 3 | N Judah stops, 24-hour note, and the "use the N Bus between subway hours" rule | https://www.sfmta.com/routes/n-judah |
| 4 | The Aug 29, 2026 Muni service change that sets the Sept 8 timetable | https://www.sfmta.com/travel-updates/muni-service-changes-effective-saturday-august-29-2026 |
| 5 | SF terminal southbound departures (6:20 AM express) and northbound arrivals - read the "Weekday" column, and switch the page to the date you travel | https://www.caltrain.com/station/sanfrancisco |
| 6 | 22nd Street southbound departures (6:24 / 6:30 AM) - and no N Judah in its connections | https://www.caltrain.com/station/22ndstreet |
| 7 | Sunnyvale northbound departures (12:12 / 12:42 / 1:12 / 1:42 PM) and the VTA 55 connection | https://www.caltrain.com/station/sunnyvale |
| 8 | Mountain View northbound departures, used for the Sunnyvale-vs-Mountain View comparison | https://www.caltrain.com/station/mountainview |
| 9 | Caltrain fares by zone, day passes, the $0.50 Muni credit, ticket machines and Clipper | https://www.caltrain.com/fares |
| 10 | VTA 55 timepoints both directions and the fare rules ($2.50, 2-hour transfers, $7.50 cap) | https://www.vta.org/sites/default/files/route_schedule_pdfs/current/route_55/route_55_schedule.pdf and https://www.vta.org/go/fares |

Cross-checks that were run: both SFMTA schedule pages re-read with `?date=20260908` (identical to the undated view); the VTA route 55 page
for the service notes; Caltrain's holiday-schedule page to confirm Sept 8 is a normal weekday;
the Orange Line bus-bridge alert (does not touch route 55); the 10-minute Caltrain->VTA walk at
Sunnyvale measured from OpenStreetMap stop coordinates (17 m platform to bay).

### What the build environment could not reach

* `https://www.caltrain.com/media/36422` (weekday timetable PDF) failed on three attempts. Every Caltrain
  minute in this project therefore comes from Caltrain's **live per-station schedule tables** (links 5-8),
  not from the PDF. The PDF's own legend was still captured from the index page, so the train-type numbers
  used in the notes are read from Caltrain's legend, not guessed.
* **Static GTFS and the 511.org trip planner are not part of the committed verification pipeline.**
  Consequence: the itinerary is verified from agency schedule pages and PDFs, not from an engine-computed
  trip-plan export. For a same-day second opinion, run the same chain in https://tripplanner.511.org
  and compare against `data/summary.md`.
* `sfmta.com` route pages render a "Real time arrivals" widget that only works in a browser, so live
  vehicle positions were not read. On a 5:15 AM start, the published timetable is the safer reference anyway.

### VTA stop times: what is exact and what is interpolated

Route 55 publishes **timepoints only**. Exact from the PDF: `Sunnyvale TC 7:19 AM`, `Sunnyvale-Saratoga &
El Camino / & Fremont`, `De Anza & Homestead 7:46 AM`, `Stelling & Stevens Creek`, and the northbound
`Stelling & Stevens Creek 12:01 / 12:31 PM`, `Sunnyvale TC 12:25 / 12:55 PM`.
Two rows in the itinerary are **not** timepoints and are labelled as such:

* `Stevens Creek & De Anza` southbound (about 7:36 AM) and
* `McClellan & Felton` northbound (about 12:06 PM) - the departure you actually stand at, derived from the
  published `Stelling & Stevens Creek` time plus the OSM stop coordinates.

VTA's own wording applies to both: *"VTA buses are scheduled to arrive at the stop 5 minutes early. All
times are approximate."* Budget for that, and use the 7:40 AM trip if you want slack (plan A2).

## Lunch - how each row was decided

Verified level per row, from `data/lunch_specials.json` (current counts: 83 official, 62 review, 166 listing, 28 conflicting, 9 unverified, 4 mixed):

* **official** - price and/or hours read from the restaurant's own website, ordering page or menu PDF.
  Examples: Benihana's Power Lunch $15.95 (Mon-Fri 11-3) on `benihana.com/locations/cupertino/`;
  Gyu-Kaku's lunch combos $18.95 / $22.95 in `https://www.gyu-kaku.com/wp-content/uploads/2025/01/cp_lunch2411.pdf`;
  Home Eat's $13.99 / $14.99 lunch specials on its Toast ordering page.
* **review** - the special exists in a Yelp/Google review, but the price is a reviewer's figure.
  Treat the price as indicative until the restaurant confirms it.
* **listing** - address/hours from a directory; no price published anywhere (Taste Palo Alto's lunch menu
  block on OpenTable is listed with its prices because OpenTable reproduces the venue's menu, and that is
  flagged in the row).
* **conflicting** - two sources disagree (Gardenia: Tuesday brunch 10:30-14:30 on one page, "closed Thursday"
  on an aggregator). Both are shown; nothing was silently picked.
* **unverified** - no usable current price/hours proof was found. These rows exist so the gap is visible; call before going.

Two rules that changed the outcome and are worth knowing when you review:

1. **Aggregator prices were never promoted to verified.** Menu/delivery sites (zmenu, menupix, restaurantji,
   restaurantguru, beyondmenu, Postmates, DoorDash) were used to find candidates and cross-check hours only.
   `Wooga`'s $9.99 price, for instance, appears **only** on an aggregator, so its row says so.
2. **The name of the restaurant is not evidence of its location.** `Cap't Loui`'s $13.95 lunch special is real
   but published for the Las Vegas restaurant; the "Los Altos" breakfast-lunch rows resolve to a Chico
   restaurant and Sparks, NV; `Z & Y` is SF Chinatown; `Old Spaghetti Factory`'s nearest location is San Jose.
   Each of those is in `data/lunch_rejected.json` with the link that proves it.

Reddit was searched for Cupertino/South Bay lunch deals and produced nothing usable for this area (only
San Antonio and Chicago threads). Recorded so the empty result is not mistaken for "not tried".

## Pre-trip checklist (5 minutes, Tuesday morning)

1. `sfmta.com/routes/n-judah` - is the subway back? If it is running by 5:15 AM, take the metro instead of the bus.
2. Caltrain's live page for the station you board - does the 6:20 AM express still run as a **southbound express from the SF terminal**? If the 6:20 is gone, the 6:25 local still reaches Sunnyvale before the 7:40 AM trip on plan A2.
3. VTA 55 service alerts (link 10) - any detour on Stevens Creek Blvd.
4. Call the restaurant you picked: lunch counters are the first thing to change, and five rows depend on hours more than on price.
5. Load a Clipper card, or tap the same contactless card on Muni **and** onto Caltrain so the $0.50 credit applies.
6. On the way back, board at `McClellan & Felton` and be at the bay for the **12:42 PM** northbound; the 1:42 PM train puts you home at 3:43 PM, past the deadline.
