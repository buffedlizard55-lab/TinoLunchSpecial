# Tino Lunch Special

A verified lunch-special master list for Cupertino and its 10-15 mile ring, plus a verified transit plan for **Tuesday, September 8, 2026**.

**Site layout (lunch front page since 2026-09-11, data refreshed 2026-09-14):** the front page (`index.html`) is the **lunch deals** - verified specials at the very top, then the full searchable table. The public-transit route plan lives on its own subpage, [`transit.html`](transit.html) - the trip-planning system itself was left untouched by this change.

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
data/lunch_specials.json    858 lunch entries (27 original + 20 batch-2 + 54 batch-3 + 49 batch-4 + 101 batch-5 + 1 review-pass + 100 batch-6/7 on 2026-09-07 + 103 batch-8 on 2026-09-08 + 68 batch-9 on 2026-09-10 + 10 batch-10 on 2026-09-11 + 59 batch-11 + 4 batch-12 follow-up on 2026-09-11 + 111 batch-13 on 2026-09-11 + 102 batch-14 on 2026-09-12 + 10 batch-15 on 2026-09-14 + 31 batch-16 on 2026-09-14 + 8 batch-17 on 2026-09-15), hours, days, prices, verification level
data/lunch_rejected.json    192 rejected/deferred rows covering 192 distinct businesses, each with a reason and a link
data/flags.json             117 irregularities found while verifying (103 lunch, 14 transit) - all still listed
data/sources.json           124 source pages, what each one proved, and the fetch status
docs/VERIFICATION.md        how to re-check every row, and what could not be verified
docs/REVIEW_2026-09-15_pass17.md  current QA pass (seventeenth lunch pass - ~100 candidates screened against a 1031-key dedupe index, 8 net-new, 9 rejections/bad-source notes, 8 new flags, 858 total)
docs/REVIEW_2026-09-14_pass16.md  previous QA pass (sixteenth lunch pass - 56 candidates resolved, 31 net-new, 25 duplicate detections, 11 rejections, 6 held back by the address dedupe, 850 total)
docs/REVIEW_2026-09-14_pass15.md  the fifteenth pass (27 candidates resolved, 10 net-new, 17 cross-checks, 819 total)
docs/REVIEW_2026-09-12_pass14.md  the fourteenth pass (102 new rows, 809 total)
docs/REVIEW_2026-09-11_pass13.md  thirteenth lunch pass (111 new, 707 total)
docs/REVIEW_2026-09-11_pass11.md  eleventh lunch pass validation
docs/REVIEW_2026-09-11.md   the tenth lunch pass + the front-page summary fix
docs/REVIEW_2026-09-10.md   the ninth lunch pass + the site split
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
5. **Nothing was backfilled by hand.** The first search pass ran 28 queries over 51 candidates; 27 survived into the master list and the rest were rejected, each with a reason and a link. Later passes added 496 more rows the same way (the seventh pass added 100, the eighth 103 - each searched and verified line by line before adding - and the ninth pass on 2026-09-10 searched ~100 new candidates Cupertino-first, then a 10-15 mile ring that now also covers Fremont, Newark, Union City, San Mateo, Redwood City, San Carlos and Foster City: 68 rows survived, 30 candidates were rejected or deferred with links, ~341 hits were deduped against the master list, four were confirmed closed (Pot Sticker King, Su Zhe Eatery, La Strada, China Delight), one new entry superseded its own earlier deferral twice over via `supersedes_rejection`, and a would-be duplicate (The Diner of Los Gatos) was caught by the address check); the tenth pass on 2026-09-11 screened ~30 more candidates and added 10 rows, deferring the rest because a price without a citable street address and weekly hours cannot be merged; and the eleventh pass on 2026-09-11 ran an automated name/city dedupe over 115 candidate names before opening a single page (85 new, 30 already listed), then swept Milpitas, Fremont, Newark, Santa Clara, San Jose, Los Gatos, Los Altos, Palo Alto, Cupertino, Sunnyvale, Santana Row and the chain row for a further ~90 candidates - 59 rows survived into the master list (L534-L592) and 21 became rejects or deferred leads, five of them outright closures (Left Bank, Rosie McCann's and Yankee Pier on Santana Row, Vida Tapas in Mountain View, plus Sushi Confidential's downtown room which has no Tuesday service at all). Two rows that survived the merge were withdrawn the same day on a self-audit when they proved to be duplicates (LUNCH-FLAG-35). The master list is now 707 rows with 154 reject rows in `data/lunch_rejected.json` (that was pass 13; pass 14 took it to 809 rows / 166 rejects, pass 15 to 819 rows / 172 rejects, pass 16 to 850 rows / 183 rejects and pass 17 to 858 rows / 192 rejects). See `docs/REVIEW_2026-09-11_pass13.md`.

