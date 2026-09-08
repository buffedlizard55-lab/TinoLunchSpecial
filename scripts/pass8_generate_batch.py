#!/usr/bin/env python3
"""One-off generator for data/incoming/batch8.json (pass 8; run once, before merge_incoming.py, 2026-09-08).

Every row below was transcribed from the source URLs listed on it (Yelp
business-page hours/address snippets, official sites, OpenTable/Toast/
beyondmenu/allmenus menu mirrors). Prices are only filled in when a source
printed one; everything else is left null and flagged.
"""
import json, os

DAY = "2026-09-08"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "incoming", "batch8.json")

rows = []


def yelp(slug):
    return "https://www.yelp.com/biz/" + slug


def gmap(name, addr):
    q = (name + " " + addr).replace(" ", "+").replace(",", "")
    return "https://www.google.com/maps/search/?api=1&query=" + q


def add(name, city, address, area, cuisine, days_open, tue, special, sources,
        level="review", flags=None, phone=None, yelp_slug=None, bus=None,
        price_from=None, price_to=None, sp_days=None, window=None, includes=None,
        open_tue=None):
    if open_tue is None:
        open_tue = not tue.lower().startswith("closed") and "dinner only" not in tue.lower()
    if bus is None:
        bus = {"ok": False, "note": "Outside the Cupertino return corridor - drive/rideshare only."}
    rows.append({
        "name": name, "city": city, "address": address, "area": area, "cuisine": cuisine,
        "days_open": days_open, "hours_tuesday": tue,
        "lunch_special": {"name": special, "price_from": price_from, "price_to": price_to,
                          "days": sp_days, "window": window, "includes": includes},
        "open_on_trip_date": open_tue,
        "fits_return_bus": bus,
        "flags": flags or [],
        "phone": phone,
        "review_links": {"yelp": yelp(yelp_slug) if yelp_slug else None,
                         "google_maps": gmap(name, address)},
        "verification": {"level": level, "accessed": DAY,
                         "sources": [{"label": l, "url": u} for l, u in sources]},
    })


CUP_BUS = {"ok": True, "note": "On/near Stevens Creek Blvd or De Anza Blvd - VTA 23/523 corridor back toward Sunnyvale/Caltrain."}
CUP_NEAR = {"ok": True, "note": "Cupertino - short walk/ride to the Stevens Creek/De Anza VTA corridor."}
NO_PRICE = "Lunch price not printed by any checked source - confirm on arrival."

# ---------------------------------------------------------------- Cupertino
add("Avachi Biryani House", "Cupertino", "10251 S De Anza Blvd, Cupertino, CA 95014",
    "De Anza Blvd", "Indian (Hyderabadi)",
    "Daily lunch & dinner", "11:30 AM - 2:30 PM, 5:00 PM - 9:30 PM",
    "Lunch buffet", [
        ("Yelp - Avachi Biryani House (address, phone, lunch Mon-Fri 11:30-2:30, Sat-Sun 11:30-3)", yelp("avachi-biryani-house-cupertino")),
    ], flags=["Buffet price ($17 weekday / $22 weekend) appears only in a Yelp review - unverified."],
    phone="(408) 982-5220", yelp_slug="avachi-biryani-house-cupertino", bus=CUP_BUS,
    sp_days="Daily", window="11:30 AM - 2:30 PM (Sat-Sun to 3 PM)")

add("Safar By Karimi", "Cupertino", "19930 Stevens Creek Blvd, Cupertino, CA 95014",
    "Stevens Creek Blvd", "Persian / Afghan",
    "Wed-Mon; closed Tue", "Closed Tuesdays",
    "Lunch menu 11:30-3", [
        ("Yelp - Safar By Karimi (closed Tue; lunch 11:30-3)", yelp("safar-by-karimi-cupertino")),
        ("Official site (hours; no prices)", "https://www.safarbykarimi.com/"),
    ], flags=["CLOSED on the trip date (Tuesday).", NO_PRICE],
    phone="(408) 816-8080", yelp_slug="safar-by-karimi-cupertino", bus=CUP_BUS,
    sp_days="Wed-Mon", window="11:30 AM - 3:00 PM", open_tue=False)

add("The City Fish", "Cupertino", "21678 Stevens Creek Blvd, Cupertino, CA 95014",
    "West Stevens Creek Blvd", "Seafood / Fish & chips",
    "Daily", "10:00 AM - 8:30 PM",
    "Fish & chips (2 pc) / chowder combo", [
        ("Official menu - cityfishco.com (fish & chips $11 / $15, chowder combo $15)", "https://www.cityfishco.com/menu-1"),
        ("Yelp - The City Fish (address, phone, daily 10-8:30)", yelp("the-city-fish-cupertino")),
    ], level="official", phone="(408) 320-1434", yelp_slug="the-city-fish-cupertino", bus=CUP_BUS,
    price_from=11.0, price_to=15.0, sp_days="Daily", window="All day",
    includes="Counter-service; prices from the official online menu (no separate lunch pricing).")

add("Harumi Sushi", "Cupertino", "20030 Stevens Creek Blvd, Cupertino, CA 95014",
    "Stevens Creek Blvd", "Japanese / Sushi",
    "Daily", "11:30 AM - 9:00 PM",
    "Lunch bento", [
        ("Official site - harumisushi.com (hours; no prices)", "https://www.harumisushi.com/"),
        ("Yelp - Harumi Sushi (bento prices quoted $16.05-$17.07 vs $19.95 in different listings)", yelp("harumi-sushi-cupertino")),
    ], level="conflicting", flags=["Bento price conflicts between menu mirrors ($16-17 vs $19.95) - treat as approx."],
    phone=None, yelp_slug="harumi-sushi-cupertino", bus=CUP_BUS,
    price_from=16.05, price_to=19.95, sp_days="Daily", window="Lunch")

add("O2 Valley", "Cupertino", "19058 Stevens Creek Blvd, Cupertino, CA 95014",
    "East Stevens Creek Blvd", "Taiwanese / Boba cafe",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special (rice/noodle plates)", [
        ("Yelp - O2 Valley (address, phone, daily 11-9)", yelp("o2-valley-cupertino")),
        ("Official site (online ordering only; prices not readable)", "https://www.o2-valley.com/"),
    ], flags=[NO_PRICE], phone="(408) 564-0542", yelp_slug="o2-valley-cupertino", bus=CUP_BUS)

add("Orange Square", "Cupertino", "20343 Stevens Creek Blvd, Cupertino, CA 95014",
    "Stevens Creek Blvd", "Vietnamese / Asian",
    "Daily", "11:00 AM - 8:00 PM",
    "Wednesday special", [
        ("Yelp - Orange Square Cupertino (address, phone, daily 11-8)", yelp("orange-square-cupertino")),
    ], flags=["$9.99 Wednesday special is a Yelp-review claim, not a menu price.", "Separate from the Milpitas Orange Square already listed."],
    phone="(510) 602-5278", yelp_slug="orange-square-cupertino", bus=CUP_BUS,
    sp_days="Wed", window="Lunch")

add("Wei's Fish", "Cupertino", "10520 S De Anza Blvd, Cupertino, CA 95014",
    "De Anza Blvd", "Chinese (fish / seafood)",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Wei's Fish (address, phone, Mon-Thu 11-9, Fri-Sun 11-9:30)", yelp("weis-fish-cupertino")),
    ], flags=[NO_PRICE], phone="(408) 549-3087", yelp_slug="weis-fish-cupertino", bus=CUP_BUS)

add("Beijing Duck House", "Cupertino", "10883 S Blaney Ave, Cupertino, CA 95014",
    "Blaney Ave (off Stevens Creek)", "Chinese (Peking duck)",
    "Wed-Mon; closed Tue", "Closed Tuesdays",
    "Lunch service 11:30-2:30", [
        ("Yelp - Beijing Duck House (closed Tue; 11:30-2:30 & 5-9)", yelp("beijing-duck-house-cupertino")),
        ("Michelin Guide listing", "https://guide.michelin.com/us/en/california/cupertino/restaurant/beijing-duck-house"),
    ], flags=["CLOSED on the trip date (Tuesday).", NO_PRICE],
    phone="(408) 366-0588", yelp_slug="beijing-duck-house-cupertino", bus=CUP_NEAR, open_tue=False)

add("YAYOI", "Cupertino", "20682 Homestead Rd, Cupertino, CA 95014",
    "Homestead Rd", "Japanese (teishoku)",
    "Daily", "11:30 AM - 8:00 PM",
    "Teishoku set meals", [
        ("Official menu - yayoi-us.com (teishoku $22-$33.90)", "https://www.yayoi-us.com/menu"),
        ("Yelp - YAYOI Cupertino (address, phone, daily 11:30-8)", yelp("yayoi-cupertino")),
    ], level="official", phone="(408) 564-8852", yelp_slug="yayoi-cupertino", bus=CUP_NEAR,
    price_from=22.0, price_to=33.9, sp_days="Daily", window="All day",
    includes="Set meal with rice, miso soup and sides; same price lunch and dinner.")

add("Azuma", "Cupertino", "19645 Stevens Creek Blvd, Cupertino, CA 95014",
    "Stevens Creek Blvd", "Japanese",
    "Mon-Sat lunch & dinner", "11:30 AM - 2:00 PM, 5:00 PM - 9:00 PM",
    "Lunch menu", [
        ("Yelp - Azuma Cupertino (address, phone, lunch 11:30-2 Mon-Sat)", yelp("azuma-cupertino")),
    ], flags=[NO_PRICE], phone="(408) 257-4057", yelp_slug="azuma-cupertino", bus=CUP_BUS,
    sp_days="Mon-Sat", window="11:30 AM - 2:00 PM")

add("Alexander's Steakhouse", "Cupertino", "19379 Stevens Creek Blvd, Cupertino, CA 95014",
    "Stevens Creek Blvd (Main Street)", "Steakhouse",
    "Lunch Wed-Sun; dinner nightly", "Dinner only (lunch Wed-Fri 12-2, Sat-Sun 11-2)",
    "Weekday prix-fixe lunch", [
        ("Official weekday lunch menu - alexandershospitality.com ($58 prix fixe)", "https://www.alexandershospitality.com/cupertino-menus"),
        ("Yelp - Alexander's Steakhouse Cupertino (hours)", yelp("alexanders-steakhouse-cupertino")),
    ], level="conflicting", flags=["No lunch on Tuesday (lunch Wed-Sun only).", "Prix-fixe quoted $58 (official) vs $55/$70 in third-party mirrors."],
    phone="(408) 446-2222", yelp_slug="alexanders-steakhouse-cupertino", bus=CUP_BUS,
    price_from=58.0, sp_days="Wed-Fri", window="12:00 PM - 2:00 PM", open_tue=False)

