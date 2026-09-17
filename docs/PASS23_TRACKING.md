# Pass 23 working log — 2026-09-17 (interim, complete for this pass)

Goal: re-fetch the four pass-22 proxy-outage rows, resolve the 12 carried leads, rescreen the
ring Cupertino-first, and merge only rows whose evidence was read from a citable page this
session. Dedupe index: 1,137 name|city keys at pass start.

## Fetch-proxy status

WORKING all pass (unlike pass 22). Direct fetches that succeeded: noburestaurants.com/paloalto/
menus, espetus.com/menu/, centralparkbistro.com/lunch-menu/, maverickjacks.com/order/ (JS shell
only), phohanoi.com (x2), toast.app/sizzlinglunch-cupertino, shikisancarlos.com/menu-1,
honojapcuisine.com (x2), radhechaatpureveg.com, rajbhogthali.com (x2), willowstreet.com/
willow-glen, rwgrill.com (x3), withbites.com/merchants/boltifulsantaclara, stampbarandgrill.com
(all-day menu re-check), gochicupertino.com (failed), yoshisushisanjose.com (HTTP 500).

## Search log (query → what it resolved)

1. Maverick Jack's order page fetch → JS shell; LUNCH-FLAG-137 stays open
2. Nobu Palo Alto menus fetch → Lunch section live as captured (L879 confirmed)
3. Espetus menu fetch → lunch restructure $27.95/$37.95/$54.95, weekend $74.95 (L881 corrected)
4. Central Park Bistro site+search → official LUNCH Mon-Fri 11:00-2:15 (L882 corrected)
5. Honō Campbell search+fetch → official hours w/ lunch block; menu "being updated" → L892
6. Golden Wang Donkatsu search → a-la-carte only → reject
7. Boltiful search+fetch → live ordering menu, no specials section → reject
8. Belmont search → belmonthall.net = New England trap; Falafelle candidate; Salt & Brine re-screened (stays rejected)
9. Foster City search → Rickshaw Corner (stays rejected), Sizzling Lunch FC (already L878), Mikiya/MJ/Warehouse/Nina candidates
10. San Carlos search → **Shiki Bistro official Lunch Special**; Stamp $19.95 Yelp claim vs official no-lunch re-check; The Cask re-confirmed (L*)
11. Saratoga search → all-NY trap results again (5th+ firing)
12. Menlo Park search → Little Sky (stays rejected), Farmhouse/Burma Love/Mama Coco (already master), NM Cafe candidate
13. Redwood City search → RW Grill candidates (already L617/L618 + link rot), Bluefin lead, "Downtown" RWC closed
14. RW Grill fetches → location pages live; specials URLs 404 → LUNCH-FLAG-143
15. Bluefin searches → official site http-only/failed; PA "Bluefin Eagle View" trap noted
16. Cupertino bento search → YAYOI/I Heart Bento/O2 Valley/JP Taiwan/Pho Ha Noi/Sizzling Lunch dedupe hits + Koshin Bento lead
17. Cupertino pho search → Pho Ha Noi Sept-special quote; Gogo Pho lead
18. Master cross-check of candidate names (script) → 21 already-listed, 6 already-rejected
19. Row-level inspection of suspected duplicates → L684/L685/L690/L691 addresses suspect
20. Gochi search+Yelp fetch → 19980 E Homestead Rd confirmed (L682 wrong)
21. YAYOI Yelp search → 20682 Homestead Rd confirmed (L690 wrong)
22. Sizzling Lunch Toast fetch → 10033 Saich Way, 11-8:30 daily (L691 wrong; L26 hours fixed)
23. JP Taiwan Bistro search → 10271 Torre Ave confirmed; chowbus "Special Time-Limited Menu 11:30-2:30" (L277 upgraded)
24. Pho Ha Noi site fetches → official hours+menu (L16 upgraded; L685 wrong)
25. Yoshi Sushi search → 250 3rd St confirmed (L666 wrong)
26. Shabuway search → CLOSED per Yelp (reject)
27. Luceti's/Little Belmont search → lunch service, no specials (rejects)
28. Mikiya SM search → AYCE $55-$98, no lunch tier (reject)
29. Mingalaba/B Street & Vine search → no lunch-special evidence (reject/lead)
30. Saratoga leads search → La Fondue $72-$138 (reject); Stackers site names Triple Seven in past tense (reject)
31. Falafelle search → all-day menu (reject)
32. Zaytinya/Telefèric fetch+search → no official lunch price (leads stay)
33. Thali search → **Rajbhog Thali** + **Radhe Chaat** official menus (L894/L893)
34. Rajbhog menu fetch → weekly schedule + a-la-carte; thali price only on delivery menus (mixed)
35. Pineapple Thai search → DoorDash "Lunch Menu" section exists; no price captured (L109 flag)
36. Willow Street search+fetch → Monday $16.99 lunch special (SinglePlatform 7/27/2026) + official address (L895)
37. MJ Sushi/Warehouse Buffet search → no lunch sections (rejects)
38. Milpitas/Fremont search → **Shabuya Milpitas $22.99 Mon-Fri lunch re-confirmed on official page** (L255 cross-check); Dish N Dash/Milpitas Buffet already master
39. Ippudo dup check → L30/L694 same address (L694 removed)
40. Master name-similarity sweep (script) → ~30 suspect pairs; 8 removed with evidence, ~20 flagged

## Candidates screened this pass (~60)

Cross-checks on existing rows (21): Espetus, Maverick Jack's, Central Park Bistro, Nobu, RW
Grill x2, Stamp Bar & Grill, Pho Ha Noi, JP Taiwan Bistro, Sizzling Lunch x2, Gochi x2, YAYOI,
Yoshi Sushi, Ippudo, Pineapple Thai, Shabuya Milpitas, Farmhouse Kitchen, Burma Love, Hobee's
(De Anza unit CLOSED per Yelp - no master row existed, doc note only), Mikiya Santa Clara.

Carried leads resolved (12): Shabuway → closure; Triple Seven → replaced by Stackers; Golden
Wang, Boltiful, Luceti's, Little Belmont, B Street & Vine, La Fondue, Pop Haus (coffee house,
not a lunch venue - folded into the Saratoga rejects of pass 22), Mikiya SM, MJ Sushi,
Mingalaba (still unverified - stays a lead).

Fresh screens (~30): Shiki Bistro, Honō, Rajbhog Thali, Radhe Chaat, Willow Street WG,
Falafelle, Kinjo (NY trap), NM Cafe, Wine Cellar LG (already master), Los Gatos Parkside
(already master), Dish N Dash (already master), Bluefin RWC, Yat Sing, Diner Japonica, Bay
Burgers, Vons Chicken, Woodside Roadhouse, Koshin Bento, Bento Corner, Gogo Pho, Little Sky
Kitchen, Star Chaat, Puranpoli, Apnabazar, Saravana Bhavan (already master), Telefèric PA,
Zaytinya (already rejected), Rickshaw Corner (stays rejected), Salt & Brine (stays rejected),
Number5 Kitchen (stays rejected), Warehouse Buffet, Lazy Dog (already master), Stackers (lead).

## Merge incident (caught and fixed before commit)

`merge_incoming.py` has no memory of withdrawals: after the 8 evidence-based removals, the
script re-added the same rows from `batch13b_...json` and `batch1_...json` (as L883-L890).
Caught by diffing the merge output against HEAD, reverted, and fixed by deleting the 8 poisoned
entries from the incoming files (with an explanatory note in each). The committed state is
879 rows = 882 − 8 + 5.