GitHub Pages is enabled at https://buffedlizard55-lab.github.io/TinoLunchSpecial/. The repo also includes `.github/workflows/pages.yml` for Action-based deployment if the Pages source is switched from `main /` to **GitHub Actions** later.

## Flagged irregularities (117)

Fourteen transit, one hundred and three lunch. Headlines:

* **N Judah does not stop at 22nd St Caltrain.** The metro line ends at King St & 4th St; Caltrain's own station page lists "Muni N-Judah" there. Plans board at the terminal and still publish the 22nd St times in the same rows for reference (same Zone 1 fare).
* **SFMTA's own pages disagree** about the pre-6:15 AM N Bus frequency: the route page says every 60 minutes, the timetable says every 15. The timetable (with the date `20260908`) was used, and both readings still make the 6:20 train.
* **The Caltrain weekday PDF could not be downloaded** from the build environment, so minute-level times were read from Caltrain's live per-station tables; the holiday/weekend PDFs were checked and do not cover Sept 8.
* **The VTA stop closest to the destination** (`Stevens Creek & De Anza`) is 1.4 km / 18 min on foot - there is no closer stop, and the 7:26 AM school-only trip is not usable.
* **Nine lunch entries remain unverified leads** and many more are listing/review-level only; the lunch front page keeps those rows visible instead of promoting them to verified specials.
* **Pass-9 additions (2026-09-10, LUNCH-FLAG-21..25):** Sankranti's Sunnyvale address shows up under the name "Bombay to Goa" in 2026 listings while 2023/2025 sources still price its lunch buffet - the row stays `conflicting` with no asserted price; four new businesses are **closed on Tuesdays** (Sala Thai Fremont, No 5 House San Mateo, Takahashi Market, plus Rin-Tei's Tuesday-closed block) and four more have disputed Tuesday lunch (Hula Plate's own site vs Yelp, Restaurant Silla's three different hours blocks, Willow Street Pizza's contradictory own pages, and the tiny Urban Kitchen entry); "Saratoga lunch special" searches keep returning Saratoga Springs NY - those were rejected with the proving links; and reviewer-quoted prices ($1 tacos, $14.99 rolls, $9.99/$14.99 Early Dine) are kept in flags, never in the price column.

* **Pass-12 follow-up (2026-09-11, LUNCH-FLAG-43):** four additional rows (Last Chance Restaurant, Nar Restaurant, Delarosa Palo Alto, and Madera at Rosewood Sand Hill) were added only after address and weekly lunch hours were citable. Last Chance and Delarosa have printed menu item prices; Nar and Madera remain unpriced because no current lunch-special price was exposed. These are clearly flagged as lunch-service/menu rows rather than overstated discount promotions. See `docs/REVIEW_2026-09-11_pass12.md`.
* **Pass-11 additions (2026-09-11, LUNCH-FLAG-34..42):** five closures caught before publication (Left Bank Brasserie, Rosie McCann's and Yankee Pier on Santana Row, Vida Tapas Y Cocteles on Castro Street, plus Sushi Confidential's downtown room which has no Tuesday lunch); two rows merged and then withdrawn on a same-day audit when they turned out to be duplicates (Inchin's Bamboo Garden - a ZIP spelling of an existing row - and Opa! Willow Glen, whose street address already belongs to Burma Roots); Boda's $5.99 weekday lunch is real but printed only on an http-only site, so the price is described and flagged rather than printed; six restaurants publish two different hours blocks for the same day (Mezcal, Strata, Togo's, Veggie Grill, Lotus Thai, and the withdrawn Opa!) and both values are shown; and eight Reddit / aggregator cheap-lunch prices (Habit $10, Red Robin $10, Olive Garden $5.99, Milpitas Buffet $19.99, Sizzler $5.49-$6.99, Don Giovanni $19.95, Veggie Grill $10-$15) are quoted in the rows but kept out of the price columns. Tatami Buffet in Cupertino is the one row whose entire operating week is a lunch service (11:30 AM-2:30 PM). Pass 11 added 59 rows against a 100-row target; the shortfall is reported in LUNCH-FLAG-42 rather than padded, because Yelp returns HTTP 403 to direct fetch from this environment.

* **Pass-15 additions (2026-09-14, LUNCH-FLAG-70..96):** the newest pass re-screened ~70 candidates Cupertino-first and across the 10-15 mile ring. Ten rows merged (Pings Bistro and DC Tap House in Cupertino, Tessora's in Campbell, Dos Burros in Saratoga, MoDak Korean Chicken and Tonkatsu Sakuton in San Jose, Toki Sushi and Speedy's Tacos in Mountain View/Sunnyvale, Yuki Sushi in Santa Clara, Vishnuji Ki Rasoi in Sunnyvale) - and **17 further candidates turned out to be rows the master list already carried, so they were merged as cross-checks rather than duplicated**. The cross-checks produced the sharpest findings of the pass: Uzumakiya Udon Izakaya (L693) now shows a different address on its own site and both Tuesday and Wednesday closed while the master row says De Anza Blvd with a $14.99 lunch, and Yelp now titles Mandarin Gourmet Cupertino (L456) CLOSED even though the owner's own answers describe lunch service. Two out-of-ring traps were caught before they could enter the list - a "$20 three-course lunch" page belonging to a New Jersey restaurant and a "Mountain View Chalet" lunch page belonging to Asbury, New Jersey - and Bobbi's Coffee Shop & Cafe, a Cupertino institution, was confirmed permanently closed on 2025-12-31 (SFGATE, Yelp CLOSED badge, r/Cupertino) and rejected rather than listed. The pass is honest about its arithmetic: the 100-row target was not reached in this pass, because just under two thirds of the candidates that passed verification were already on the list. See `docs/REVIEW_2026-09-14_pass15.md`.

* **Pass-17 additions (2026-09-15, LUNCH-FLAG-104..111):** the seventeenth pass screened **~100 candidate names Cupertino-first and across the 10-15 mile ring**, grepping every one against a **1,031-key `norm(name)|norm(city)` dedupe index** built from the master and reject files *before* opening a page. **8 net-new rows merged (L851-L858)** with 9 rejections and bad-source notes (R184-R192). The clearest qualifying find is **The Courtyard Long Bar & Bistro (Los Altos)**, whose own menu prints a named **"Soup & Sandwich Special $17"** on a $7-$28 lunch card served Mon-Sat 11:00 AM - 1:30 PM. **Birk's Restaurant (Santa Clara)** was verified straight off its own April 2026 `Lunch_SP2026.pdf` ($14-$27 lunch-only band, Mon-Fri 11:00 AM - 2:30 PM), and **Barbayani Greek Taverna (Los Altos)** off an explicitly separate "Barbayani Lunch Menu" on its own Toast page ($23-$42 daily 11:30-2:30, several dishes genuinely cheaper than the adjacent dinner card). Four venues publish a lunch *window* but **no lunch price on any page they control** - Sorelle Italian Bistro (Wed-Fri 11:30-2:00), Senza Italian Kitchen (Wed-Fri 11:00-2:00), Hibari in Portola Valley (menu published only as a Canva image slideshow) and Tal Palo (no fixed menu by design, rejected) - so three were listed with **deliberately empty price columns** and press/reviewer figures (Hibari $18-$66 lunch sets, Senza's $40 verbal special) are held in row flags as quotes, never as prices (LUNCH-FLAG-106). Two rows are honest **absence results**: Crepevine Palo Alto and The Good Salad Campbell publish no lunch special at all, and say so on their own priced menus. Traps caught: a "$15 Breakfast/Lunch Specials" page that belongs to **Saratoga County, NEW YORK** (LUNCH-FLAG-105), an aggregator link routing **Kakuna Sushi Milpitas to the Fremont store** (LUNCH-FLAG-110), a TripAdvisor record claiming a **5:00 AM opening** for a Sunnyvale Korean BBQ restaurant (LUNCH-FLAG-109), three dead restaurant-controlled menu URLs including the exact path OpenTable advertises for Barbayani (LUNCH-FLAG-107), and a Hibari day conflict where Yelp says Tuesday closed while both December 2025 press write-ups say Tuesday-Sunday (LUNCH-FLAG-108). **Oren's Hummus Palo Alto and Oren's Hummus Express are genuinely missing from the master list but were deliberately NOT added**, because no restaurant-controlled page was fetched and no lunch special was evidenced - only aggregator hour grids that contradict each other (LUNCH-FLAG-111). The 8-row result against a 100-candidate screen is reported as a shortfall in LUNCH-FLAG-104 rather than padded: the dense core of the ring is close to exhausted after sixteen prior passes, and a padded row would be a duplicate, which is a hallucination in table form. The route-planning system was not touched. See `docs/REVIEW_2026-09-15_pass17.md`.

* **Pass-16 additions (2026-09-14, LUNCH-FLAG-97..103):** the sixteenth pass screened ~192 fresh candidate names Cupertino-first and across the ring, wrote up 56 in eight batch files (`batch16a`-`batch16h`) and merged **31 net-new rows (L820-L850)** with 11 rejections (R156-R166). **25 of the 56 turned out to be venues the master list already carried** - including an entire batch file of eight Sunnyvale/Santa Clara rows that was verified before it was screened - so their captures were filed as cross-checks instead of duplicates and the shortfall against the 100-row target is reported in LUNCH-FLAG-103 rather than padded. Four of the eleven rejections are **stale CLOSED listings that still print a full weekly schedule** (Pho & Bun in Milpitas, whose TripAdvisor page still says "Open until 9:30 PM"; Kitayama Yoichi in Fremont; Bierhaus at 383 Castro St, one letter away from the *open* Das Bierhauz two blocks up; and Square Pie Guys' closed Local Kitchens unit that printed 11:00 AM-midnight daily). Three more are out-of-area "Los Altos" name traps in Salinas, Goleta and San Bernardino, and one is a genuine "$15 lunch" Restaurant Week page belonging to Saratoga Springs, **New York**. The sharpest data findings: **Lotus Thai Bistro is listed twice in the master list** (L76 with no hours and L650 with hours, one address - LUNCH-FLAG-99); **Kiya Sushi's own ordering site advertises a lunch special until 3:00 PM while its own hours close at 2:30 PM Mon-Thu** (LUNCH-FLAG-100); Jang Su Jang's own holiday note still names November 23 as Thanksgiving, which was true in 2023 and not in 2026 (LUNCH-FLAG-101); and **six verified rows are held back by street-address collisions**, including Elia at 276 E Campbell Ave, which looks like a rebrand of L532 Opa! Authentic Greek Cuisine at the same address (LUNCH-FLAG-98). Reviewer-quoted prices found this pass - Kiya Sushi's $14.99 trio-roll lunch, Country Way's $7.95 bacon-burger lunch, Jang Su Jang's $75 galbi jjim, Elia's $29 moussaka, Tai Pan's "sesame balls 5 for $1" - are attached to their rows as quotes and kept out of the price columns, which is why all 31 new rows carry no printed price. See `docs/REVIEW_2026-09-14_pass16.md`.

Full text of every flag, with the link to re-check it, is in `data/flags.json` - lunch flags on the front page, transit flags on the transit subpage.