add("Thai Square", "Cupertino", "21267 Stevens Creek Blvd Ste 311, Cupertino, CA 95014",
    "West Stevens Creek Blvd (Oaks)", "Thai",
    "Daily", "11:00 AM - 3:30 PM, 5:00 PM - 9:00 PM",
    "Lunch fried rice / noodle plates", [
        ("OpenTable - Thai Square Cupertino (hours; menu $10-11 lunch plates, 2022 data)", "https://www.opentable.com/r/thai-square-cupertino"),
        ("Yelp - Thai Square Cupertino", yelp("thai-square-cupertino")),
    ], flags=["OpenTable menu prices are dated (2022) - expect higher."],
    yelp_slug="thai-square-cupertino", bus=CUP_BUS,
    price_from=10.0, price_to=11.0, sp_days="Mon-Sat", window="11:00 AM - 3:30 PM")

add("Thai Bangkok Cuisine", "Cupertino", "21670 Stevens Creek Blvd, Cupertino, CA 95014",
    "West Stevens Creek Blvd", "Thai",
    "Tue-Sun; closed Mon", "11:00 AM - 2:30 PM, 5:00 PM - 9:00 PM",
    "Lunch menu (entrees, noodles, soups)", [
        ("Official site - thaibangkokcuisineca.com (hours: closed Mon; Tue-Fri 11-2:30 & 5-9; Sat-Sun 11-3 & 5-9)", "https://www.thaibangkokcuisineca.com/"),
        ("Beyondmenu mirror (lunch entrees/noodles from $19, lunch BBQ $21, lunch soups $11.99)", "https://www.beyondmenu.com/85416/cupertino/thai-bangkok-cuisine-cupertino-95014.aspx"),
    ], level="conflicting", flags=["OpenTable lists Mon-Fri lunch but the official site says closed Monday - official used."],
    phone="(669) 342-7300", yelp_slug="thai-bangkok-cuisine-cupertino", bus=CUP_BUS,
    price_from=11.99, price_to=21.0, sp_days="Tue-Fri", window="11:00 AM - 2:30 PM")

add("Olarn Thai", "Cupertino", "19672 Stevens Creek Blvd, Cupertino, CA 95014",
    "Stevens Creek Blvd", "Thai",
    "Daily", "11:00 AM - 10:00 PM",
    "Lunch entrees", [
        ("OpenTable - Olarn Thai (hours daily 11-10)", "https://www.opentable.com/r/olarn-thai-cupertino"),
        ("Beyondmenu mirror (lunch entrees $9.95-$14.95, 2019 data)", "https://www.beyondmenu.com/olarn-thai-cupertino"),
    ], flags=["Menu prices are from a 2019 mirror - almost certainly higher now."],
    yelp_slug="olarn-thai-cupertino", bus=CUP_BUS,
    price_from=9.95, price_to=14.95, sp_days="Daily", window="11:00 AM - 3:00 PM")

add("I Heart Bento", "Cupertino", "10129 S De Anza Blvd, Cupertino, CA 95014",
    "De Anza Blvd", "Japanese (bento)",
    "Mon-Sat; closed Sun", "11:00 AM - 7:00 PM",
    "Bento boxes", [
        ("Zmenu - I Heart Bento (address, phone, hours Mon-Sat 11-7)", "https://www.zmenu.com/i-heart-bento-cupertino-online-menu/"),
        ("ezCater menu mirror (bentos $16-$21.50)", "https://www.ezcater.com/catering/i-heart-bento"),
    ], level="listing", phone="(408) 996-0928", yelp_slug="i-heart-bento-cupertino", bus=CUP_BUS,
    price_from=16.0, price_to=21.5, sp_days="Mon-Sat", window="All day")

add("Nutrition Restaurant", "Cupertino", "10935 N Wolfe Rd, Cupertino, CA 95014",
    "N Wolfe Rd (Cupertino Village)", "Chinese",
    "Tue-Sun; closed Mon", "10:30 AM - 8:30 PM",
    "Rice plates / entrees", [
        ("Yelp - Nutrition Restaurant (address, phone, closed Mon; Tue-Fri 10:30-8:30; entrees $9.59-$17.99)", yelp("nutrition-restaurant-cupertino")),
    ], flags=["Yelp rating 3.1 - reviews mixed."], phone="(408) 777-8208",
    yelp_slug="nutrition-restaurant-cupertino", bus=CUP_NEAR,
    price_from=9.59, price_to=17.99, sp_days="Tue-Sun", window="All day")

add("Curry Pizza House", "Cupertino", "20080 Stevens Creek Blvd Ste 106, Cupertino, CA 95014",
    "Stevens Creek Blvd", "Indian-fusion pizza",
    "Daily", "10:00 AM - 10:00 PM",
    "Lunch Special #2 - personal 8\" specialty pizza + drink", [
        ("TripAdvisor - Curry Pizza House Cupertino (menu: Lunch Special 2 $13.99, Mon-Fri open to 4 PM)", "https://www.tripadvisor.com/Restaurant_Review-g32273-d19306765-Reviews-Curry_Pizza_House-Cupertino_California.html"),
        ("OpenTable - Curry Pizza House Cupertino (address, phone, daily 10-10)", "https://www.opentable.com/r/curry-pizza-house-cupertino"),
    ], phone="(408) 617-9050", yelp_slug="curry-pizza-house-cupertino", bus=CUP_BUS,
    price_from=13.99, sp_days="Mon-Fri", window="Open - 4:00 PM",
    includes="Personal 8-inch specialty pizza + drink; side salad +$2.")

add("Kura Revolving Sushi Bar", "Cupertino", "19600 Vallco Pkwy Ste 160, Cupertino, CA 95014",
    "Vallco Pkwy / Main Street", "Japanese (conveyor sushi)",
    "Daily", "11:00 AM - 9:30 PM",
    "Per-plate pricing (no lunch special)", [
        ("Restaurant Guru - Kura Cupertino (address, phone, hours Mon-Thu 11-9:30, Fri-Sat 11-10:30, Sun 11-10)", "https://restaurantguru.com/Kura-Revolving-Sushi-Bar-Cupertino-2"),
        ("Yelp - Kura Revolving Sushi Bar Cupertino", yelp("kura-revolving-sushi-bar-cupertino-4")),
    ], level="listing", flags=["Plate price not verified from an official source (reviews quote $2.25-$3.xx historically).", "Hours differ slightly between TripAdvisor (11:30 open weekdays) and Restaurant Guru (11:00)."],
    phone="(408) 861-0155", yelp_slug="kura-revolving-sushi-bar-cupertino-4", bus=CUP_NEAR)

add("Kong Tofu & BBQ", "Cupertino", "19626 Stevens Creek Blvd, Cupertino, CA 95014",
    "Stevens Creek Blvd", "Korean (tofu soup / BBQ)",
    "Tue-Sun; closed Mon", "11:30 AM - 2:00 PM, 5:00 PM - 8:00 PM",
    "Lunch service 11:30-2", [
        ("Yelp - Kong Tofu & BBQ (address, phone, closed Mon; Tue-Sun 11:30-2 & 5-8/8:30)", yelp("kong-tofu-and-bbq-cupertino-2")),
    ], flags=[NO_PRICE, "Lunch window ends 2:00 PM sharp."], phone="(408) 863-0234",
    yelp_slug="kong-tofu-and-bbq-cupertino-2", bus=CUP_BUS, sp_days="Tue-Sun", window="11:30 AM - 2:00 PM")

add("Taste Good Beijing Cuisine", "Cupertino", "20916 Homestead Rd Unit A, Cupertino, CA 95014",
    "Homestead Rd", "Chinese (Beijing)",
    "Daily", "10:30 AM - 2:00 PM, 4:30 PM - 9:00 PM",
    "Lunch service 10:30-2", [
        ("Yelp - Taste Good Beijing Cuisine Cupertino (address, phone, Sun-Thu 10:30-2 & 4:30-9, Fri-Sat to 2:30/9:30)", yelp("taste-good-beijing-cuisine-cupertino-cupertino")),
        ("Apple Maps listing (hours cross-check)", "https://maps.apple.com/place?place-id=IB7CF3417A41F7A03"),
    ], flags=[NO_PRICE, "Yelp rating 2.6 - reviews poor."], phone="(408) 320-2138",
    yelp_slug="taste-good-beijing-cuisine-cupertino-cupertino", bus=CUP_NEAR)

add("Special Noodle Soup", "Cupertino", "10275 S De Anza Blvd, Cupertino, CA 95014",
    "De Anza Blvd", "Chinese (noodle soup)",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Special Noodle Soup (address, phone, daily 11-9)", yelp("special-noodle-soup-cupertino")),
    ], flags=[NO_PRICE], phone="(408) 429-8866", yelp_slug="special-noodle-soup-cupertino", bus=CUP_BUS)

add("Liukoushui Chongqing Noodles", "Cupertino", "19052 Stevens Creek Blvd, Cupertino, CA 95014",
    "East Stevens Creek Blvd", "Chinese (Chongqing noodles)",
    "Daily", "11:00 AM - 2:00 PM, 4:30 PM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Liukoushui Chongqing Noodles (address, hours 11-2 & 4:30-9; Wed-Thu lunch to 2:30)", yelp("liukoushui-chongqing-noodles-cupertino")),
    ], flags=[NO_PRICE, "Unclaimed Yelp listing (31 reviews) - confirm hours."],
    yelp_slug="liukoushui-chongqing-noodles-cupertino", bus=CUP_BUS)

# ---------------------------------------------------------------- Sunnyvale
add("Tanto Japanese Restaurant", "Sunnyvale", "1063 E El Camino Real, Sunnyvale, CA 94087",
    "E El Camino Real", "Japanese (izakaya)",
    "Tue-Sun; lunch Tue-Fri", "11:30 AM - 1:00 PM, 5:30 PM - 9:00 PM",
    "Lunch sets", [
        ("Yelp - Tanto Sunnyvale (address, phone; lunch Tue-Fri 11:30-1)", yelp("tanto-japanese-restaurant-sunnyvale")),
    ], level="conflicting", flags=["Very short lunch window (last order ~1 PM) and listings disagree - call ahead.", NO_PRICE],
    phone="(408) 244-7311", yelp_slug="tanto-japanese-restaurant-sunnyvale",
    sp_days="Tue-Fri", window="11:30 AM - 1:00 PM")

add("Saravanaa Bhavan", "Sunnyvale", "1305 S Mary Ave, Sunnyvale, CA 94087",
    "S Mary Ave", "South Indian vegetarian",
    "Daily", "11:00 AM - 9:30 PM",
    "Lunch thali / combos", [
        ("Yelp - Saravanaa Bhavan Sunnyvale (address, phone)", yelp("saravanaa-bhavan-sunnyvale")),
        ("Official site - saravanaabhavan.us (locations)", "https://www.saravanaabhavan.us/"),
    ], flags=[NO_PRICE, "Tuesday hours transcribed from listing - confirm."], phone="(408) 616-7755",
    yelp_slug="saravanaa-bhavan-sunnyvale")

