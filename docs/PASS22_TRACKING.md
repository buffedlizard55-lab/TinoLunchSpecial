# Pass 22 working log — 2026-09-16 (interim, updated as the sweep runs)

Goal: screen ~100 new candidates Cupertino-first, then the 10-15 mile ring; merge only
rows whose price/days/window/hours/address were read from a fetched, citable page this
session. Dedupe index: 1,111 name|city keys (master 878 + rejected 235) built at pass start.

Searches run this pass (query → best result):
1. Cupertino lunch special restaurant menu 2026 → Yelp top-10 (Siam Station, Wooga, Home Eat, XPP, Jingege & Yaoyao, Liuyishou, Master Oh's, Cap't Loui, Ajito, Gochi) + Happy Lamb, Marufuku, Dainty Cuisine, Olive Garden, Holders
2. Stanford CA restaurant lunch special menu price → stanfords.com promotions (Summer Stack $16 lunch special "through 8/31"), Northgate menu PDF
3. Sunnyvale lunch special menu power lunch → svcoc.org Restaurant Week (time-limited event), P.F. Chang's Sunnyvale (no lunch program)
4. "lunch special" Campbell CA → Yelp top-10 (Wooga, Honō Izakaya & Sushi, Siam Station, Luigi's, Taste Of Thai, Home Eat, Thai Orchid, TGI's, Campbell Cafe & More, Master Oh's) + Water Tower Kitchen, Orchard City Kitchen, Brew City Grill, Naschmarkt, GIWA; La Pizzeria Campbell (already L226)
5. Los Altos restaurant lunch special menu 2026 → losaltosmexicangrill.com (Goose Creek), losaltosrestaurant.com (Santa Barbara), losaltosmenu.com "stuart"
6. Saratoga CA restaurant lunch special daily → warrensaratoga.com (The Saratoga Restaurant), saratoga.com (Saratoga Springs NY specials), discoversaratoga.org (Saratoga County Restaurant Week Nov 2-8 2026)
7. Santa Clara CA lunch special restaurant menu daily → thehutsantaclara.com, wanderlog 50-list, Yelp (Manakish, Good Salad, Katsu Burger, Brew City, Boltiful, The Stand, Eureka $13 lunch special, Joey, Golden Wang Donkatsu)
8. Milpitas lunch special menu restaurant → Yelp (Katsu Gin, Jun Bistro, Siam Station, Yaichi, Mokkoji, Mian, Daeho, Mari Mari, Taipei Station), milpitasbuffet.us, shabuyarestaurant.com/milpitas-online
9. Palo Alto restaurant lunch special price menu → noburestaurants.com/paloalto/menus (separate priced Lunch menu), namasteindiabistro.com, Yelp (Imperial Treasure, Ramen Nagi, J&J, Taste, Sweet Maple, Fambrini's, Pho Banh Mi, Tamarine, Schaub's, So Gong Dong)
10. Mountain View lunch special restaurant menu price → mountainviewseafood.com 2022 PDF, mtviewrestaurant.com, mountainviewdinerco.com/lunch
11. San Mateo Belmont lunch special → wheree Little Belmont Cafe, reddit r/SanMateo, OpenTable business-meals list (Porterhouse, Ranzan, Central Park Bistro, Luceti's)
12. Chinese buffet lunch special Cupertino Sunnyvale → Yelp (Home Eat, Grandma's Kitchen, Asia Village, Royal Cuisine, First Wok), restaurantguru Great Buffet Cupertino ("may be permanently closed")
13. "San Mateo" lunch special restaurant menu price daily → wanderlog 50-list (B Street & Vine, Central Park Bistro, Shabuway, Mingalaba, Maverick Jack's $15 lunch), Yelp (Kirk's, Chili's, Taste & Glory, Foreigner Cafe)
14. Cupertino combo lunch special Korean Japanese Thai → Wooga (already in master), TikTok Wooga, TripAdvisor Tofu Plus Cupertino (2018)
15. Saratoga California lunch special Downtown → theheroranchkitchen.com (DINNER ONLY), Yelp (Pop Haus, GOGA, Flowers, Hero Ranch, Sue's, Bell Tower, Darla, Anchors, Los Gatos Cafe, Mint Leaf), sfstation.com (Bell Tower Bistro, Indo Cafe, La Fondue, Triple Seven)
16. Los Gatos lunch special menu price 2026 → lgdiner.com (already in master), Yelp (Tsing Tao, Wooga, Goku Sushi, Coup De Thai), cafe-inspector Los Gatos Cafe
17. San Jose lunch special restaurant menu daily combo → sanjosesoriginal.com (Lunch Combos $12.90), sanjoselutz.com (Lunch Specials $9.00-$14.50), IHOP San Jose
18. "lunch special" Cupertino restaurantguru/opentable → Gochi (already in master), Tokyo Central (already), Sushi Kuni (already), Gyu-Kaku (already)

## Candidates NOT in the dedupe index (to deep-verify)

Cupertino core:
- [ ] Parkview Kitchen and Spirits (Cupertino) — res-menu.net menu shows breakfast + dinner; need official site, lunch check
- [ ] Jingege & Yaoyao (Cupertino?) — Yelp page says MILPITAS; fantuan lists "(Cupertino)" delivery — resolve the address first
- [ ] Great Buffet (Cupertino) — restaurantguru "May be permanently closed" — verify closure

San Jose / Santa Clara:
- [ ] San Jose's Original (San Jose) — official menu: Lunch Combos $12.90 (dinner $15.90)
- [ ] Lutz (San Jose) — official menu: Lunch Specials $9.00-$14.50
- [ ] Golden Wang Donkatsu (Santa Clara)
- [ ] Boltiful Fresh Kitchen (Santa Clara)
- [ ] La Fontana (Santa Clara, Hilton all-day)

Palo Alto / Stanford:
- [ ] Nobu (Palo Alto) — official site has a separate priced Lunch menu (items ~$10-$95, bento boxes $39-$80); need address + hours

Campbell / Saratoga / Los Altos:
- [ ] Honō Izakaya & Sushi (Campbell)
- [ ] Indo Cafe (Saratoga) — "five rice plates" (sfstation)
- [ ] Triple Seven Pizzeria (Saratoga)
- [ ] Pop Haus (Saratoga) — coffee house; probably no lunch special

Mountain View:
- [ ] Mountain View Seafood — location/address unverified
- [ ] Mt View Restaurant (mtviewrestaurant.com) — http-only domain; address unverified
- [ ] Mountain View Diner (mountainviewdinerco.com) — address unverified

Milpitas:
- (Jingege & Yaoyao if the real address is Milpitas)

Peninsula (San Mateo):
- [ ] Maverick Jack's (San Mateo) — chain; wanderlog review quotes $15 lunch special
- [ ] Shabuway (San Mateo) — chain; wanderlog: weekday lunch menu, weekend similar deal $12.25
- [ ] Mingalaba (San Mateo)
- [ ] Foreigner Cafe (San Mateo)
- [ ] Espetus (San Mateo)
- [ ] Porterhouse (San Mateo) — steakhouse; lunch?
- [ ] Allspice (San Mateo)
- [ ] Ranzan (San Mateo)
- [ ] Central Park Bistro (San Mateo)
- [ ] Luceti's (San Mateo)
- [ ] Sushi Sam (San Mateo)
- [ ] Pasta Moon (Half Moon Bay) — ~25+ mi, likely out of ring

## Candidates already in master/rejected (cross-checks only, not re-added)

Siam Station, Wooga Premium Korean BBQ, Home Eat, XPP Claypot, Liuyishou, Master Oh's,
Cap't Loui, Ajito, Gochi, Happy Lamb Hot Pot, Marufuku Ramen, Dainty Cuisine, Olive Garden,
Holders Country Inn, Sizzling Lunch, Luigi's Pizza & Pasta, Taste Of Thai, Thai Orchid,
TGI's Sushi, Campbell Cafe & More, Water Tower Kitchen, Orchard City Kitchen, Brew City Grill,
Naschmarkt, GIWA, Falafel Flare, Delhi to Kathmandu, Adrestia, P.F. Chang's (chain, no lunch
program — bowls), The Hut (Santa Clara), Eureka (Santa Clara), Katsu Burger, The Stand,
Milpitas Buffet, Jun Bistro, Mokkoji, Yaichi, Katsu Gin, Taipei Station, Manakish, La Fontana?
(re-check), Nobu? (not in index — verify), Imperial Treasure, Tamarine, J & J Hawaiian BBQ,
Fambrini's, Ramen Nagi, Sweet Maple, Pho Banh Mi, Schaub's, Namaste India Bistro,
Grandma's Kitchen, Asia Village, Royal Cuisine, First Wok, Little Belmont Cafe, Farm House
Kitchen, DASH/Dish Dash, B Street & Vine (bloom vine dup check), Kirk's SteakBurgers (Palo Alto),
Tofu Plus, IHOP (Milpitas), Tokyo Central, Sushi Kuni, Gyu-Kaku, GOGA, Flowers Saratoga,
Bell Tower Cafe, Mint Leaf, Darla, Anchors Fish & Chips, Sue's Gallery Cafe, The Hero Ranch
Kitchen (dinner only — verify row exists), Tsing Tao, Goku Sushi, Coup De Thai, Los Gatos Cafe,
The Diner of Los Gatos, Stanford's (see reject below)

## Rejections already provable from fetched/linked pages

- Los Altos Taqueria / Los Altos Mexican Grill — 1316 Red Bank Road, Goose Creek, SC 29445 (site: losaltosmexicangrill.com, fetched 2026-09-16). SC, out of area. Its $7.99-$19.99 "Lunchtime Specials" (Mon-Fri 11-3) are real but in the wrong state.
- The Saratoga Restaurant — warrensaratoga.com; Economos family; 518-area-code ring; Saratoga Springs, NY trap (third occurrence after flags 105/113).
- saratoga.com "Food & Drink Specials" — Saratoga Springs NY (Morrissey's (518) 350-7945, The Iron's Edge, Brook Tavern). NY trap.
- discoversaratoga.org Restaurant Week — Saratoga County NY, Nov 2-8 2026. NY trap + future event.
- Los Altos Restaurant — losaltosrestaurant.com — Santa Barbara, CA. Out of area.
- Los Altos Mexican Restaurant — losaltosmenu.com "stuart" page — not the Bay Area; no in-ring address.
- Stanford's (stanfords.com) — chain site lists only Clackamas OR / Northgate Seattle WA / Tanasbourne OR; the $16 "Summer Stack Special" (lunch, dine-in only) ran "through 8/31" and is no longer posted. No current lunch special; no CA location on the current locations page.
- The Hero Ranch Kitchen (Saratoga CA) — official site: DINNER only (Tue-Thu 5-9:30, Fri-Sat 5-10:30, Sun 5-9). No lunch service.

## Fetch infrastructure note

The sandbox page-fetch proxy began failing with `InvalidAccessKeyId` (routify OSS proxy)
mid-pass around search #10. Pages fetched successfully before the outage: stanfords.com/
promotions/, losaltosmexicangrill.com (3 pages), noburestaurants.com/paloalto/menus (chunk 0
of 5 — the Lunch section). All rows below were read from those pages or from search-result
snippets that link to the cited page; anything not yet re-fetched stays flagged.