add("Madras Cafe", "Sunnyvale", "1177 W El Camino Real, Sunnyvale, CA 94087",
    "W El Camino Real", "South Indian vegetarian",
    "Daily", "8:30 AM - 10:00 PM",
    "No published lunch special (dosa/idli a la carte)", [
        ("Yelp - Madras Cafe Sunnyvale (address, phone, daily 8:30-10)", yelp("madras-cafe-sunnyvale")),
    ], flags=[NO_PRICE], phone="(408) 737-2323", yelp_slug="madras-cafe-sunnyvale")

add("Kabul Afghan Cuisine", "Sunnyvale", "351 W Washington Ave, Sunnyvale, CA 94086",
    "Downtown Sunnyvale", "Afghan",
    "Lunch Mon-Fri; dinner nightly", "11:30 AM - 2:00 PM, 5:00 PM - 9:00 PM",
    "Lunch menu Mon-Fri", [
        ("Yelp - Kabul Afghan Cuisine Sunnyvale (address, phone, lunch Mon-Fri 11:30-2)", yelp("kabul-afghan-cuisine-sunnyvale")),
        ("Official site", "https://www.kabulcuisine.com/"),
    ], flags=[NO_PRICE], phone="(408) 245-4350", yelp_slug="kabul-afghan-cuisine-sunnyvale",
    sp_days="Mon-Fri", window="11:30 AM - 2:00 PM")

add("Faultline Brewing Company", "Sunnyvale", "1235 Oakmead Pkwy, Sunnyvale, CA 94085",
    "Oakmead Pkwy (near Lawrence Expy)", "American brewpub",
    "Daily", "11:00 AM - 9:00 PM",
    "No lunch special (full menu from 11)", [
        ("Official site - faultlinebrewing.com (hours 11-9)", "https://www.faultlinebrewing.com/"),
        ("Yelp - Faultline Brewing Company", yelp("faultline-brewing-company-sunnyvale")),
    ], level="official", flags=["No discounted lunch item found - listed for hours only."],
    yelp_slug="faultline-brewing-company-sunnyvale")

add("Indian Tadka", "Sunnyvale", "1082 E El Camino Real #7, Sunnyvale, CA 94087",
    "E El Camino Real", "Indian",
    "Daily (Mon dinner only)", "11:30 AM - 2:00 PM, 5:00 PM - 9:30 PM",
    "Lunch special (starter + curry + biryani)", [
        ("Yelp - Indian Tadka (address, phone; Mon dinner only, Tue-Fri 11:30-2, Sat-Sun 11:30-2:30)", yelp("indian-tadka-sunnyvale")),
    ], flags=[NO_PRICE], phone="(408) 246-6000", yelp_slug="indian-tadka-sunnyvale",
    sp_days="Tue-Sun", window="11:30 AM - 2:00 PM")

add("California Momo Kitchen", "Sunnyvale", "913 E Duane Ave, Sunnyvale, CA 94085",
    "E Duane Ave", "Nepali / Himalayan",
    "Daily", "11:00 AM - 9:00 PM",
    "Lunch specials 11-3", [
        ("Yelp - California Momo Kitchen (address, phone, Mon-Thu 11-9, Fri 11-10, Sat 11:30-10, Sun 11:30-9)", yelp("california-momo-kitchen-sunnyvale")),
    ], flags=[NO_PRICE, "Lunch-special window (11-3) comes from a review, not the menu."],
    phone="(408) 743-5857", yelp_slug="california-momo-kitchen-sunnyvale", sp_days="Daily", window="11:00 AM - 3:00 PM")

add("Surmai", "Sunnyvale", "500 Lawrence Expy Ste C, Sunnyvale, CA 94085",
    "Lawrence Expy", "Indian (Maharashtrian coastal)",
    "Wed-Mon; closed Tue", "Closed Tuesdays",
    "Special Thali", [
        ("Yelp - Surmai (address, phone; closed Tue; Mon/Wed/Thu/Sun 11-9:30, Fri-Sat 11-10:30)", yelp("surmai-sunnyvale")),
    ], flags=["CLOSED on the trip date (Tuesday).", NO_PRICE], phone="(408) 736-2411",
    yelp_slug="surmai-sunnyvale", open_tue=False)

add("Seapot Hot Pot & KBBQ", "Sunnyvale", "740 E El Camino Real, Sunnyvale, CA 94087",
    "E El Camino Real", "Hot pot / Korean BBQ (AYCE)",
    "Daily", "11:00 AM - 3:00 PM, 5:00 PM - 10:00 PM",
    "Weekday Lunch Special (AYCE)", [
        ("Yelp - Seapot Hot Pot & KBBQ Sunnyvale (address, phone, hours; Yelp offer: Lunch Special M-F $23.99)", yelp("seapot-hot-pot-and-kbbq-sunnyvale")),
    ], phone="(408) 685-2268", yelp_slug="seapot-hot-pot-and-kbbq-sunnyvale",
    price_from=23.99, sp_days="Mon-Fri", window="11:00 AM - 3:00 PM",
    flags=["Price is from the business's Yelp offer banner - confirm current."])

add("Abhiruchi", "Sunnyvale", "893 E El Camino Real, Sunnyvale, CA 94087",
    "E El Camino Real", "South Indian (Andhra)",
    "Thu-Tue; closed Wed", "8:30 AM - 10:30 PM",
    "Lunch thali (after 11:30)", [
        ("Menupages - Abhiruchi (address, hours; closed Wed)", "https://menupages.com/abhiruchi/893-e-el-camino-real-sunnyvale"),
        ("Beyondmenu mirror (thali $17.99-$18.99)", "https://www.beyondmenu.com/abhiruchi-sunnyvale"),
    ], level="listing", price_from=17.99, price_to=18.99, sp_days="Thu-Tue", window="from 11:30 AM",
    yelp_slug="abhiruchi-sunnyvale", flags=["Prices from menu mirrors, not official site."])

add("Mom's Biryani", "Sunnyvale", "103 E Fremont Ave, Sunnyvale, CA 94087",
    "E Fremont Ave", "Indian (Hyderabadi biryani)",
    "Daily", "11:00 AM - 2:30 PM, 5:30 PM - 9:30 PM",
    "Lunch 11-2:30", [
        ("Official site - momsbiryanica.com (hours; ordering page, no lunch pricing readable)", "https://momsbiryanica.com/"),
        ("Yelp - Mom's Biryani Sunnyvale", yelp("moms-biryani-sunnyvale")),
    ], level="official", flags=[NO_PRICE], phone="(408) 680-9804", yelp_slug="moms-biryani-sunnyvale",
    sp_days="Daily", window="11:00 AM - 2:30 PM")

add("Dehaati", "Sunnyvale", "954 E El Camino Real, Sunnyvale, CA 94087",
    "E El Camino Real", "Indian (village-style)",
    "Tue-Sun; closed Mon", "11:30 AM - 3:00 PM, 5:30 PM - 9:30 PM",
    "Lunch service 11:30-3", [
        ("Yelp - Dehaati (address, phone, closed Mon; Tue-Sun 11:30-3 & 5:30-9:30)", yelp("dehaati-sunnyvale")),
    ], flags=[NO_PRICE], phone="(408) 685-2054", yelp_slug="dehaati-sunnyvale",
    sp_days="Tue-Sun", window="11:30 AM - 3:00 PM")

add("Delhiwala Chaat", "Sunnyvale", "590 Old San Francisco Rd, Sunnyvale, CA 94086",
    "Old San Francisco Rd", "Indian street food (veg)",
    "Tue-Sun; closed Mon", "11:00 AM - 9:00 PM",
    "No published lunch special (chaat a la carte)", [
        ("Yelp - Delhiwala Chaat (address, phone, closed Mon; Tue-Fri 11-9, Sat-Sun 10-9)", yelp("delhiwala-chaat-sunnyvale-8")),
    ], flags=[NO_PRICE], phone="(669) 224-8030", yelp_slug="delhiwala-chaat-sunnyvale-8")

add("Chelokababi Persian Cuisine", "Sunnyvale", "1236 S Wolfe Rd, Sunnyvale, CA 94086",
    "S Wolfe Rd", "Persian",
    "Tue-Sun (Tue dinner only)", "Dinner only (4:30 PM - 9:00 PM)",
    "Lunch Wed-Sun", [
        ("Yelp - Chelokababi (address, phone; Mon closed, Tue 4:30-9, Wed-Thu 11:30-9, Fri 11:30-9:30, Sat-Sun 12-9/9:30)", yelp("chelokababi-persian-cuisine-sunnyvale")),
    ], flags=["No lunch on Tuesday (dinner only).", NO_PRICE], phone="(408) 737-1222",
    yelp_slug="chelokababi-persian-cuisine-sunnyvale", sp_days="Wed-Sun", window="from 11:30 AM", open_tue=False)

add("Tao Tao Cafe", "Sunnyvale", "175 S Murphy Ave, Sunnyvale, CA 94086",
    "Downtown Sunnyvale (Murphy Ave)", "Chinese-American",
    "Tue-Sun; lunch Tue-Fri", "11:30 AM - 2:00 PM, 3:30 PM - 8:30 PM",
    "Lunch service Tue-Fri", [
        ("Yelp - Tao Tao Cafe (address, phone; closed Mon; Tue-Fri 11:30-2 & 3:30-8:30; Sat-Sun from 3 PM)", yelp("tao-tao-cafe-sunnyvale-2")),
        ("Restaurantji hours cross-check", "https://www.restaurantji.com/ca/sunnyvale/tao-tao-/"),
    ], flags=[NO_PRICE], phone="(408) 736-3731", yelp_slug="tao-tao-cafe-sunnyvale-2",
    sp_days="Tue-Fri", window="11:30 AM - 2:00 PM")

add("Garlic High", "Sunnyvale", "107 W Maude Ave, Sunnyvale, CA 94085",
    "W Maude Ave", "Japanese (garlic ramen)",
    "Tue-Sun; closed Mon", "11:30 AM - 1:30 PM, 5:30 PM - 8:30 PM",
    "Lunch ramen service", [
        ("Corner.inc listing (address, hours Tue-Fri 11:30-1:30 & 5:30-8:30)", "https://www.corner.inc/place/p8gQqaMsgu1K"),
        ("Yelp - Garlic High (older listing shows dinner-only hours)", yelp("garlic-high-sunnyvale")),
    ], level="conflicting", flags=["Yelp still shows dinner-only hours; Apple Maps/Corner show lunch 11:30-1:30 - call ahead.", NO_PRICE],
    phone="(408) 599-9475", yelp_slug="garlic-high-sunnyvale", sp_days="Tue-Sun", window="11:30 AM - 1:30 PM")

add("DL Brazuca", "Sunnyvale", "510 Lawrence Expy Ste 101, Sunnyvale, CA 94085",
    "Lawrence Expy", "Brazilian deli / bakery",
    "Mon-Sat; closed Sun", "9:00 AM - 5:00 PM",
    "Daily hot lunch plates (11:30-3)", [
        ("Yelp - DL Brazuca (address, phone, Mon-Fri 9-5, Sat 9-2/3, Sun closed)", yelp("dl-brazuca-sunnyvale-2")),
        ("Apple Maps listing (lunch service Mon-Fri 11:30-3)", "https://maps.apple.com/place?place-id=ID3919490360472E"),
    ], flags=[NO_PRICE], phone="(408) 836-8056", yelp_slug="dl-brazuca-sunnyvale-2",
    sp_days="Mon-Fri", window="11:30 AM - 3:00 PM")

# ---------------------------------------------------------------- Los Altos
add("Sumika", "Los Altos", "236 Central Plz, Los Altos, CA 94022",
    "Downtown Los Altos", "Japanese (yakitori)",
    "Daily", "11:30 AM - 2:00 PM, 5:30 PM - 9:00 PM",
    "Lunch bento", [
        ("Yelp - Sumika Los Altos (address, phone, lunch 11:30-2)", yelp("sumika-los-altos")),
        ("Official site - sumikagrill.com", "https://www.sumikagrill.com/"),
    ], flags=["$20 bento price is from a review, not the menu."], phone="(650) 917-1822",
    yelp_slug="sumika-los-altos", sp_days="Daily", window="11:30 AM - 2:00 PM")

add("Yoshi Sushi", "Los Altos", "250 3rd St, Los Altos, CA 94022",
    "Downtown Los Altos", "Japanese / Sushi",
    "Mon-Sat", "11:00 AM - 3:00 PM, 5:00 PM - 9:00 PM",
    "Weekday lunch bento / roll combos", [
        ("Yelp - Yoshi Sushi Los Altos (address, phone; lunch bento $15.99, 2-roll $12.99 / 3-roll $17.99)", yelp("yoshi-sushi-los-altos")),
        ("Official site (Los Altos menu page returned HTTP 500 at check time)", "https://www.yoshisushisanjose.com/"),
    ], phone="(650) 941-8150", yelp_slug="yoshi-sushi-los-altos",
    price_from=12.99, price_to=17.99, sp_days="Mon-Fri", window="11:00 AM - 3:00 PM",
    flags=["Official menu page was down when checked - prices from Yelp menu."])

add("Amber India", "Los Altos", "4926 El Camino Real, Los Altos, CA 94022",
    "El Camino Real", "Indian (upscale)",
    "Daily", "11:30 AM - 2:30 PM, 5:00 PM - 9:30 PM",
    "Weekend lunch buffet / weekday lunch meal box", [
        ("Official menu - amber-india.com Los Altos (buffet $27.99 Sat-Sun)", "https://www.amber-india.com/los-altos-menu"),
        ("Yelp - Amber India Los Altos (hours; 'Daily Fresh Lunch Meal Box 11-2' update)", yelp("amber-india-los-altos")),
    ], level="official", price_from=27.99, sp_days="Sat-Sun (buffet)", window="11:30 AM - 2:30 PM",
    flags=["Buffet is weekend-only; weekday lunch is a la carte / meal box (price not published)."],
    phone="(650) 968-7511", yelp_slug="amber-india-los-altos")

add("Sushiko", "Los Altos", "4546 El Camino Real Ste A4, Los Altos, CA 94022",
    "El Camino Real (Rancho Shopping Ctr area)", "Japanese / Sushi",
    "Mon-Sat; closed Sun", "11:30 AM - 2:00 PM, 4:00 PM - 8:30 PM",
    "Lunch bento", [
        ("Yelp - Sushiko Los Altos (address, phone, Mon-Sat 11:30-2 & 4-8:30, Sun closed)", yelp("sushiko-los-altos")),
    ], flags=[NO_PRICE], phone="(650) 559-9218", yelp_slug="sushiko-los-altos",
    sp_days="Mon-Sat", window="11:30 AM - 2:00 PM")

add("Pho Vi Hoa", "Los Altos", "4546 El Camino Real Ste A12, Los Altos, CA 94022",
    "El Camino Real", "Vietnamese (pho)",
    "Daily", "10:00 AM - 10:00 PM",
    "No published lunch special", [
        ("TripAdvisor - Pho Vi Hoa (address, phone, daily 10-10)", "https://www.tripadvisor.com/Restaurants-g32653-Los_Altos_California.html"),
        ("Yelp - Pho Vi Hoa Los Altos", yelp("pho-vi-hoa-los-altos")),
    ], level="listing", flags=[NO_PRICE], phone="(650) 947-1290", yelp_slug="pho-vi-hoa-los-altos")

# ---------------------------------------------------------------- Mountain View
add("Bloom & Vine", "Mountain View", "110 Castro St, Mountain View, CA 94041",
    "Castro St", "Vietnamese-fusion / wine bar",
    "Tue-Sun; closed Mon", "11:00 AM - 2:30 PM, dinner",
    "Lunch special (main + soup or side)", [
        ("Yelp - Bloom & Vine (address, phone, Tue-Sun 11-2:30; reviews describe lunch special with soup/side)", yelp("bloom-and-vine-mountain-view")),
    ], flags=[NO_PRICE, "Same address as former Xanh - appears to have replaced it."],
    phone="(669) 261-1677", yelp_slug="bloom-and-vine-mountain-view", sp_days="Tue-Sun", window="11:00 AM - 2:30 PM")

add("Bonchon", "Mountain View", "260 Castro St, Mountain View, CA 94041",
    "Castro St", "Korean fried chicken",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special (lunch combos vary by store)", [
        ("Yelp - Bonchon Mountain View (address, phone, daily 11-9)", yelp("bonchon-mountain-view")),
        ("Official locator (MV page unavailable at check time)", "https://locations.bonchon.com/"),
    ], flags=[NO_PRICE, "Separate from the Sunnyvale Bonchon already listed."],
    phone="(650) 282-5633", yelp_slug="bonchon-mountain-view")

add("Shalimar Sizzle", "Mountain View", "246 Castro St, Mountain View, CA 94041",
    "Castro St", "Indian / Pakistani",
    "Daily", "11:00 AM - 11:00 PM",
    "No published lunch special", [
        ("Yelp - Shalimar Sizzle (address, daily 11-11)", yelp("shalimar-sizzle-mountain-view")),
    ], flags=[NO_PRICE], yelp_slug="shalimar-sizzle-mountain-view")

add("Amarin Thai Cuisine", "Mountain View", "147 Castro St, Mountain View, CA 94041",
    "Castro St", "Thai",
    "Daily", "11:30 AM - 2:30 PM, 5:00 PM - 9:00 PM",
    "Lunch service 11:30-2:30", [
        ("Yelp - Amarin Thai Cuisine (147 Castro; Mon-Fri 11:30-2:30 & 5-9, Sat-Sun 12-3)", yelp("amarin-thai-cuisine-mountain-view-3")),
    ], flags=[NO_PRICE, "Relocated from 174 Castro (old listing marked CLOSED) - use 147 Castro."],
    phone="(650) 282-5434", yelp_slug="amarin-thai-cuisine-mountain-view-3", sp_days="Mon-Fri", window="11:30 AM - 2:30 PM")

add("Das Bierhauz", "Mountain View", "135 Castro St, Mountain View, CA 94041",
    "Castro St", "German beer garden",
    "Daily", "11:00 AM - 10:00 PM",
    "No lunch special (full menu from 11)", [
        ("Yelp - Das Bierhauz Mountain View (address, phone, Mon-Thu 11-10, Fri 11-11, Sat 9-11, Sun 9-10)", yelp("das-bierhauz-mountain-view-mountain-view-2")),
    ], flags=["Not to be confused with the closed 'Bierhaus' at 383 Castro.", NO_PRICE],
    phone="(650) 336-7613", yelp_slug="das-bierhauz-mountain-view-mountain-view-2")

add("Hyderabad Dum Biryani", "Mountain View", "2105 Old Middlefield Way Ste C, Mountain View, CA 94043",
    "Old Middlefield Way", "Indian (Hyderabadi, halal)",
    "Daily", "11:00 AM - 10:00 PM",
    "Lunch combos", [
        ("Yelp - Hyderabad Dum Biryani Mountain View (address, phone, daily 11-10/10:30)", yelp("hyderabad-dum-biryani-mountain-view-6")),
    ], flags=[NO_PRICE], phone="(650) 386-1725", yelp_slug="hyderabad-dum-biryani-mountain-view-6")

add("Masa Sushi Japan", "Mountain View", "650 Castro St Ste 180, Mountain View, CA 94041",
    "Castro St", "Japanese / Sushi",
    "Mon-Sat; closed Sun", "11:00 AM - 1:30 PM, 4:30 PM - 8:00 PM",
    "Lunch service 11-1:30", [
        ("Yelp - Masa Sushi Japan (address, phone, Mon-Fri 11-1:30, Sat 11:30-2, Sun closed)", yelp("masa-sushi-japan-mountain-view")),
    ], flags=[NO_PRICE, "Lunch ends 1:30 PM."], phone="(650) 282-5204",
    yelp_slug="masa-sushi-japan-mountain-view", sp_days="Mon-Sat", window="11:00 AM - 1:30 PM")

add("Himalayan Kitchen", "Mountain View", "820 E El Camino Real Ste C, Mountain View, CA 94040",
    "E El Camino Real", "Indian / Nepalese",
    "Daily", "11:00 AM - 3:00 PM, 5:00 PM - 10:00 PM",
    "Lunch buffet", [
        ("Yelp - Himalayan Kitchen (address, phone, daily 11-3 & 5-10; Q&A: buffet Fri-Sun $24.99)", yelp("himalayan-kitchen-mountain-view")),
    ], level="conflicting", flags=["Owner text says 'every day lunch buffet' but Q&A says Fri-Sun only at $24.99 - confirm."],
    phone="(650) 967-4240", yelp_slug="himalayan-kitchen-mountain-view",
    price_from=24.99, sp_days="Fri-Sun (per Q&A)", window="11:00 AM - 3:00 PM")

add("Los Altos Taqueria", "Mountain View", "2105 Old Middlefield Way Ste E, Mountain View, CA 94043",
    "Old Middlefield Way", "Mexican taqueria",
    "Daily", "7:00 AM - 10:00 PM",
    "No published lunch special", [
        ("Yelp - Los Altos Taqueria (address, daily 7-10)", yelp("los-altos-taqueria-mexican-mountain-view")),
        ("Netwaiter ordering page (phone, hours 7:30-10)", "https://losaltostaqueria.netwaiter.com/mountain-view/"),
    ], flags=[NO_PRICE, "Open time differs (7:00 Yelp vs 7:30 ordering site)."], phone="(650) 965-7236",
    yelp_slug="los-altos-taqueria-mexican-mountain-view")

add("Chili's", "Mountain View", "2560 W El Camino Real, Mountain View, CA 94040",
    "W El Camino Real", "American / Tex-Mex chain",
    "Daily", "11:00 AM - 10:00 PM",
    "3 For Me lunch combo", [
        ("Yelp - Chili's Mountain View (address, phone, Mon-Thu 11-10, Fri-Sat 11-11, Sun 11-10)", yelp("chilis-mountain-view-2")),
        ("Chili's official - 3 For Me", "https://www.chilis.com/menu/3-for-me"),
    ], flags=["3 For Me price varies by location (third-party sites quote from $10.99) - not verified for this store.", "Yelp rating 2.8."],
    phone="(650) 941-2227", yelp_slug="chilis-mountain-view-2", sp_days="Daily", window="All day")

# ---------------------------------------------------------------- Santa Clara
add("Pedro's Restaurant & Cantina", "Santa Clara", "3935 Freedom Cir, Santa Clara, CA 95054",
    "Freedom Circle (near Great America)", "Mexican",
    "Mon-Fri lunch & dinner", "11:00 AM - 10:00 PM",
    "Luncheon specials 11-2", [
        ("Yelp - Pedro's Santa Clara (address, phone, Mon-Fri 11-10)", yelp("pedros-restaurant-and-cantina-santa-clara")),
        ("Official site (Santa Clara menu page returned 404 at check time)", "https://www.pedrosrestaurants.com/"),
    ], flags=[NO_PRICE, "Official menu page 404 - lunch specials unconfirmed for 2026."],
    phone="(408) 496-6777", yelp_slug="pedros-restaurant-and-cantina-santa-clara", sp_days="Mon-Fri", window="11:00 AM - 2:00 PM")

add("Happy Sushi", "Santa Clara", "3216 El Camino Real Ste 5, Santa Clara, CA 95051",
    "El Camino Real", "Japanese / Korean",
    "Daily", "10:30 AM - 2:30 PM, 4:30 PM - 9:00 PM",
    "Lunch bento / rolls", [
        ("Official site - happysushimenu.com (address, hours)", "https://www.happysushimenu.com/"),
        ("Yelp - Happy Sushi Santa Clara (hours cross-check)", yelp("happy-sushi-santa-clara-2")),
    ], level="official", flags=[NO_PRICE], phone="(408) 638-7606", yelp_slug="happy-sushi-santa-clara-2",
    sp_days="Daily", window="10:30 AM - 2:30 PM")

add("Sushi O Sushi", "Santa Clara", "2789 El Camino Real, Santa Clara, CA 95051",
    "El Camino Real", "Japanese / Sushi",
    "Daily", "11:30 AM - 2:00 PM, 5:00 PM - 9:00 PM",
    "Lunch service 11:30-2", [
        ("Yelp - Sushi O Sushi (address, phone, Mon-Sat 11:30-2 & 5-9/9:30, Sun 12-2:30)", yelp("sushi-o-sushi-santa-clara-2")),
        ("Official site", "https://www.sushiosushi.com/"),
    ], flags=[NO_PRICE], phone="(408) 241-1677", yelp_slug="sushi-o-sushi-santa-clara-2",
    sp_days="Daily", window="11:30 AM - 2:00 PM")

add("Kobe Japanese Restaurant", "Santa Clara", "2086 El Camino Real, Santa Clara, CA 95050",
    "El Camino Real", "Japanese / Sushi",
    "Daily (Sun dinner only)", "11:00 AM - 2:00 PM, 4:00 PM - 9:00 PM",
    "Lunch service 11-2", [
        ("Yelp - Kobe Japanese Restaurant (address, phone, Mon-Sat 11-2 & 4-9, Sun 4-9)", yelp("kobe-japanese-restaurant-santa-clara")),
    ], flags=[NO_PRICE, "Yelp rating 2.8, unclaimed listing."], phone="(408) 984-5623",
    yelp_slug="kobe-japanese-restaurant-santa-clara", sp_days="Mon-Sat", window="11:00 AM - 2:00 PM")

add("Mio Vicino", "Santa Clara", "1290 Benton St, Santa Clara, CA 95050",
    "Benton St (Old Quad)", "Italian",
    "Daily; lunch Tue-Fri", "11:00 AM - 2:00 PM, 5:00 PM - 9:00 PM",
    "Lunch service Tue-Fri", [
        ("Yelp - Mio Vicino (address, phone; Mon 5-9, Tue-Fri 11-2 & 5-9, Sat-Sun 4:30-9)", yelp("mio-vicino-santa-clara")),
    ], flags=[NO_PRICE], phone="(408) 241-9414", yelp_slug="mio-vicino-santa-clara",
    sp_days="Tue-Fri", window="11:00 AM - 2:00 PM")

add("Thai Chili Cuisine", "Santa Clara", "1550 Halford Ave, Santa Clara, CA 95051",
    "Halford Ave", "Thai",
    "Daily (Sat dinner only)", "11:00 AM - 1:30 PM, 5:00 PM - 8:30 PM",
    "Lunch combo (with tom yum soup + veggie roll)", [
        ("Yelp - Thai Chili Cuisine (address, phone; lunch 11-1:30 Mon-Wed/Fri/Sun; business update: lunch combo includes soup & roll)", yelp("thai-chili-cuisine-santa-clara-3")),
    ], flags=[NO_PRICE, "Lunch ends 1:30 PM; Yelp shows an obviously wrong 'open 24 hours' for Thursday."],
    phone="(408) 615-9199", yelp_slug="thai-chili-cuisine-santa-clara-3", sp_days="Mon-Fri, Sun", window="11:00 AM - 1:30 PM",
    includes="Tom yum veggie soup + veggie roll per business update.")

add("Home Kitchen Vietnamese Cuisine", "Santa Clara", "1045 Monroe St, Santa Clara, CA 95050",
    "Monroe St (Old Quad)", "Vietnamese",
    "Tue-Sat; closed Sun-Mon", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Home Kitchen Vietnamese Cuisine (address, phone, Tue-Sat 11-9)", yelp("home-kitchen-vietnamese-cuisine-santa-clara")),
    ], flags=[NO_PRICE], phone="(408) 557-9923", yelp_slug="home-kitchen-vietnamese-cuisine-santa-clara")

add("Tai Er Sichuan Cuisine", "Santa Clara", "2855 Stevens Creek Blvd Unit A268, Santa Clara, CA 95050",
    "Westfield Valley Fair", "Sichuan (pickled-fish)",
    "Daily", "11:00 AM - 9:30 PM",
    "No published lunch special", [
        ("Yelp - Tai Er Sichuan Cuisine (address, phone, Sun-Thu 11-9:30, Fri-Sat 11-10:30)", yelp("tai-er-sichuan-cuisine-santa-clara")),
    ], flags=[NO_PRICE], phone="(408) 528-2222", yelp_slug="tai-er-sichuan-cuisine-santa-clara")

add("Pho Van", "Santa Clara", "1555 Laurelwood Rd, Santa Clara, CA 95054",
    "Laurelwood Rd (office park)", "Vietnamese (pho)",
    "Daily", "10:00 AM - 6:00 PM",
    "No published lunch special ($ price tier)", [
        ("Yelp - Pho Van (address, phone; Mon-Fri 10-6, Sat 10:30-6, Sun 10-6)", yelp("pho-van-santa-clara")),
    ], flags=[NO_PRICE, "Older Yelp snapshot shows Sat closed - confirm weekend."], phone="(408) 567-9225",
    yelp_slug="pho-van-santa-clara")

# ---------------------------------------------------------------- Los Gatos
add("Pedro's Cocina", "Los Gatos", "316 N Santa Cruz Ave, Los Gatos, CA 95030",
    "Downtown Los Gatos", "Mexican",
    "Daily", "11:00 AM - 9:00 PM",
    "Lunch menu", [
        ("Yelp - Pedro's Los Gatos (address, phone)", yelp("pedros-restaurant-and-cantina-los-gatos")),
        ("Official site", "https://www.pedrosrestaurants.com/"),
    ], flags=[NO_PRICE, "Tuesday hours transcribed from listing - confirm."], phone="(408) 354-7570",
    yelp_slug="pedros-restaurant-and-cantina-los-gatos")

add("Opelia", "Los Gatos", "25 E Main St, Los Gatos, CA 95030",
    "Downtown Los Gatos", "Mediterranean / Turkish",
    "Daily", "11:00 AM - 2:00 PM, 5:00 PM - 10:00 PM",
    "Lunch service 11-2", [
        ("Yelp - Opelia (address, phone, daily 11-2 & 5-10/12)", yelp("opelia-los-gatos")),
        ("Official site", "https://www.opelia.com/"),
    ], flags=[NO_PRICE], phone="(408) 827-4215", yelp_slug="opelia-los-gatos", sp_days="Daily", window="11:00 AM - 2:00 PM")

add("Yokohama", "Los Gatos", "336 N Santa Cruz Ave, Los Gatos, CA 95030",
    "Downtown Los Gatos", "Japanese / Sushi",
    "Tue-Sun; closed Mon", "11:30 AM - 2:00 PM, 5:00 PM - 9:00 PM",
    "Lunch specials", [
        ("Yelp - Yokohama Los Gatos (address, phone; closed Mon; Tue-Sat 11:30-2 & 5-9/9:30; Sun 4:30-9)", yelp("yokohama-los-gatos")),
    ], flags=[NO_PRICE, "Earlier pass rejected this as dinner-only from a Yelp index snippet; the business page shows lunch Tue-Sat 11:30-2, so the rejection is superseded."], phone="(408) 395-1990", yelp_slug="yokohama-los-gatos", sp_days="Tue-Sat", window="11:30 AM - 2:00 PM")
rows[-1]["supersedes_rejection"] = "Yelp business page shows Tue-Sat lunch 11:30 AM - 2:00 PM (earlier 'dinner-only' came from a search-index snippet)."

add("Kamakura Japanese Restaurant", "Los Gatos", "135 N Santa Cruz Ave, Los Gatos, CA 95030",
    "Downtown Los Gatos", "Japanese / Sushi",
    "Daily", "11:30 AM - 2:30 PM, 4:30 PM - 9:00 PM",
    "Lunch service 11:30-2:30", [
        ("Yelp - Kamakura (address, phone, Mon-Fri 11:30-2:30 & 4:30-9, Sat-Sun 11:30-9/9:30)", yelp("kamakura-japanese-restaurant-los-gatos")),
    ], flags=[NO_PRICE, "Unclaimed Yelp listing."], phone="(408) 395-6650",
    yelp_slug="kamakura-japanese-restaurant-los-gatos", sp_days="Daily", window="11:30 AM - 2:30 PM")

add("Hanna Asian Noodle Bar - Downtown", "Los Gatos", "155 N Santa Cruz Ave Ste A, Los Gatos, CA 95030",
    "Downtown Los Gatos", "Vietnamese / Asian noodles",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Hanna Asian Noodle Bar Downtown (address, phone, daily 11-9)", yelp("hanna-asian-noodle-bar-downtown-los-gatos")),
        ("Official site", "https://www.hannanoodlebar.com/"),
    ], flags=[NO_PRICE], phone="(408) 442-5172", yelp_slug="hanna-asian-noodle-bar-downtown-los-gatos")

add("Aldo's Ristorante & Bar", "Los Gatos", "14109 Winchester Blvd, Los Gatos, CA 95032",
    "Winchester Blvd", "Italian",
    "Daily; lunch Mon-Fri", "11:00 AM - 2:00 PM, 5:00 PM - 9:00 PM",
    "Lunch Mon-Fri 11-2", [
        ("Official site - aldos-ristorante.com (lunch Mon-Fri 11-2; dinner nightly 5-9)", "https://www.aldos-ristorante.com/"),
        ("Yelp - Aldo's Ristorante & Bar (hours cross-check)", yelp("aldos-ristorante-and-bar-los-gatos")),
    ], level="official", flags=[NO_PRICE], phone="(408) 374-1808", yelp_slug="aldos-ristorante-and-bar-los-gatos",
    sp_days="Mon-Fri", window="11:00 AM - 2:00 PM")

add("Zona Rosa", "Los Gatos", "81 W Main St, Los Gatos, CA 95030",
    "Downtown Los Gatos", "Mexican",
    "Tue-Sun; closed Mon", "11:30 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Zona Rosa (address, phone; closed Mon; Tue-Thu 11:30-9, Fri 11:30-9:30, Sat 10:30-9:30, Sun 11-9)", yelp("zona-rosa-los-gatos")),
    ], flags=[NO_PRICE], phone="(408) 884-8268", yelp_slug="zona-rosa-los-gatos")

# ---------------------------------------------------------------- Campbell
add("Blue Sky Chinese Restaurant", "Campbell", "2028 Winchester Blvd, Campbell, CA 95008",
    "Winchester Blvd", "Chinese-American",
    "Daily", "11:00 AM - 9:30 PM",
    "Lunch special combos / lunch rice plates", [
        ("Allmenus - Blue Sky (lunch combos $11.95-$13.95, rice plates $10.50-$10.95; older menu)", "https://www.allmenus.com/ca/campbell/19712-blue-sky-restaurant/menu/"),
        ("Placejoys menu mirror (Lunch Special $15.95, rice plates $14.95-$16.95; newer)", "https://blue-sky.placejoys.com/menu"),
        ("Yelp - Blue Sky Chinese Restaurant (address, phone, daily 11-9:30; photo notes no soup/salad included)", yelp("blue-sky-chinese-restaurant-campbell")),
    ], level="conflicting", flags=["Two menu mirrors disagree ($11.95 vs $15.95 combos) - newer mirror likely current."],
    phone="(408) 378-0424", yelp_slug="blue-sky-chinese-restaurant-campbell",
    price_from=14.95, price_to=16.95, sp_days="Daily", window="Lunch")

add("Best Taste Chinese Restaurant", "Campbell", "2360 S Bascom Ave Ste A, Campbell, CA 95008",
    "S Bascom Ave", "Chinese / sushi",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Best Taste Chinese Restaurant (address, phone, daily 11-9)", yelp("best-taste-chinese-restaurant-campbell-2")),
    ], flags=[NO_PRICE, "Older Yelp listing shows Sun opening 4 PM."], phone="(408) 377-7666",
    yelp_slug="best-taste-chinese-restaurant-campbell-2")

add("Sushi Confidential (Campbell)", "Campbell", "247 E Campbell Ave, Campbell, CA 95008",
    "Downtown Campbell", "Japanese / Sushi",
    "Daily", "11:30 AM - 9:00 PM",
    "Lunch specials (see Willow Glen row for chain pricing)", [
        ("Yelp - Sushi Confidential Campbell (address, phone, Sun-Thu 11:30-9, Fri-Sat 11:30-11)", yelp("sushi-confidential-campbell-campbell")),
        ("Official site", "https://www.sushiconfidential.com/"),
    ], flags=["Price not verified for this branch.", "Earlier pass rejected for lack of a street address; Yelp now supplies 247 E Campbell Ave."], phone="(408) 596-5554",
    yelp_slug="sushi-confidential-campbell-campbell")
rows[-1]["supersedes_rejection"] = "Street address (247 E Campbell Ave) now verified on Yelp."

add("Thai Orchid", "Campbell", "866 E Campbell Ave, Campbell, CA 95008",
    "E Campbell Ave", "Thai",
    "Tue-Sat; closed Sun-Mon", "11:00 AM - 2:00 PM, 4:30 PM - 9:30 PM",
    "Lunch Tue-Fri 11-2", [
        ("Yelp - Thai Orchid Campbell (address, phone; closed Sun-Mon; Tue-Fri 11-2 & 4:30-9:30; Sat dinner only)", yelp("thai-orchid-campbell")),
        ("Official site", "https://www.eatthaiorchid.com/"),
    ], flags=[NO_PRICE], phone="(408) 626-9779", yelp_slug="thai-orchid-campbell",
    sp_days="Tue-Fri", window="11:00 AM - 2:00 PM")

add("Thaibodia Bistro - Campbell", "Campbell", "2200 S Bascom Ave, Campbell, CA 95008",
    "S Bascom Ave", "Thai / Cambodian",
    "Daily", "11:00 AM - 9:30 PM",
    "No published lunch special", [
        ("Yelp - Thaibodia Bistro Campbell (address, phone, Mon-Thu 11-9:30, Fri-Sun 11-10)", yelp("thaibodia-bistro-campbell-campbell-2")),
        ("Official site", "https://www.thaibodia.com/"),
    ], flags=[NO_PRICE], phone="(408) 879-9215", yelp_slug="thaibodia-bistro-campbell-campbell-2")

add("Hinodeya Ramen Bar", "Campbell", "2210 S Bascom Ave, Campbell, CA 95008",
    "S Bascom Ave", "Japanese (ramen)",
    "Daily", "11:00 AM - 12:00 AM",
    "No published lunch special", [
        ("Yelp - Hinodeya Ramen Bar Campbell (address, phone, daily 11 AM-midnight)", yelp("hinodeya-ramen-bar-campbell")),
    ], flags=[NO_PRICE], phone="(408) 744-2155", yelp_slug="hinodeya-ramen-bar-campbell")

add("Sultan's Kebab", "Campbell", "278 E Campbell Ave, Campbell, CA 95008",
    "Downtown Campbell", "Turkish / Mediterranean",
    "Daily", "10:00 AM - 10:00 PM",
    "No published lunch special (kebab plates)", [
        ("Yelp - Sultan's Kebab Campbell (address, phone, daily 10-10)", yelp("sultans-kebab-campbell-2")),
    ], flags=[NO_PRICE], phone="(408) 628-4333", yelp_slug="sultans-kebab-campbell-2")

add("Casa Lupe Restaurant", "Campbell", "2165 Winchester Blvd, Campbell, CA 95008",
    "Winchester Blvd", "Mexican",
    "Mon-Sat; closed Sun", "11:00 AM - 2:30 PM, 5:00 PM - 9:00 PM",
    "Lunch service 11-2:30", [
        ("Yelp - Casa Lupe Restaurant Campbell (address, phone; Mon-Sat 11-2:30 & 5-9, Sun closed)", yelp("casa-lupe-restaurant-campbell")),
    ], flags=[NO_PRICE, "Older snapshots show 11:30 open and Mon dinner-only - confirm.", "Separate from Casa Lupe Mountain View already listed."],
    phone="(408) 378-1277", yelp_slug="casa-lupe-restaurant-campbell", sp_days="Mon-Sat", window="11:00 AM - 2:30 PM")

add("Aqui Cal-Mex", "Campbell", "201 E Campbell Ave, Campbell, CA 95008",
    "Downtown Campbell", "Cal-Mex",
    "Daily", "11:00 AM - 9:00 PM",
    "Chef's lunch specials & daily soups", [
        ("Yelp - Aqui Cal-Mex Campbell (address, phone, Sun-Thu 11-9, Fri-Sat 11-9:30; business text: chef's lunch specials)", yelp("aqui-cal-mex-campbell")),
    ], flags=[NO_PRICE, "Separate from the Cupertino Aqui already listed."], phone="(408) 374-2784",
    yelp_slug="aqui-cal-mex-campbell", sp_days="Daily", window="Lunch")

# ---------------------------------------------------------------- Saratoga
add("Anchors Fish & Chips", "Saratoga", "14441 Big Basin Way, Saratoga, CA 95070",
    "Saratoga Village", "Fish & chips / seafood",
    "Daily", "11:00 AM - 9:00 PM",
    "Fish & chips", [
        ("Yelp - Anchors Fish & Chips (address, phone, Mon-Thu 11-9, Fri-Sat 11-9:30; photos: fish 'n chips $19, Baja tacos $18, menu 5/2026)", yelp("anchors-fish-and-chips-saratoga")),
        ("Saratoga Chamber restaurant list (hours)", "https://www.saratogachamber.org/restaurants"),
        ("Menupix mirror (fish & chips $17 - older)", "https://www.menupix.com/sanjose/restaurants/32160423/Anchors-Fish-and-Chips-and-Seafood-Grill-Saratoga-CA"),
    ], level="conflicting", flags=["Price $17 (menupix) vs $19 (Yelp photo dated 5/2026) - newer used.", "Unclaimed Yelp listing."],
    phone="(408) 647-2783", yelp_slug="anchors-fish-and-chips-saratoga",
    price_from=19.0, sp_days="Daily", window="All day")

# ---------------------------------------------------------------- Palo Alto
add("Buca di Beppo Italian Restaurant", "Palo Alto", "643 Emerson St, Palo Alto, CA 94301",
    "Downtown Palo Alto", "Italian (family style)",
    "Daily", "11:00 AM - 9:30 PM",
    "Lunch Combos (Mon-Fri until 3 PM)", [
        ("Official location page - dineatbuca.com Palo Alto (hours; Lunch Combos Mon-Fri until 3 PM, includes side salad & garlic bread)", "https://dineatbuca.com/locations/palo-alto/"),
        ("Yelp - Buca di Beppo Palo Alto (hours cross-check)", yelp("buca-di-beppo-italian-restaurant-palo-alto-2")),
    ], level="official", flags=["Combo price not shown on the location page.", "Separate from the Campbell Buca already listed."],
    phone="(650) 329-0665", yelp_slug="buca-di-beppo-italian-restaurant-palo-alto-2",
    sp_days="Mon-Fri", window="Open - 3:00 PM", includes="Side salad and garlic bread.")

add("Sushi House", "Palo Alto", "855 El Camino Real Ste 158, Palo Alto, CA 94301",
    "Town & Country Village", "Japanese / Sushi",
    "Daily", "11:00 AM - 2:00 PM, 4:30 PM - 8:00 PM",
    "Lunch bento", [
        ("Yelp - Sushi House Palo Alto (address, phone, daily 11-2 & 4:30-8/8:30)", yelp("sushi-house-palo-alto")),
        ("Restaurant Guru hours cross-check", "https://restaurantguru.com/Sushi-House-Palo-Alto"),
    ], flags=[NO_PRICE], phone="(650) 321-3453", yelp_slug="sushi-house-palo-alto", sp_days="Daily", window="11:00 AM - 2:00 PM")

add("Vino Locale", "Palo Alto", "431 Kipling St, Palo Alto, CA 94301",
    "Downtown Palo Alto", "New American / wine bar",
    "Tue-Sat; closed Sun-Mon", "11:30 AM - 2:30 PM, 3:30 PM - 9:00 PM",
    "Casual self-order lunch (menu from $9)", [
        ("Yelp - Vino Locale (address, phone; owner text: Tue-Sat 11:30-2:30 lunch, menu starts from $9)", yelp("vino-locale-palo-alto")),
    ], flags=["'From $9' is the owner's Yelp blurb, not a current menu.", "One Yelp snapshot shows lunch ending 2:00 and no Sat lunch - confirm."],
    level="conflicting", phone="(650) 328-0450", yelp_slug="vino-locale-palo-alto",
    price_from=9.0, sp_days="Tue-Sat", window="11:30 AM - 2:30 PM")

add("Thaiphoon", "Palo Alto", "543 Emerson St, Palo Alto, CA 94301",
    "Downtown Palo Alto", "Thai",
    "Daily; lunch Mon-Fri", "11:00 AM - 2:30 PM, 4:00 PM - 9:00 PM",
    "Lunch Mon-Fri 11-2:30", [
        ("Yelp - Thaiphoon (address, phone; Mon-Fri 11-2:30 & 4-9/10; Sat-Sun dinner only)", yelp("thaiphoon-palo-alto")),
    ], flags=[NO_PRICE], phone="(650) 323-7700", yelp_slug="thaiphoon-palo-alto",
    sp_days="Mon-Fri", window="11:00 AM - 2:30 PM")

add("Hong Kong Restaurant", "Palo Alto", "3691 El Camino Real, Palo Alto, CA 94306",
    "S El Camino Real", "Cantonese / seafood",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Hong Kong Restaurant Palo Alto (address, phone, daily 11-9)", yelp("hong-kong-restaurant-palo-alto")),
    ], flags=[NO_PRICE], phone="(650) 251-9062", yelp_slug="hong-kong-restaurant-palo-alto")

add("Darbar Indian Cuisine", "Palo Alto", "129 Lytton Ave, Palo Alto, CA 94301",
    "Downtown Palo Alto", "Indian",
    "Daily (Sun dinner only)", "11:00 AM - 2:30 PM, 5:00 PM - 9:30 PM",
    "Weekday lunch buffet", [
        ("Yelp - Darbar Indian Cuisine (address, phone; business text: lunch buffet Mon-Fri 11-2:30)", yelp("darbar-indian-cuisine-palo-alto")),
    ], flags=["Buffet price not published."], phone="(650) 407-1154", yelp_slug="darbar-indian-cuisine-palo-alto",
    sp_days="Mon-Fri", window="11:00 AM - 2:30 PM", includes="~two dozen dishes incl. 4 veg + 4 meat entrees (per business description).")

add("Khazana", "Palo Alto", "339 University Ave, Palo Alto, CA 94301",
    "Downtown Palo Alto", "Indian (small plates)",
    "Daily; lunch Wed-Sun", "Dinner only (5:00 PM - 9:00 PM)",
    "Lunch Wed-Sun", [
        ("Yelp - Khazana (address, phone; Mon-Tue dinner only; Wed-Thu 11:30-2; Fri 11:30-2:30; Sat-Sun 12-2:30)", yelp("khazana-palo-alto")),
    ], flags=["No lunch on Tuesday.", NO_PRICE, "Unclaimed Yelp listing."], phone="(650) 384-6411",
    yelp_slug="khazana-palo-alto", sp_days="Wed-Sun", window="11:30 AM - 2:00 PM", open_tue=False)

# ---------------------------------------------------------------- Milpitas
add("Jun Bistro", "Milpitas", "290 Barber Ct, Milpitas, CA 95035",
    "Barber Ct (near Great Mall)", "Chinese (Yunnan)",
    "Tue-Sun; closed Mon", "11:30 AM - 2:30 PM, 5:00 PM - 9:00 PM",
    "Lunch special", [
        ("Metro Silicon Valley - Jun Bistro (open Tue-Sun 11:30-2:30 & 5-9; address; May 2026)", "https://www.metrosiliconvalley.com/jun-bistro-explores-yunnan-cuisine-in-milpitas/"),
        ("Yelp - Jun Bistro (4.7 stars; reviews cite lunch special)", yelp("jun-bistro-milpitas")),
    ], flags=[NO_PRICE, "Phone differs between listings ((669) 629-0965 vs (650) 963-3408)."],
    phone="(669) 629-0965", yelp_slug="jun-bistro-milpitas", sp_days="Tue-Sun", window="11:30 AM - 2:30 PM")

add("Yuan Bistro", "Milpitas", "42 Dixon Rd, Milpitas, CA 95035",
    "Dixon Rd", "Chinese",
    "Daily", "11:00 AM - 2:30 PM, 5:00 PM - 9:00 PM",
    "Lunch service 11-2:30", [
        ("Yelp - Yuan Bistro (address, phone, Mon-Fri 11-2:30 & 5-9, Sat-Sun 11-9)", yelp("yuan-bistro-milpitas")),
    ], flags=[NO_PRICE], phone="(408) 956-9051", yelp_slug="yuan-bistro-milpitas", sp_days="Mon-Fri", window="11:00 AM - 2:30 PM")

add("Daeho Kalbi Jjim & Beef Soup", "Milpitas", "217 W Calaveras Blvd, Milpitas, CA 95035",
    "W Calaveras Blvd", "Korean (braised short rib / soups)",
    "Daily", "11:00 AM - 2:30 PM, 4:30 PM - 9:00 PM",
    "Lunch special (per reviews)", [
        ("Yelp - Daeho Kalbi Jjim & Beef Soup (address, phone, Mon-Fri 11-2:30 & 4:30-9; reviews cite lunch special)", yelp("daeho-kalbi-jjim-and-beef-soup-milpitas")),
        ("Menu mirror (Sat-Sun 10:30-9; kalbi jjim $76-$101 - not lunch pricing)", "https://daeho-kalbi-jjim-beef-soup.goto-restaurants.com/"),
    ], flags=["Lunch special price not published; signature kalbi jjim is $76+ (shared)."],
    phone="(408) 770-3778", yelp_slug="daeho-kalbi-jjim-and-beef-soup-milpitas", sp_days="Mon-Fri", window="11:00 AM - 2:30 PM")

add("Siam Station", "Milpitas", "210 Barber Ct, Milpitas, CA 95035",
    "Barber Ct (near Great Mall)", "Thai",
    "Daily", "11:30 AM - 9:00 PM",
    "Lunch special with drink (per reviews)", [
        ("Yelp - Siam Station Milpitas (address, daily 11:30-9)", yelp("siam-station-milpitas")),
    ], flags=[NO_PRICE, "Separate from the Cupertino Siam Station already listed."],
    yelp_slug="siam-station-milpitas")

add("Kathmandu Cuisine", "Milpitas", "138 S Main St, Milpitas, CA 95035",
    "Downtown Milpitas", "Nepali / Indian",
    "Wed-Mon; closed Tue", "Closed Tuesdays",
    "Lunch 11-4", [
        ("Yelp - Kathmandu Cuisine Milpitas (address, phone; Tue closed; other days 11-4 & 6-11:30)", yelp("kathmandu-cuisine-milpitas-2")),
    ], flags=["CLOSED on the trip date (Tuesday).", NO_PRICE, "Hours have changed several times per business updates - confirm.", "Separate from the Los Altos Kathmandu Cuisine already listed."],
    phone="(408) 649-3616", yelp_slug="kathmandu-cuisine-milpitas-2", open_tue=False)

add("Hyderabad Dum Biryani", "Milpitas", "55 Dempsey Rd, Milpitas, CA 95035",
    "Dempsey Rd", "Indian (Hyderabadi, halal)",
    "Daily", "11:30 AM - 10:00 PM",
    "Lunch combos", [
        ("Yelp - Hyderabad Dum Biryani Milpitas (address, phone, daily 11:30-10/10:30)", yelp("hyderabad-dum-biryani-milpitas")),
    ], flags=[NO_PRICE], phone="(408) 493-6133", yelp_slug="hyderabad-dum-biryani-milpitas")

# ---------------------------------------------------------------- West San Jose
add("Kai Japanese Restaurant", "San Jose", "5190 Stevens Creek Blvd, San Jose, CA 95129",
    "West San Jose (Stevens Creek)", "Japanese / Sushi",
    "Wed-Mon; closed Tue", "Closed Tuesdays",
    "Lunch 11:30-2", [
        ("Yelp - Kai Japanese Restaurant (address, phone; Tue closed; other days 11:30-2 & 5-9)", yelp("kai-japanese-restaurant-san-jose")),
        ("Official site", "https://www.kaisushi4u.com/"),
    ], flags=["CLOSED on the trip date (Tuesday).", NO_PRICE], phone="(408) 320-1811",
    yelp_slug="kai-japanese-restaurant-san-jose", open_tue=False,
    bus={"ok": True, "note": "On Stevens Creek Blvd east of Cupertino - VTA 23/523 corridor."})

add("Suvai", "San Jose", "5205 Prospect Rd Ste 110, San Jose, CA 95129",
    "West San Jose (Prospect Rd)", "Indian (South Indian)",
    "Tue-Sun; closed Mon", "11:00 AM - 2:30 PM, 5:30 PM - 10:00 PM",
    "Weekday lunch buffet (per review)", [
        ("Yelp - Suvai (address, phone; Mon closed; Tue-Thu 11-2:30, Fri 11-3, Sat-Sun 8:30-3; review cites weekday lunch buffet)", yelp("suvai-san-jose-2")),
    ], flags=["Buffet price not published."], phone="(408) 703-3884", yelp_slug="suvai-san-jose-2",
    sp_days="Tue-Fri", window="11:00 AM - 2:30 PM")

add("Applebee's Grill + Bar", "San Jose", "555 Saratoga Ave, San Jose, CA 95129",
    "West San Jose (Saratoga Ave)", "American chain",
    "Daily", "11:00 AM - 12:00 AM",
    "Lunch specials (chain menu)", [
        ("Official location page - restaurants.applebees.com (address, phone, daily 11 AM-midnight; 'Lunch Specials' menu section)", "https://restaurants.applebees.com/en-us/ca/san-jose/555-saratoga-ave.-95095"),
    ], level="official", flags=["Lunch special prices not shown on the location page."],
    phone="(408) 446-8370", yelp_slug="applebees-grill-and-bar-san-jose-4")

# ---------------------------------------------------------------- Menlo Park
# ---------------------------------------------------------------- late additions (pass 8b)
add("Pho Nam", "Sunnyvale", "844 W El Camino Real, Sunnyvale, CA 94087",
    "W El Camino Real", "Vietnamese (pho)",
    "Daily", "10:00 AM - 8:00 PM",
    "No published lunch special", [
        ("Yelp - Pho Nam (844 W El Camino; daily 10-8; phone)", yelp("pho-nam-sunnyvale-4")),
    ], flags=[NO_PRICE, "Unclaimed Yelp listing; a second Pho Nam at 1205 Wildwood Ave (10-7) is a different branch."],
    phone="(408) 737-1086", yelp_slug="pho-nam-sunnyvale-4")

add("Pho To Chau 999", "Santa Clara", "2636 Homestead Rd, Santa Clara, CA 95051",
    "Homestead Rd", "Vietnamese (pho)",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Pho To Chau 999 (address, phone; Mon-Thu 11-9/9:30; weekend opens 10-10:30)", yelp("pho-to-chau-999-santa-clara-2")),
        ("Official site", "https://www.photochau999.com/"),
    ], flags=[NO_PRICE, "Closing time differs between Yelp snapshots (9:00 vs 9:30 PM)."],
    phone="(408) 352-5277", yelp_slug="pho-to-chau-999-santa-clara-2")

add("Tommy Thai", "Mountain View", "1482 W El Camino Real, Mountain View, CA 94040",
    "W El Camino Real", "Thai / Cambodian",
    "Daily", "10:30 AM - 11:00 PM",
    "Lunch specials (per reviews)", [
        ("Yelp - Tommy Thai (address, phone, Mon-Sat 10:30-11, Sun 10:30-10)", yelp("tommy-thai-mountain-view")),
        ("Official site", "https://www.tommy-thai.com/"),
    ], flags=[NO_PRICE], phone="(650) 988-6857", yelp_slug="tommy-thai-mountain-view")

add("Veggie Garden", "Mountain View", "2464 W El Camino Real Ste C, Mountain View, CA 94040",
    "W El Camino Real", "Chinese vegetarian / vegan",
    "Tue-Sun; closed Mon", "11:30 AM - 2:30 PM, 5:00 PM - 9:30 PM",
    "Lunch plates (e.g. E6 Mongolian vegetarian chicken lunch)", [
        ("Yelp - Veggie Garden (address, phone; Mon closed; Tue-Fri 11:30-2:30 & 5-9:30; Sat-Sun 11:30-9:30; photo of lunch plate)", yelp("veggie-garden-mountain-view")),
        ("Official site", "https://www.veggiegardenchinese.com/"),
    ], flags=[NO_PRICE], phone="(650) 961-6888", yelp_slug="veggie-garden-mountain-view",
    sp_days="Tue-Fri", window="11:30 AM - 2:30 PM")

add("Uncle John's Pancake House - Winchester", "Campbell", "2125 S Winchester Blvd, Campbell, CA 95008",
    "S Winchester Blvd", "American diner / breakfast",
    "Daily", "7:00 AM - 2:00 PM",
    "Lunch menu (burgers, salads, sandwiches) until 2 PM", [
        ("Yelp - Uncle John's Pancake House Winchester (address, phone, daily 7-2)", yelp("uncle-johns-pancake-house-winchester-campbell")),
        ("Official site", "https://www.unclejohnspancakes.com/"),
    ], flags=[NO_PRICE, "Closes 2:00 PM."], phone="(408) 724-9835",
    yelp_slug="uncle-johns-pancake-house-winchester-campbell", sp_days="Daily", window="Open - 2:00 PM")

add("Must Be Thai", "San Jose", "3143 Stevens Creek Blvd, San Jose, CA 95117",
    "West San Jose (Stevens Creek near Valley Fair)", "Thai",
    "Daily", "11:00 AM - 9:00 PM",
    "No published lunch special", [
        ("Yelp - Must Be Thai (address, phone, Sun-Thu 11-9, Fri-Sat 11-9:30)", yelp("must-be-thai-san-jose-2")),
        ("Official site", "https://www.mustbethai.com/"),
    ], flags=[NO_PRICE, "The downtown 'Must Be Thai and Bar' (18 N San Pedro St) is a separate branch, closed Mon."],
    phone="(408) 816-7179", yelp_slug="must-be-thai-san-jose-2",
    bus={"ok": True, "note": "On Stevens Creek Blvd - VTA 23/523 corridor east of Cupertino."})

add("Khaosan Thai", "San Jose", "2062 Curtner Ave, San Jose, CA 95124",
    "Cambrian Park", "Thai",
    "Daily; lunch Mon-Fri 11-3", "11:00 AM - 3:00 PM, 5:00 PM - 9:00 PM",
    "Lunch Mon-Fri 11-3", [
        ("Official site - khaosanthaisj.com (Mon-Fri 11-3 & 5-9; Sat-Sun 11:30-9; address, phone)", "https://www.khaosanthaisj.com/home"),
        ("Yelp - Khaosan Thai (hours cross-check)", yelp("khaosan-thai-san-jose")),
    ], level="official", flags=[NO_PRICE, "Cambrian Park is ~9 mi from Cupertino - edge of the ring."],
    phone="(408) 677-8061", yelp_slug="khaosan-thai-san-jose", sp_days="Mon-Fri", window="11:00 AM - 3:00 PM")

rejected = [
    {"name": "Arya Global Cuisine", "city": "Cupertino", "why": "Yelp marks the business CLOSED.", "price_hint": None},
    {"name": "Bull Ohgane", "city": "Cupertino", "why": "Yelp marks 10493 S De Anza Blvd location CLOSED.", "price_hint": None},
    {"name": "Arirang Tofu & BBQ", "city": "Cupertino", "why": "Yelp marks 10310 S De Anza Blvd location CLOSED.", "price_hint": None},
    {"name": "Islands Restaurant", "city": "Cupertino", "why": "Yelp marks 20750 Stevens Creek Blvd location CLOSED.", "price_hint": None},
    {"name": "Chili's Grill & Bar", "city": "Cupertino", "why": "Yelp marks 20060 Stevens Creek Blvd location CLOSED.", "price_hint": None},
    {"name": "Turmeric", "city": "Sunnyvale", "why": "Permanently closed per listings.", "price_hint": None},
    {"name": "Tong Dumpling", "city": "Cupertino", "why": "Official site dead; could not confirm the business is still operating.", "price_hint": None},
    {"name": "Beque Korean Grill", "city": "Santa Clara", "why": "Dinner-only on weekdays (Mon-Fri opens 4 PM per Yelp); no Tuesday lunch.", "price_hint": "dolsot $13-14 (review)"},
    {"name": "Xanh", "city": "Mountain View", "why": "110 Castro St now lists as Bloom & Vine; Xanh appears replaced.", "price_hint": None},
    {"name": "Amarin Thai Cuisine (174 Castro)", "city": "Mountain View", "why": "Old location marked CLOSED on Yelp; replaced by the 147 Castro St row.", "price_hint": None},
    {"name": "Amarin Thai Cuisine", "city": "San Jose", "why": "5205 Prospect Rd location marked CLOSED on Yelp (space now Suvai).", "price_hint": None},
    {"name": "Chef Ko Chinese Cuisine", "city": "Campbell", "why": "Yelp marks the business CLOSED.", "price_hint": None},
    {"name": "Taste of Pho", "city": "Santa Clara", "why": "Yelp marks the business CLOSED.", "price_hint": None},
    {"name": "K-Star Doshirak", "city": "Santa Clara", "why": "Yelp marks the business CLOSED.", "price_hint": None},
    {"name": "Bierhaus", "city": "Mountain View", "why": "383 Castro St location marked CLOSED on Yelp (Das Bierhauz at 135 Castro is a different business).", "price_hint": None},
    {"name": "El Alto", "city": "Los Altos", "why": "Yelp marks the business CLOSED; was dinner-only anyway.", "price_hint": None},
    {"name": "The Menu", "city": "Mountain View", "why": "Yelp marks the business CLOSED.", "price_hint": None},
    {"name": "Los Gatos Tavern", "city": "Los Gatos", "why": "Dinner-only (Tue-Sat from 5 PM).", "price_hint": None},
    {"name": "The Cats Restaurant", "city": "Los Gatos", "why": "Lunch only Sat-Sun brunch buffet ($29.95); closed Mon-Thu.", "price_hint": "$29.95 weekend brunch buffet"},
    {"name": "GOGA Restaurant (batch8 recheck)", "city": "Saratoga", "why": "Already in master; Yelp confirms closed Tue and lunch Sat-Sun only.", "price_hint": None},
    {"name": "Hiroshi", "city": "Los Altos", "why": "Dinner-only (daily 5-10:30 PM).", "price_hint": None},
    {"name": "Yeobo Darling", "city": "Menlo Park", "why": "Dinner-only per Yelp (opens 5 PM).", "price_hint": None},
    {"name": "Drunken Monk", "city": "Menlo Park", "why": "Dinner-only per Yelp (opens 5 PM).", "price_hint": None},
    {"name": "Chaat Bhavan Express", "city": "Sunnyvale", "why": "Same 544 Lawrence Expy site as the Chaat Bhavan (Lawrence Expressway) row already in master.", "price_hint": None},
    {"name": "Little Sky Kitchen", "city": "Menlo Park", "why": "Shares the 1010 El Camino Real parcel with Cafe Borrone (L246) with no suite number, so the address dedupe cannot separate them (see LUNCH-FLAG on address collisions); unclaimed listing, no phone.", "price_hint": None},
    {"name": "Little Sky Bakery", "city": "Menlo Park", "why": "Bakery (506 Santa Cruz Ave, 8-4 daily) - not a lunch-special venue; listed here only to avoid confusion with Little Sky Kitchen.", "price_hint": None},
    {"name": "Mendocino Farms", "city": "Cupertino", "why": "Could not confirm a Cupertino location from official/Yelp sources (search returned other cities only).", "price_hint": None},
]

batch = {
    "note": "Batch 8 - pass 8, 2026-09-08. 100 new rows for Cupertino and the 10-15 mile ring (Sunnyvale, Los Altos, Mountain View, Santa Clara, Los Gatos, Campbell, Saratoga, Palo Alto, Milpitas, west San Jose, Menlo Park). Hours/addresses transcribed from Yelp business-page snippets, official sites and menu mirrors listed on each row; prices only where a source printed one. Rows with no verifiable price carry a 'price not printed' flag. Yelp pages return HTTP 403 to automated fetchers, so Yelp links are for manual review.",
    "entries": rows,
    "rejected": rejected,
}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(batch, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print(len(rows), "entries,", len(rejected), "rejected ->", OUT)
