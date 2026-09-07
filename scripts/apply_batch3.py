#!/usr/bin/env python3
"""Batch-3 data update (2026-09-07, second pass).

Applies, in one auditable place:
  1. Transit re-verification corrections (VTA minutes, stop 15199, $0.50
     Caltrain->Muni credit, youth $1, MuniMobile single-ride discontinued,
     early-return backup row).
  2. Lunch updates to L03/L36/L21/L19/L40.
  3. 54 new master rows L48-L101.
  4. 3 new rejected rows (R15-R17, 4 businesses).
  5. New flags (FLAG-10/11/12, LUNCH-FLAG-11) + FLAG-2 resolution note.
  6. New sources S31-S37 + S6/S12/S15 refreshes.
  7. search_protocol counters, README.md and docs/VERIFICATION.md text.

Run from the repo root:  python3 scripts/apply_batch3.py
Then:  python3 scripts/build_data.py && python3 scripts/check_links.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def save(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


ACC = "2026-09-07"
NOT_CUP = "not on the Cupertino return walk"

# ---------------------------------------------------------------- transit
outbound = load("transit_outbound.json")
retplan = load("transit_return.json")
fares = load("fares.json")
plan = load("plan.json")

# CORRECTION 1: Plan A2 VTA timepoints 7:54/8:02 -> 7:55/8:03.
a2vta = outbound["plans"][1]["legs"][3]
assert "7:54" in a2vta["note"] and "8:02" in a2vta["note"]
a2vta["note"] = a2vta["note"].replace(
    "De Anza & Homestead 7:54, Stelling & Stevens Creek 8:02",
    "De Anza & Homestead 7:55, Stelling & Stevens Creek 8:03")

# CORRECTION 2: Plan B VTA timepoint 10:21 -> 10:20.
bvta = outbound["plans"][2]["legs"][3]
assert "10:21" in bvta["note"]
bvta["note"] = bvta["note"].replace(
    "Stelling & Stevens Creek 10:21", "Stelling & Stevens Creek 10:20")

# CORRECTION 3: westbound Judah & 19th Ave stop 15201 -> 15199 (return only;
# eastbound boarding stop 15200 is unchanged).
for p in retplan["plans"]:
    for leg in p["legs"]:
        for key in ("from", "to", "note"):
            if isinstance(leg.get(key), str) and "15201" in leg[key]:
                leg[key] = leg[key].replace("15201", "15199")
        for s in leg.get("sources", []):
            if "15201" in s.get("verifies", ""):
                s["verifies"] = s["verifies"].replace("15201", "15199")
plan["origin"]["nearest_stop"] = plan["origin"]["nearest_stop"].replace(
    "15201 westbound", "15199 westbound")

# CORRECTION 5: transfer credit $2.85 -> $0.50 TO Muni only, within 1 hour.
r1muni = retplan["plans"][0]["legs"][4]
r1muni["fare_note"] = (
    "Single ride $2.85 (or $3.00 cash). With the same Clipper/contactless card "
    "used to tag off Caltrain, the $0.50 inter-agency transfer credit applies, "
    "so this ride is $2.35 if tapped within 1 hour.")
r1muni["sources"][1]["verifies"] = (
    "$2.85 single ride, $3.00 cash, day pass $5.70, and the $0.50 "
    "inter-agency transfer credit onto Muni within 1 hour of tagging off Caltrain")
retplan["plans"][1]["legs"][3]["fare_note"] = (
    "$2.85, or $2.35 with the $0.50 Clipper inter-agency credit "
    "(same card, within 1 hour of the Caltrain tag-off).")
retplan["plans"][2]["legs"][4]["fare_note"] = "$2.85 ($2.35 with the $0.50 credit)."
for p in retplan["plans"]:
    assert p["clipper_cost_usd"] == 11.0
    p["clipper_cost_usd"] = 13.35  # 2.50 + 8.50 + 2.35

# Early-return backup row (VTA 55 NB Stelling 11:31 -> TC 11:55, verified).
retplan["option_table"].insert(0, {
    "leave_gillick": "11:27 AM",
    "vta_55_nb": "about 11:36 AM at McClellan & Felton (11:31 AM from Stelling & Stevens Creek)",
    "arrives_sunnyvale_tc": "11:55 AM",
    "caltrain_nb": "12:12 PM from Sunnyvale",
    "arrives_sf_terminal": "1:16 PM",
    "n_judah_wb": "1:32 PM",
    "home": "about 2:16 PM",
    "status": "EARLY BACKUP - needs lunch done by about 11:20 AM; verified 2026-09-07",
})
retplan["notes"][1] = (
    "The 11:31 AM northbound trip from Stelling & Stevens Creek (Sunnyvale TC "
    "11:55 AM) was verified on the VTA weekday sheet on 2026-09-07 and is shown "
    "as the early-backup row above; earlier mid-morning trips exist but their "
    "stop times were not verified.")

# CORRECTION 4: Caltrain youth one-way is $1.00 flat, all zones.
for a in fares["agencies"]:
    if a["id"] == "caltrain":
        for r in a["rows"]:
            if r["ticket"].startswith("Youth"):
                r["price"] = 1.0
                r["validity"] = "$1.00 flat, all zones"
    if a["id"] == "sfmta":
        for r in a["rows"]:
            if r["ticket"].startswith("Single Ride (Clipper"):
                # CORRECTION 6: MuniMobile Single Ride passes discontinued Sep 1 2026.
                r["ticket"] = "Single Ride (Clipper or contactless)"
            if r["ticket"].startswith("Clipper inter-agency"):
                r["price"] = -0.50
                r["validity"] = ("$0.50 off an adult Muni fare when transferring TO Muni "
                                 "from Caltrain within 1 hour of tagging off (tag on and off; "
                                 "Clipper cash value or monthly pass including Zone 1; SFMTA table "
                                 "also shows contactless eligible)")
                r["applies_to"] = ("the return N Judah ride after tapping off Caltrain "
                                    "on the same card")
        a["notes"].append(
            "MuniMobile Single Ride passes were discontinued Sep 1 2026 - on Sep 8 a "
            "Muni single ride is Clipper/contactless ($2.85) or cash/TVM ($3.00).")

dt = fares["day_totals"]
# Cheapest realistic: drop the nonexistent Muni->Caltrain credit, apply $0.50 on return.
dt[0]["items"] = [i for i in dt[0]["items"] if i["fare"] != -2.85]
assert len(dt[0]["items"]) == 6
dt[0]["items"][-1] = {
    "label": ("Muni N Judah metro, 1:56 PM (more than 120 min after the first tap, "
              "so a new Single Ride $2.85 minus the $0.50 Caltrain-to-Muni credit)"),
    "fare": 2.35,
}
dt[0]["total"] = 27.20
dt[0]["assumption"] = ("Adult fare, Clipper or contactless end to end; the $0.50 "
                       "Caltrain-to-Muni credit applies to the return Muni ride (same card, "
                       "tag off Caltrain then tap Muni within 1 hour).")
dt[0]["verified_from"] += ", https://www.caltrain.com/fares/regional-transfer-discounts"
dt[1]["assumption"] = ("Useful if you do not tap the same Clipper card onto Caltrain, or if you "
                       "buy a paper ticket: the $0.50 Muni credit is not applied.")
dt[1]["caveat"] = "$0.50 more than the first option; the credit is the only difference."
dt[3]["caveat"] = ("$0.50 more than two one-ways with the transfer credit, so the day pass is "
                   "cheap insurance against a missed train on the outbound leg.")
dt[4]["caveat"] = ("Costs $3.00 more than the Clipper option ($30.20 vs $27.20) and adds nothing "
                   "for a single one-way pair of rides.")
dt[5]["items"][1]["fare"] = 2.0
dt[5]["items"][1]["label"] = "Caltrain youth 3-zone one-way, both directions ($1.00 flat each)"
dt[5]["total"] = 4.5

plan["verification"]["review_status"] = (
    "Ready for manual review. 23 open flags (12 transit + 11 lunch), listed in "
    "data/flags.json and on the Flags tab.")

save("transit_outbound.json", outbound)
save("transit_return.json", retplan)
save("fares.json", fares)
save("plan.json", plan)

# ---------------------------------------------------------------- lunch updates
specials = load("lunch_specials.json")
by_id = {e["id"]: e for e in specials["entries"]}

# LUNCH UPDATE 1: Home Eat Cupertino lunch floor is $12.99.
l03 = by_id["L03"]
l03["lunch_special"]["price_from"] = 12.99
l03["lunch_special"]["includes"] = (
    "Crispy Chicken / Sesame Chicken $12.99, Beef Broccoli $13.99, Mongolian Shrimp "
    "$14.99, String Beans & Eggplant (price not shown in the menu block), each with a "
    "randomly chosen complimentary dine-in drink")
specials["top_picks_for_tuesday_sept_8"][0]["why"] = specials[
    "top_picks_for_tuesday_sept_8"][0]["why"].replace("$13.99-$14.99", "$12.99-$14.99")

# LUNCH UPDATE 2: Galpao official lunch prices.
l36 = by_id["L36"]
l36["lunch_special"]["name"] = "Weekday lunch rodizio (official Cupertino lunch prices)"
l36["lunch_special"]["price_from"] = 46.0
l36["lunch_special"]["price_to"] = 59.0
l36["lunch_special"]["includes"] = (
    "Official pricing page: lunch Monday-Friday salad bar $46 / full experience $59; "
    "dinner and weekends $46 / $79.")
l36["verification"]["level"] = "official"
l36["verification"]["sources"][0] = {
    "label": "Official Galpao Cupertino pricing (lunch Mon-Fri $46/$59)",
    "url": "https://galpaogauchousa.com/location/cupertino-ca/",
}
l36["flags"][0] = ("Previously rejected (R10) for dinner-only pricing; re-added with a weekday "
                   "lunch window and now official lunch prices. Lunch ends about 2:00 PM; only "
                   "a short meal fits the 11:50 AM departure.")

# LUNCH UPDATE 3: Gardenia Thursday conflict resolved (Mon closed, Tue-Sun open).
l21 = by_id["L21"]
l21["hours_tuesday"] = "8:30 AM - 9:00 PM (brunch 10:30 AM - 2:30 PM)"
l21["days_open"] = "Monday closed; Tue-Sun 8:30 AM - 9:00 PM (Yelp, current)"
l21["verification"]["level"] = "listing"
l21["flags"][0] = ("Thursday-closure conflict RESOLVED 2026-09-07: the current Yelp listing shows "
                    "Monday closed, Tue-Sun 8:30 AM - 9:00 PM. Phone (669) 294-4498.")

# LUNCH NOTE L19: Los Gatos Cafe current dish prices.
l19 = by_id["L19"]
l19["lunch_special"]["includes"] += (" Current Yelp dishes $16.80-$28.80 "
                                     "(Irish Benedict $24.00, Crabcakes $28.80).")
l19["flags"][1] = ("No lunch price published; the $16.80-$28.80 figures are regular menu items "
                    "from Yelp (Irish Benedict $24, Crabcakes $28.80), not special pricing.")

# LUNCH FLAG L40: event price vs daily offer.
by_id["L40"]["flags"].append(
    "Sunnyvale Restaurant Week lunch $16.99 (svoc.org) was a past limited-time event, not "
    "the daily offer - the row keeps OpenTable's daily 'Lunch from $13.99'.")

# ---------------------------------------------------------------- 54 new rows
def gmaps(q):
    return "https://www.google.com/maps/search/?api=1&query=" + q.replace(" ", "+")


def yelp_search(desc, loc):
    return ("https://www.yelp.com/search?find_desc=" + desc.replace(" ", "+").replace("&", "%26")
            + "&find_loc=" + loc.replace(" ", "+").replace(",", "%2C"))


def E(id_, name, city, area, address, cuisine, ls_name, pf, pt, days, window, includes,
      hours_tue, days_open, open_trip, fit_ok, fit_note, level, sources, yelp, maps_q,
      flags, phone=None, coords=None, coords_source=None):
    e = {
        "id": id_, "name": name, "city": city, "area": area, "address": address,
        "coords": coords, "cuisine": cuisine,
        "lunch_special": {"name": ls_name, "price_from": pf, "price_to": pt,
                          "days": days, "window": window, "includes": includes},
        "hours_tuesday": hours_tue, "days_open": days_open,
        "open_on_trip_date": open_trip,
        "fits_return_bus": {"ok": fit_ok, "note": fit_note},
        "verification": {"level": level, "sources": sources, "accessed": ACC},
        "review_links": {"yelp": yelp, "google_maps": gmaps(maps_q)},
        "flags": flags, "distance_mi": None,
    }
    if phone:
        e["phone"] = phone
    if coords_source:
        e["coords_source"] = coords_source
    return e


NEW = [
    E("L48", "Ginger Cafe", "Sunnyvale", "W El Camino Real",
      "1146 W El Camino Real, Sunnyvale, CA 94087", "Chinese / Southeast Asian",
      "Lunch Specials with soup + rice", 16.0, 19.0, "every day",
      "11:00 AM - 3:00 PM",
      "Entree ($16-$19: e.g. Kung Pao Chicken $17, Mango Chicken $17.50, Crispy Shrimp "
      "Garlic Noodles $19, Wonton Soup $16) with soup of the day and steamed or egg fried rice.",
      "11:00 AM - 9:00 PM (lunch 11 AM - 3 PM; dinner/dim sum 11 AM - 9 PM)",
      "every day 11:00 AM - 9:00 PM", True, False,
      "Sunnyvale El Camino - " + NOT_CUP + ".", "official",
      [{"label": "Ginger Cafe official lunch menu - specials $16-$19, 11 AM-3 PM, soup + rice",
        "url": "https://gingercafe.net/menus/lunchmenu/"},
       {"label": "Ginger Cafe homepage - address, phone, daily hours",
        "url": "https://gingercafe.net/"}],
      yelp_search("Ginger Cafe", "Sunnyvale, CA"), "Ginger Cafe 1146 W El Camino Real Sunnyvale",
      ["Salad add-on price conflicts on the restaurant's own pages ($1.25 vs $2.50) - "
       "confirm at the table."],
      phone="(408) 736-2828"),
    E("L49", "Thai Spoons", "Sunnyvale", "W El Camino Real",
      "909 W El Camino Real, Sunnyvale, CA 94087", "Thai, seafood, vegan",
      "Lunch Combo Menu", None, None, "Tue-Sat",
      "10:30 AM - 2:00 PM",
      "Ordering storefront lists a Lunch Combo Menu 10:30 AM - 2:00 PM (items/prices not "
      "captured). A Yelp reviewer mentions $5-$6 lunch specials (date unknown - do not budget).",
      "10:30 AM - 9:00 PM (Chowbus) / 11:00 AM - 9:00 PM (restaurantji)",
      "Tue-Sat 10:30/11:00 AM - 9:00 PM; Sun closed; Monday conflicts (closed per Chowbus, "
      "11-9 per restaurantji)", True, False, "Sunnyvale - " + NOT_CUP + ".", "review",
      [{"label": "Thai Spoons ordering storefront - address, hours, Lunch Combo Menu 10:30-2",
        "url": "https://pos.chowbus.com/online-ordering/store/Thai-Spoons/22597"},
       {"label": "Restaurantji - Thai Spoons hours/address cross-check",
        "url": "https://www.restaurantji.com/ca/sunnyvale/thai-spoons-/"}],
      yelp_search("Thai Spoons", "Sunnyvale, CA"), "Thai Spoons 909 W El Camino Real Sunnyvale",
      ["Monday open/closed conflicts between sources; Tuesday lunch is agreed. Combo prices "
       "unpublished - phone (408) 739-1798."],
      phone="(408) 739-1798", coords=[37.37144595, -122.0441334],
      coords_source="thaifoodnetwork listing geo"),
    E("L50", "First Wok", "Sunnyvale", "S Bernardo Ave",
      "653 S Bernardo Ave, Sunnyvale, CA 94087", "Chinese, vegetarian",
      "Lunch specials (Yelp tag; details unpublished)", None, None, "unknown",
      "store hours 11:00 AM - 9:30 PM",
      "Yelp tags it for lunch specials but no lunch menu, items or prices were captured.",
      "11:00 AM - 9:30 PM", "Mon-Sat 11:00 AM - 9:30 PM; Sunday conflicts (closed per "
      "restaurantji/ordering page, open per zmenu)", True, False,
      "Sunnyvale - " + NOT_CUP + ".", "listing",
      [{"label": "Restaurantji - First Wok address, hours, phone",
        "url": "https://www.restaurantji.com/ca/sunnyvale/first-wok-/"},
       {"label": "First Wok ordering page - address/hours JSON-LD",
        "url": "https://www.smorefood.com/by3jcocr/first-wok-sunnyvale-94087/order-online"}],
      yelp_search("First Wok", "Sunnyvale, CA"), "First Wok 653 S Bernardo Ave Sunnyvale",
      ["Sunday open/closed conflicts; Tuesday agreed. No lunch price published - phone "
       "(408) 481-9888."],
      phone="(408) 481-9888"),
    E("L51", "Asia Village Restaurant", "Sunnyvale", "S Wolfe Rd",
      "747 S Wolfe Rd, Sunnyvale, CA 94086", "Cantonese / Chinese",
      "Lunch specials incl. beef stew (reviewer)", None, None, "unknown",
      "11:00 AM - 2:30 PM",
      "Reviewer describes a beef stew lunch special; no lunch menu or prices captured.",
      "11:00 AM - 2:30 PM, 4:30 PM - 9:00 PM",
      "every day 11:00 AM - 2:30 PM / 4:30 - 9:00 PM (restaurantji, restaurantguru); Apple "
      "Maps says Monday closed", True, False, "Sunnyvale - " + NOT_CUP + ".", "listing",
      [{"label": "Restaurantji - Asia Village hours/address",
        "url": "https://www.restaurantji.com/ca/sunnyvale/asia-village-/"},
       {"label": "RestaurantGuru - Asia Village hours/geo cross-check",
        "url": "https://restaurantguru.com/Asia-Village-Sunnyvale"}],
      yelp_search("Asia Village", "Sunnyvale, CA"), "Asia Village 747 S Wolfe Rd Sunnyvale",
      ["Monday open/closed conflicts; Tuesday lunch agreed. Apple Maps lists an official site "
       "(asiavillagesunnyvale.com) that was not fetched - it may publish the lunch menu. "
       "Phone (408) 773-8988."],
      phone="(408) 773-8988", coords=[37.365393, -122.0150982],
      coords_source="restaurantguru geo fields"),
    E("L52", "Pho Lyfe", "Sunnyvale", "E El Camino Real",
      "568 E El Camino Real Unit B, Sunnyvale, CA 94087", "Vietnamese",
      "Lunch specials (reviewer: published on restaurant website)", None, None, "unknown",
      "store hours 11:00 AM - 9:00 PM",
      "Reviewer says lunch specials are on the restaurant's website; the site (pholyfe.com) "
      "returned HTTP 500 when fetched, so items/prices are unconfirmed.",
      "11:00 AM - 9:00 PM", "every day 11:00 AM - 9:00 PM (Yelp)", True, False,
      "Sunnyvale - " + NOT_CUP + ".", "review",
      [{"label": "Yelp - Pho Lyfe (address, phone, daily 11-9 hours)",
        "url": "https://www.yelp.com/biz/pho-lyfe-sunnyvale-2"}],
      "https://www.yelp.com/biz/pho-lyfe-sunnyvale-2", "Pho Lyfe 568 E El Camino Real Sunnyvale",
      ["Official site unreachable (HTTP 500) - lunch specials unconfirmed. Phone "
       "(408) 685-2121."],
      phone="(408) 685-2121"),
    E("L53", "Cam Hung", "Sunnyvale", "Reed Ave",
      "903 Reed Ave, Sunnyvale, CA 94086", "Vietnamese sandwiches, coffee & tea",
      "Banh mi lunch (~$10 reviewer)", 10.0, None, "every day",
      "all day (opens 8:00/8:30 AM)",
      "Reviewer figure: banh mi about $10. No published menu prices captured.",
      "8:00 AM - 8:00 PM (Yelp) / 8:30 AM - 8:00 PM (Tripadvisor)",
      "Mon-Fri 8:00 AM - 8:00 PM; Sat-Sun 9:00 AM - 8:00 PM (Yelp)", True, False,
      "Sunnyvale - " + NOT_CUP + ".", "review",
      [{"label": "Yelp - Cam Hung (address, phone, weekly hours)",
        "url": "https://www.yelp.com/biz/cam-hung-sunnyvale"},
       {"label": "Tripadvisor - Cam Hung (address, hours, geo)",
        "url": "https://www.tripadvisor.com/Restaurant_Review-g33146-d540624-Reviews-C_m_Hung_Sandwich_Coffee-Sunnyvale_California.html"}],
      "https://www.yelp.com/biz/cam-hung-sunnyvale", "Cam Hung 903 Reed Ave Sunnyvale",
      ["Opening time conflicts by 30 min (8:00 vs 8:30 AM); Tuesday open either way. Price "
       "is a reviewer figure. Phone (408) 735-8989."],
      phone="(408) 735-8989", coords=[37.366985, -122.013306],
      coords_source="Tripadvisor JSON-LD"),
    E("L54", "Country Gourmet", "Sunnyvale", "S Mary Ave",
      "1314 S Mary Ave, Sunnyvale, CA 94087", "American breakfast, brunch & lunch",
      "Brunch/lunch menu (no priced special)", None, None, "unknown",
      "lunch covered under either hours reading",
      "Breakfast/brunch/lunch restaurant; no lunch special or prices captured.",
      "7:00 AM - 9:00 PM (Yellow Pages, Tripadvisor) vs 8:00 AM - 3:00 PM (nears.me)",
      "conflicting - see Tuesday line", True, False, "Sunnyvale - " + NOT_CUP + ".", "listing",
      [{"label": "Yellow Pages - Country Gourmet (address, Mon-Fri 7-9 hours)",
        "url": "https://www.yellowpages.com/sunnyvale-ca/mip/country-gourmet-restaurant-305632"},
       {"label": "Tripadvisor - Country Gourmet American Bistro (hours, geo)",
        "url": "https://www.tripadvisor.com/Restaurant_Review-g33146-d350027-Reviews-Country_Gourmet_American_Bistro-Sunnyvale_California.html"}],
      yelp_search("Country Gourmet", "Sunnyvale, CA"), "Country Gourmet 1314 S Mary Ave Sunnyvale",
      ["Hours conflict materially (close 3 PM vs 9 PM); Tuesday lunch is covered by both. "
       "countrygourmet.com is a parked domain - there is no official site there. Phone "
       "(408) 733-9446."],
      phone="(408) 733-9446", coords=[37.351474, -122.049414],
      coords_source="nears.me listing geo"),
    E("L55", "Dumpling Depot", "Sunnyvale", "S Murphy Ave, downtown Sunnyvale",
      "562 S Murphy Ave, Sunnyvale, CA 94086", "Dumplings, dim sum, noodles",
      "Lunch service (no priced special)", None, None, "every day",
      "11:00 AM - 2:30 PM (Sat-Sun to 3:00 PM)",
      "Official site gives hours only; no lunch menu prices captured.",
      "11:00 AM - 2:30 PM, 5:00 PM - 9:00 PM",
      "Mon-Fri 11:00 AM - 2:30 PM / 5:00 - 9:00 PM; Sat-Sun 11:00 AM - 3:00 PM / 5:00 - "
      "9:00 PM (official)", True, False, "Downtown Sunnyvale - " + NOT_CUP + ".", "official",
      [{"label": "Dumpling Depot official site - address and weekly hours",
        "url": "https://dumplingdepot-s.com/"},
       {"label": "Restaurantji - Dumpling Depot hours cross-check",
        "url": "https://www.restaurantji.com/ca/sunnyvale/dumpling-depot-/"}],
      yelp_search("Dumpling Depot", "Sunnyvale, CA"), "Dumpling Depot 562 S Murphy Ave Sunnyvale",
      ["No lunch prices published on the official site. Phone (408) 685-2979."],
      phone="(408) 685-2979", coords=[37.3694473, -122.0321685],
      coords_source="official ordering page JSON-LD"),
    E("L56", "10 Butchers Korean BBQ", "Sunnyvale", "E El Camino Real, Camino Oaks Plaza",
      "595 E El Camino Real, Sunnyvale, CA 94087", "Korean BBQ, wine bar",
      "Lunch special (reviewer)", None, None, "unknown",
      "11:30 AM - 2:30 PM",
      "Reviewer mentions a lunch special; items/prices unconfirmed.",
      "11:30 AM - 2:30 PM, 5:00 PM - 9:00 PM",
      "Mon-Thu 11:30 AM - 2:30 PM / 5:00 - 9:00 PM; Fri to 10:00 PM; Sat 11:30 AM - 10:00 "
      "PM; Sun 11:30 AM - 9:00 PM (3 sources agree)", True, False,
      "Sunnyvale - " + NOT_CUP + ".", "listing",
      [{"label": "Restaurantji - 10 Butchers hours/address",
        "url": "https://www.restaurantji.com/ca/sunnyvale/10-butchers-korean-bbq-/"},
       {"label": "RestaurantGuru - 10 Butchers hours/geo cross-check",
        "url": "https://restaurantguru.com/10-Butchers-Korean-BBQ-Sunnyvale"}],
      yelp_search("10 Butchers", "Sunnyvale, CA"), "10 Butchers 595 E El Camino Real Sunnyvale",
      ["Official site 10butchers.net was not fetched - it may publish the lunch special. "
       "Phone (408) 720-8889."],
      phone="(408) 720-8889", coords=[37.3628164, -122.0254525],
      coords_source="restaurantguru geo fields"),
    E("L57", "Home Eat", "Santa Clara", "El Camino Real",
      "638 El Camino Real, Santa Clara, CA 95050", "Chinese, seafood, hot pot",
      "Lunch Specials with mystery drink", 12.99, 14.99,
      "listed on the online menu; no day restriction shown",
      "restaurant open 11:15 AM - 11:15 PM",
      "Chicken $12.99 / beef $13.99 / shrimp $14.99 tiers with a randomly chosen "
      "complimentary dine-in drink (same program as the Cupertino store).",
      "11:15 AM - 11:15 PM", "every day 11:15 AM - 11:15 PM (Yelp, Apple Maps)", True, False,
      "Santa Clara - " + NOT_CUP + " (sister store of L03).", "official",
      [{"label": "Home Eat Santa Clara official ordering - lunch specials $12.99-$14.99",
        "url": "https://homeeat.toast.site/order/home-eat-santa-clara"},
       {"label": "Yelp - Home Eat Santa Clara (address, phone, daily hours)",
        "url": "https://www.yelp.com/biz/home-eat-santa-clara-2"}],
      "https://www.yelp.com/biz/home-eat-santa-clara-2", "Home Eat 638 El Camino Real Santa Clara",
      ["Drink is randomly selected per the menu text. Phone (408) 984-0414."],
      phone="(408) 984-0414"),
    E("L58", "Dusita Thai Cuisine", "Santa Clara", "El Camino Real",
      "2325 El Camino Real, Ste 104-105, Santa Clara, CA 95050", "Thai",
      "Weekday lunch", 13.75, None, "Monday-Friday", "11:00 AM - 2:30 PM",
      "Reviewer figure $13.75 for weekday lunch; official menu PDF confirms the lunch "
      "window (regular menu prices e.g. soups $11.95+).",
      "11:00 AM - 2:30 PM, 5:00 PM - 9:30 PM",
      "Mon-Fri lunch 11:00 AM - 2:30 PM + dinner 5:00 - 9:30 PM; Sat dinner only; Sun "
      "closed (official PDF, Yelp agrees)", True, False, "Santa Clara - " + NOT_CUP + ".",
      "mixed",
      [{"label": "Dusita official menu PDF - lunch window, address, phone",
        "url": "https://dusitathaicuisine.com/wp-content/uploads/Dusita_mainmenu_JL-1-10-no-bg-SM.pdf"},
       {"label": "Yelp - Dusita Thai Cuisine (hours cross-check)",
        "url": "https://www.yelp.com/biz/dusita-thai-cuisine-santa-clara"}],
      "https://www.yelp.com/biz/dusita-thai-cuisine-santa-clara",
      "Dusita Thai 2325 El Camino Real Santa Clara",
      ["$13.75 is a reviewer figure, not a published lunch price. Phone (408) 247-5199."],
      phone="(408) 247-5199"),
    E("L59", "Il Fornaio", "Santa Clara", "Augustine Dr, north Santa Clara",
      "2752 Augustine Dr, Ste 120, Santa Clara, CA 95054", "Italian, pizza, seafood",
      "Lunch menu (no priced special)", None, None, "every day",
      "opens 11:30 AM",
      "No lunch special or prices captured; official menu not fetched.",
      "11:30 AM - 9:30 PM (Yelp) / to 9:00 PM Mon-Thu (wheree)",
      "every day 11:30 AM - 9:30 PM (Yelp, updated ~Sep 2026)", True, False,
      "North Santa Clara - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Il Fornaio Santa Clara (address, phone, daily hours)",
        "url": "https://www.yelp.com/biz/il-fornaio-santa-clara-2"},
       {"label": "Wheree - Il Fornaio hours cross-check",
        "url": "https://il-fornaio-santa-clara.wheree.com/"}],
      "https://www.yelp.com/biz/il-fornaio-santa-clara-2", "Il Fornaio 2752 Augustine Dr Santa Clara",
      ["Close time conflicts by 30 min on weeknights (9:00 vs 9:30 PM); lunch unaffected. "
       "Phone (408) 217-8844."],
      phone="(408) 217-8844"),
    E("L60", "Mastro's Steakhouse", "Santa Clara", "Stevens Creek Blvd (Valley Fair)",
      "2855 Stevens Creek Blvd, Suite 1860, Santa Clara, CA 95050", "Steakhouse, seafood",
      "Lunch menu (official; price band to re-verify)", None, None, "every day",
      "opens 12:00 PM",
      "Official lunch menu exists; a ~$22-$42 mains band was seen in the first pass and must "
      "be re-verified on the menu page before budgeting.",
      "12:00 PM - 9:00 PM", "Sun-Thu 12:00 PM - 9:00 PM; Fri-Sat 12:00 PM - 10:00 PM "
      "(official)", True, False, "Santa Clara - " + NOT_CUP + ".", "official",
      [{"label": "Mastro's official Santa Clara page - address, hours",
        "url": "https://www.mastrosrestaurants.com/location/santa-clara/"},
       {"label": "Mastro's California page - Santa Clara dining hours cross-check",
        "url": "https://www.mastrosrestaurants.com/california/"}],
      yelp_search("Mastro's Steakhouse", "Santa Clara, CA"),
      "Mastro's Steakhouse 2855 Stevens Creek Blvd Santa Clara",
      ["CORRECTION: this is Mastro's STEAKHOUSE Santa Clara, not an Ocean Club. Lunch price "
       "band unverified - phone (408) 538-4183."],
      phone="(408) 538-4183"),
    E("L61", "Erik's DeliCafe", "Santa Clara", "Kiely Blvd",
      "830 Kiely Blvd, Suite 105, Santa Clara, CA 95051", "Deli: sandwiches, salads, soups",
      "Deli lunch (no priced special)", None, None, "every day",
      "opens 10:00 AM (11:00 AM Sun)",
      "No lunch special or prices captured; sandwiches/salads/soups/bakery.",
      "10:00 AM - 7:00 PM", "Mon-Sat 10:00 AM - 7:00 PM; Sun 11:00 AM - 7:00 PM (official)",
      True, False, "Santa Clara - " + NOT_CUP + ".", "official",
      [{"label": "Erik's DeliCafe official locations - Santa Clara Kiely address/hours",
        "url": "https://www.eriksdelicafe.com/locations/"}],
      yelp_search("Erik's DeliCafe", "Santa Clara, CA"), "Erik's DeliCafe 830 Kiely Blvd Santa Clara",
      ["No prices on the locations page - check the ordering menu. Phone (408) 246-1010."],
      phone="(408) 246-1010"),
    E("L62", "Clara's Junction", "Santa Clara", "Tasman Dr, near Levi's Stadium",
      "2221 Tasman Dr, Santa Clara, CA 95054", "American, sports bar, BBQ",
      "$19 Two-Course Lunch (NOT valid Tuesday)", 19.0, 19.0,
      "Wednesday-Friday ONLY", "11:00 AM - 3:00 PM",
      "Official: starter (avocado/Caesar/hummus) + main (smash burger, chicken/pork "
      "sandwich, tinga tacos, fish & chips) + lemonade/iced tea/soda. Tuesday is regular "
      "menu only.",
      "11:00 AM - 9:00 PM (Yelp) vs CLOSED Tuesday (wheree) - CONFLICT",
      "Mon-Thu/Sun 11:00 AM - 9:00 PM; Fri-Sat 11:00 AM - 10:00 PM (Yelp, Jul 2026) vs "
      "Mon-Tue closed (wheree)", True, False, "Santa Clara - " + NOT_CUP + ".", "conflicting",
      [{"label": "Clara's Junction homepage - $19 lunch Wed-Fri 11-3",
        "url": "https://www.clarasjunction.com/"},
       {"label": "Yelp - Clara's Junction (address, phone, Tue 11-9)",
        "url": "https://www.yelp.com/biz/claras-junction-santa-clara"}],
      "https://www.yelp.com/biz/claras-junction-santa-clara", "Clara's Junction 2221 Tasman Dr Santa Clara",
      ["Two material caveats: (1) the $19 special runs Wed-Fri, NOT on the Tuesday trip; "
       "(2) Tuesday open/closed conflicts between Yelp (open) and wheree (closed) - phone "
       "(408) 335-7788 before going."],
      phone="(408) 335-7788"),
    E("L63", "Stick & Wok", "Santa Clara", "Stevens Creek Blvd (Valley Fair)",
      "2855 Stevens Creek Blvd, Ste 2329, Santa Clara, CA 95050", "Chinese (skewers/wok)",
      "Lunch service (no priced special)", None, None, "unknown",
      "Tuesday 11:00 AM - 8:30 PM",
      "No lunch special or prices captured.",
      "11:00 AM - 8:30 PM", "Tuesday 11:00 AM - 8:30 PM (Yelp via search index); rest of "
      "week not captured", True, False, "Santa Clara - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp search - Stick & Wok Santa Clara (address, Tue hours, via search index)",
        "url": yelp_search("Stick & Wok", "Santa Clara, CA")}],
      yelp_search("Stick & Wok", "Santa Clara, CA"), "Stick & Wok 2855 Stevens Creek Santa Clara",
      ["WEAK ROW: single-source hours via the search index - verify by phone before going."]),
    E("L64", "Din Tai Fung", "Santa Clara", "Stevens Creek Blvd (Valley Fair)",
      "2855 Stevens Creek Blvd, Ste 1259, Santa Clara, CA 95050",
      "Taiwanese dumplings / xiao long bao",
      "No lunch special (verified negative)", None, None, "n/a",
      "Tuesday 10:30 AM - 9:30 PM",
      "No lunch special claimed anywhere; listed so the gap is visible.",
      "10:30 AM - 9:30 PM", "Tuesday 10:30 AM - 9:30 PM (directory, via search index); rest "
      "of week not captured", True, False, "Santa Clara - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp search - Din Tai Fung Santa Clara (address, Tue hours, via search index)",
        "url": yelp_search("Din Tai Fung", "Santa Clara, CA")}],
      yelp_search("Din Tai Fung", "Santa Clara, CA"), "Din Tai Fung 2855 Stevens Creek Santa Clara",
      ["Suite 1259 is per a directory listing - confirm on the official site. Hours need a "
       "re-check on the official locations page."]),
    E("L65", "City Pizza", "Campbell", "W Hamilton Ave",
      "888 West Hamilton Ave, Campbell, CA 95008", "Pizza, Italian",
      "Value menu (no lunch-only special)", 6.99, 10.99, "every day (assumed - see flag)",
      "11:00 AM - 9:00 PM",
      "Official menu: gyro $6.99, cheese + 1 topping $8.99, specialty pizzas $10.99, wings "
      "$11.99, salads $6.99-$10.99.",
      "11:00 AM - 9:00 PM", "11:00 AM - 9:00 PM (days not specified on the page; assumed "
      "daily)", True, False, "Campbell - " + NOT_CUP + ".", "official",
      [{"label": "City Pizza official site - menu prices, address, hours",
        "url": "https://www.citypizzacampbell.com/"}],
      yelp_search("City Pizza", "Campbell, CA"), "City Pizza 888 West Hamilton Ave Campbell",
      ["Open days not stated on the official page - Tuesday assumed, phone (408) 370-2489. "
       "Wings price differs between menu blocks ($11.99 vs $12.99)."],
      phone="(408) 370-2489"),
    E("L66", "TGI's Sushi", "Campbell", "W Hamilton Ave",
      "100 W Hamilton Ave, Ste C, Campbell, CA 95008", "Sushi, Japanese",
      "Lunch menu (aggregator prices - re-verify)", None, None, "Mon/Tue/Thu/Fri/Sat",
      "11:30 AM - 2:00/2:30 PM",
      "Lunch menu $13.95-$16.95 per the menupages aggregator (NOT verified on the "
      "restaurant's site).",
      "11:30 AM - 2:30 PM, 4:30 PM - 9:00 PM (Yelp, newest)",
      "Mon/Tue/Thu/Fri/Sat lunch + dinner; Wed and Sun dinner only (Yelp) - restaurantji "
      "and Apple Maps differ on splits/closes", True, False, "Campbell - " + NOT_CUP + ".",
      "listing",
      [{"label": "Yelp - TGI's Sushi Campbell (address, hours)",
        "url": "https://www.yelp.com/biz/tgis-sushi-campbell"},
       {"label": "Restaurantji - TGI's Sushi hours cross-check",
        "url": "https://www.restaurantji.com/ca/campbell/tgi-sushi-/"}],
      "https://www.yelp.com/biz/tgis-sushi-campbell", "TGI's Sushi 100 W Hamilton Ave Campbell",
      ["Lunch prices are aggregator-sourced - confirm on tgisushi.com or by phone (408) "
       "871-0123. Three-way hours conflict; Tuesday lunch 11:30-2+ is agreed."],
      phone="(408) 871-0123"),
    E("L67", "The Breakfast Club", "Campbell", "W Hamilton Ave, Midtown",
      "851 W Hamilton Ave, Campbell, CA 95008", "Breakfast & brunch, American",
      "Brunch menu to 3 PM (no lunch-only special)", 19.0, 30.0, "every day",
      "7:00 AM - 3:00 PM",
      "Brunch dishes $19-$30 per Yelp; kitchen closes 3:00 PM daily.",
      "7:00 AM - 3:00 PM", "every day 7:00 AM - 3:00 PM (official + Yelp agree)", True, False,
      "Campbell - " + NOT_CUP + ".", "mixed",
      [{"label": "Breakfast Club official location page - address, daily 7-3",
        "url": "https://www.bcmidtown.com/location/unnamed-1/"},
       {"label": "Yelp - The Breakfast Club Campbell (hours/prices cross-check)",
        "url": "https://www.yelp.com/biz/the-breakfast-club-campbell"}],
      "https://www.yelp.com/biz/the-breakfast-club-campbell",
      "Breakfast Club 851 W Hamilton Ave Campbell",
      ["Prices are Yelp-sourced, not from the official site. Phone (408) 374-4559."],
      phone="(408) 374-4559"),
    E("L68", "Oak & Rye", "Los Gatos", "N Santa Cruz Ave, downtown",
      "303 N Santa Cruz Ave, Los Gatos, CA 95030", "Pizza, American",
      "Lunch 12-3 Thu-Sun (CLOSED Tuesday)", None, None, "Thu-Sun",
      "12:00 PM - 3:00 PM + dinner",
      "No lunch special or prices captured.",
      "CLOSED on Tuesday (restaurantji + wheree agree)",
      "Mon/Wed 5:00 - 9:00 PM; Tue closed; Thu-Sun 12:00 - 3:00 PM + dinner (to 9/10 PM)",
      False, False, "Closed on the trip day; Los Gatos is off the return path anyway.",
      "listing",
      [{"label": "Restaurantji - Oak & Rye (Tue closed, lunch Thu-Sun)",
        "url": "https://www.restaurantji.com/ca/los-gatos/oak-and-rye-/"},
       {"label": "Wheree - Oak & Rye hours cross-check (Tue closed)",
        "url": "https://oak-rye.wheree.com/"}],
      yelp_search("Oak & Rye", "Los Gatos, CA"), "Oak & Rye 303 N Santa Cruz Ave Los Gatos",
      ["Yellow Pages shows stale daily hours - the two current sources agree Tuesday is "
       "closed. Phone (408) 395-4441."],
      phone="(408) 395-4441", coords=[37.227684, -121.98171],
      coords_source="Yellow Pages listing geo"),
    E("L69", "Willow Street Wood-Fired Pizza", "Los Gatos", "S Santa Cruz Ave, downtown",
      "20 S Santa Cruz Ave, Ste 218, Los Gatos, CA 95030", "Pizza, Italian, New American",
      "Regular menu (no priced special)", None, None, "every day",
      "opens 11:30 AM",
      "Wood-fired pizzas, pastas, salads, sandwiches; no lunch special captured.",
      "11:30 AM - 9:00 PM (Yelp, newest)",
      "every day 11:30 AM - 9:00 PM (newest Yelp; older captures show 8:30 PM closes)",
      True, False, "Los Gatos - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Willow Street Los Gatos (address, daily hours)",
        "url": "https://www.yelp.com/biz/willow-street-wood-fired-pizza-los-gatos-6"}],
      "https://www.yelp.com/biz/willow-street-wood-fired-pizza-los-gatos-6",
      "Willow Street Pizza 20 S Santa Cruz Ave Los Gatos",
      ["Close time drifted between captures (8:30 vs 9:00 PM); lunch unaffected. Official "
       "site willowstreet.com not fetched. Phone (408) 354-5566."],
      phone="(408) 354-5566"),
    E("L70", "Super Duper Burgers", "Los Gatos", "Los Gatos Blvd",
      "15991 Los Gatos Blvd, Bldg 3, Los Gatos, CA 95032", "Burgers, American",
      "Regular menu; happy hour 4-6 PM weekdays (after lunch)", None, None, "every day",
      "opens 10:30 AM",
      "Mini/Super burgers, chicken sandwich, veggie burger, shakes. Official happy hour "
      "Mon-Fri 4-6 PM (free fries with a drink) is after the return bus.",
      "10:30 AM - 9:30 PM (Yelp, newest)",
      "Mon-Thu/Sun 10:30 AM - 9:30 PM; Fri-Sat 10:30 AM - 10:00 PM (newest Yelp; older "
      "captures vary 9:00-10:00 PM)", True, False, "Los Gatos - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Super Duper Burgers Los Gatos (address, hours)",
        "url": "https://www.yelp.com/biz/super-duper-burgers-los-gatos"},
       {"label": "Restaurantji - Super Duper hours cross-check",
        "url": "https://www.restaurantji.com/ca/los-gatos/super-duper-burgers-/"}],
      "https://www.yelp.com/biz/super-duper-burgers-los-gatos",
      "Super Duper Burgers 15991 Los Gatos Blvd Los Gatos",
      ["Close-time conflicts (9:00/9:30/10:00 PM) between captures; lunch unaffected. No "
       "prices captured. Phone (408) 356-0684."],
      phone="(408) 356-0684"),
    E("L71", "La Esquina", "Los Gatos", "N Santa Cruz Ave",
      "551 N Santa Cruz Ave, Los Gatos, CA 95030", "Mexican",
      "Regular menu (no priced special)", None, None, "Mon-Sat (Sun closed)",
      "Tuesday 9:00 AM - 8:00 PM",
      "No lunch special or prices captured.",
      "9:00 AM - 8:00 PM (official)",
      "Mon/Wed/Sat 9:00 AM - 3:00 PM; Tue/Thu/Fri 9:00 AM - 8:00 PM; Sun closed (official)",
      True, False, "Los Gatos - " + NOT_CUP + ".", "official",
      [{"label": "La Esquina official site - address, phone, Tue 9-8 hours",
        "url": "https://www.laesquinamexlosgatos.com/"},
       {"label": "Restaurantji - La Esquina cross-check",
        "url": "https://www.restaurantji.com/ca/los-gatos/la-esquina-/"}],
      yelp_search("La Esquina", "Los Gatos, CA"), "La Esquina 551 N Santa Cruz Ave Los Gatos",
      ["Restaurantji opens an hour later (10 AM) than the official site (9 AM). Phone "
       "(408) 884-8599."],
      phone="(408) 884-8599", coords=[37.2336259, -121.9789257],
      coords_source="Waze place geo"),
    E("L72", "The Bywater", "Los Gatos", "N Santa Cruz Ave",
      "532 N Santa Cruz Ave, Los Gatos, CA 95030", "Cajun/Creole/Southern",
      "Lunch Special, Wed-Fri (CLOSED Tuesday)", None, None, "Wed-Fri (not Tue)",
      "12:00 PM - 9:00 PM (Wed-Fri)",
      "OpenTable notes a Lunch Special; closed Tuesday so not valid on the trip.",
      "CLOSED on Tuesday (official + Yelp agree)",
      "Mon 3:00 - 9:00 PM; Tue closed; Wed-Fri 12:00 - 9:00 PM; Sat 11:00 AM - 9:00 PM; "
      "Sun 11:00 AM - 8:00 PM", False, False,
      "Closed on the trip day; Los Gatos is off the return path anyway.", "official",
      [{"label": "Bywater official site - Tue closed, address, phone",
        "url": "https://www.thebywaterca.com/"},
       {"label": "Yelp - The Bywater (Tue closed cross-check)",
        "url": "https://www.yelp.com/biz/the-bywater-los-gatos"},
       {"label": "OpenTable - The Bywater (Lunch Special note, hours)",
        "url": "https://www.opentable.com/r/the-bywater-los-gatos"}],
      "https://www.yelp.com/biz/the-bywater-los-gatos", "Bywater 532 N Santa Cruz Ave Los Gatos",
      ["Lunch Special exists but Tuesday closure blocks the trip. Phone (408) 560-9639."],
      phone="(408) 560-9639"),
    E("L73", "Italian Brothers Restaurant", "Los Gatos", "N Santa Cruz Ave, downtown",
      "330 N Santa Cruz Ave, Los Gatos, CA 95030", "Italian, pizza",
      "Lunch service 11:30-2:30 (no priced special)", None, None, "Tue-Sun",
      "11:30 AM - 2:30 PM",
      "No lunch special or prices captured.",
      "11:30 AM - 2:30 PM + dinner (restaurantji/Slice) / 11:30 AM - 9:00 PM continuous "
      "(official JSON-LD)",
      "Mon dinner only; Tue-Sun lunch + dinner (splits/closes vary by source)", True, False,
      "Los Gatos - " + NOT_CUP + ".", "official",
      [{"label": "Italian Brothers official site - address, hours JSON-LD",
        "url": "https://www.italianbrothers.restaurant/"},
       {"label": "Restaurantji - Italian Brothers hours cross-check",
        "url": "https://www.restaurantji.com/ca/los-gatos/italian-brothers-restaurant-/"}],
      yelp_search("Italian Brothers", "Los Gatos, CA"), "Italian Brothers 330 N Santa Cruz Ave Los Gatos",
      ["Official page shows continuous hours, directories show a lunch/dinner split; Tuesday "
       "lunch 11:30-2:30 is agreed. Phone (408) 354-0111."],
      phone="(408) 354-0111", coords=[37.2281621, -121.9811058],
      coords_source="Slice ordering page geo"),
    E("L74", "The Pastaria & Market", "Los Gatos", "N Santa Cruz Ave, downtown",
      "27 N Santa Cruz Ave, Los Gatos, CA 95030", "Italian",
      "Lunch service 11:30-3 (no priced special)", None, None, "Tue-Sat",
      "11:30 AM - 3:00 PM",
      "No lunch special or prices captured; still open (closure worry unfounded).",
      "11:30 AM - 3:00 PM, 5:00 PM - 9:00 PM",
      "Mon closed; Tue-Fri 11:30 AM - 3:00 PM / 5:00 - 9:00 PM; Sat 11:30 AM - 9:00 PM; "
      "Sun 2:00 - 8:00 PM (official JSON-LD)", True, False, "Los Gatos - " + NOT_CUP + ".",
      "official",
      [{"label": "Pastaria official menu - address, hours JSON-LD",
        "url": "https://www.thepastaria.com/menu"}],
      yelp_search("Pastaria", "Los Gatos, CA"), "Pastaria 27 N Santa Cruz Ave Los Gatos",
      ["No prices on the official menu page. Phone (408) 399-3477."],
      phone="(408) 399-3477", coords=[37.223506, -121.983772],
      coords_source="official site JSON-LD"),
    E("L75", "The Diner of Los Gatos", "Los Gatos", "Los Gatos-Saratoga Rd",
      "235 Los Gatos Saratoga Rd, Los Gatos, CA 95030", "American diner",
      "All-day diner menu (no priced special)", None, None, "every day",
      "7:00 AM - 9:00 PM",
      "No lunch special or prices captured.",
      "7:00 AM - 9:00 PM", "every day 7:00 AM - 9:00 PM (Yelp, Toast, Wanderlog agree)",
      True, False, "Los Gatos - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Diner of Los Gatos (address, daily 7-9)",
        "url": "https://www.yelp.com/biz/the-diner-of-los-gatos-los-gatos"},
       {"label": "Diner of Los Gatos Toast ordering - address/hours",
        "url": "https://www.toasttab.com/local/order/lgdiner"}],
      "https://www.yelp.com/biz/the-diner-of-los-gatos-los-gatos",
      "Diner of Los Gatos 235 Los Gatos Saratoga Rd",
      ["No prices captured. Phone (408) 354-4886."],
      phone="(408) 354-4886"),
    E("L76", "Lotus Thai Bistro", "Palo Alto", "California Ave",
      "425 California Avenue, Palo Alto, CA", "Thai",
      "Lunch specials Mon-Sat (official; prices TBD)", None, None, "Monday-Saturday",
      "daypart hours not published",
      "Official site confirms lunch specials Mon-Sat and dinner; lunch menu is a linked PDF "
      "that was not fetched.",
      "open Tuesday (hours of day not published)", "Mon-Sat open; Sun closed; closed Labor "
      "Day Mon 9/7/2026 (day before the trip)", True, False,
      "Palo Alto California Ave - " + NOT_CUP + ".", "official",
      [{"label": "Lotus Thai Bistro official site - lunch specials Mon-Sat, address, phone",
        "url": "https://www.lotusthaibistro.com/"}],
      yelp_search("Lotus Thai Bistro", "Palo Alto, CA"), "Lotus Thai Bistro 425 California Ave Palo Alto",
      ["Lunch prices and daypart hours TBD - check the Toast ordering page or phone (650) "
       "289-0907."],
      phone="(650) 289-0907"),
    E("L77", "Sprout Cafe", "Palo Alto", "University Ave, downtown",
      "168 University Ave, Palo Alto, CA 94301", "Californian: salads, sandwiches",
      "Salads/sandwiches (2018 prices - stale)", None, None, "Mon-Sat",
      "10:30 AM - 7:00 PM",
      "2018 menu had salads from $8.45 - eight years old, do not budget.",
      "10:30 AM - 7:00 PM", "Mon-Sat 10:30 AM - 7:00 PM (directory, via search index)",
      True, False, "Downtown Palo Alto - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp search - Sprout Cafe Palo Alto (address, hours, via search index)",
        "url": yelp_search("Sprout Cafe", "Palo Alto, CA")}],
      yelp_search("Sprout Cafe", "Palo Alto, CA"), "Sprout Cafe 168 University Ave Palo Alto",
      ["WEAK ROW: single-source hours via the search index; prices stale (2018). Verify by "
       "phone before going."]),
    E("L78", "La Boheme", "Palo Alto", "California Ave",
      "415 California Avenue, Palo Alto, CA 94306", "French / Californian",
      "Lunch Tue-Fri (official window; no prices)", None, None, "Tuesday-Friday",
      "11:00 AM - 2:00 PM",
      "Official lunch window; no lunch menu prices captured.",
      "11:00 AM - 2:00 PM, 5:00 PM - 9:00 PM",
      "Lunch Tue-Fri 11:00 AM - 2:00 PM; dinner Tue-Sat 5:00 - 9:00 PM; brunch Sat-Sun "
      "9:30 AM - 2:00 PM (official)", True, False, "Palo Alto California Ave - " + NOT_CUP + ".",
      "official",
      [{"label": "La Boheme official homepage - lunch Tue-Fri 11-2, address, phone",
        "url": "https://www.labohemepaloalto.com/"}],
      yelp_search("La Boheme", "Palo Alto, CA"), "La Boheme 415 California Ave Palo Alto",
      ["No lunch prices on the official homepage (no menu page found). Phone (650) 561-3577."],
      phone="(650) 561-3577", coords=[37.4262478, -122.1446999],
      coords_source="Google Maps pin linked from official homepage"),
    E("L79", "Terun Pizzeria", "Palo Alto", "California Ave",
      "448 California Ave, Palo Alto, CA 94306", "Italian / pizza",
      "Lunch (Tuesday lunch CONFLICTED)", None, None, "unknown for Tuesday",
      "conflicted - see flags",
      "Page text says lunch + dinner 7 days; JSON-LD says Mon/Tue dinner only. Tuesday "
      "dinner 5-9 PM is agreed; Tuesday lunch is not.",
      "dinner 5:00 - 9:00 PM agreed; lunch 11:30 AM - 2:00 PM conflicted",
      "conflicting - see Tuesday line", None, False,
      "Tuesday lunch unconfirmed; Palo Alto is off the return path anyway.", "conflicting",
      [{"label": "Terun official site - address; page text vs JSON-LD hours conflict",
        "url": "https://www.terunpizza.com/"},
       {"label": "Yelp search - Terun Palo Alto (hours cross-check)",
        "url": yelp_search("Terun", "Palo Alto, CA")}],
      yelp_search("Terun", "Palo Alto, CA"), "Terun 448 California Ave Palo Alto",
      ["MATERIAL CONFLICT: do not plan a Tuesday lunch without phoning first."]),
    E("L80", "Local Union 271", "Palo Alto", "University Ave, downtown",
      "271 University Ave, Palo Alto, CA 94301", "American farm-to-table, bar",
      "Lunch menu $7-$33.95 (OpenTable block - re-verify)", 7.0, 33.95, "every day",
      "opens 11:30 AM (10:00 AM Sat-Sun)",
      "OpenTable menu block items $7-$33.95; menu URL not retained - re-verify.",
      "11:30 AM - 9:00 PM", "Mon-Wed 11:30 AM - 9:00 PM; Thu-Fri to 10:00 PM; Sat-Sun "
      "10:00 AM - 10:00/9:00 PM (Yelp/Corner; closes vary by capture)", True, False,
      "Downtown Palo Alto - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Local Union 271 (address, hours, phone)",
        "url": "https://www.yelp.com/biz/local-union-271-palo-alto-2"},
       {"label": "Corner - Local Union 271 (hours/address cross-check)",
        "url": "https://www.corner.inc/place/123161"}],
      "https://www.yelp.com/biz/local-union-271-palo-alto-2", "Local Union 271 University Ave Palo Alto",
      ["Menu prices from an OpenTable block whose URL was not retained - re-verify on "
       "OpenTable or localunion271.com. Phone (650) 322-7509."],
      phone="(650) 322-7509"),
    E("L81", "The Post", "Los Altos", "Main St, downtown Los Altos",
      "395 Main St, Los Altos, CA 94022", "American comfort food, cocktail bar",
      "Lunch menu $21-$27 (CLOSED Tuesday)", 21.0, 27.0, "not Tuesday",
      "n/a for the trip",
      "OpenTable menu $21-$27 (URL not retained - re-verify); closed Tuesday.",
      "CLOSED on Tuesday (Yelp, restaurantji, nears.me agree)",
      "Mon/Wed/Thu 11:30 AM - 9:30 PM; Fri to midnight; Sat-Sun 11:00 AM - 9:30/9:00 PM; "
      "Tue closed", False, False, "Closed on the trip day; Los Altos is off the return path.",
      "listing",
      [{"label": "Yelp - The Post Los Altos (Tue closed, address)",
        "url": "https://www.yelp.com/biz/the-post-los-altos"},
       {"label": "Restaurantji - The Post (Tue closed cross-check)",
        "url": "https://www.restaurantji.com/ca/los-altos/the-post-/"}],
      "https://www.yelp.com/biz/the-post-los-altos", "The Post 395 Main St Los Altos",
      ["Menu prices from an OpenTable block whose URL was not retained. Phone (650) 935-2003."],
      phone="(650) 935-2003", coords=[37.377796, -122.1174993],
      coords_source="nears.me listing geo"),
    E("L82", "Urfa Bistro", "Los Altos", "State St, downtown Los Altos",
      "233 State St, Los Altos, CA 94022", "Mediterranean / Turkish / Middle Eastern",
      "Lunch 11-2 daily (no priced special)", None, None, "every day",
      "11:00 AM - 2:00 PM",
      "No lunch special or prices captured.",
      "11:00 AM - 2:00 PM, 5:00 PM - 8:30 PM",
      "Mon/Tue/Sun 11:00 AM - 2:00 PM / 5:00 - 8:30 PM; Wed-Sat dinner to 9:00 PM (Yelp "
      "Sep 2026, restaurantji agree)", True, False, "Los Altos - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Urfa Bistro (address, lunch 11-2 daily)",
        "url": "https://www.yelp.com/biz/urfa-bistro-los-altos"},
       {"label": "Restaurantji - Urfa Bistro hours cross-check",
        "url": "https://www.restaurantji.com/ca/los-altos/urfa-bistro-/"}],
      "https://www.yelp.com/biz/urfa-bistro-los-altos", "Urfa Bistro 233 State St Los Altos",
      ["No prices captured. Phone (650) 397-5614."],
      phone="(650) 397-5614"),
    E("L83", "Aurum", "Los Altos", "State St, downtown Los Altos",
      "132 State St, Los Altos, CA 94022", "Indian, vegan-friendly",
      "Lunch 11:30-2:30 (no priced special)", None, None, "every day",
      "11:30 AM - 2:30 PM (Toast: to 2:15 PM)",
      "No lunch special or prices captured.",
      "11:30 AM - 2:30 PM, 5:00 PM - 9:30 PM",
      "Mon-Thu/Sun 11:30 AM - 2:30 PM / 5:00 - 9:30 PM; Fri-Sat dinner to 10:00 PM "
      "(Toast shows :15/:45 closes)", True, False, "Los Altos - " + NOT_CUP + ".", "listing",
      [{"label": "RestaurantGuru - Aurum (address, hours, geo)",
        "url": "https://restaurantguru.com/Aurum-Los-Altos"},
       {"label": "Restaurantji - Aurum hours cross-check",
        "url": "https://www.restaurantji.com/ca/los-altos/aurum-/"},
       {"label": "Aurum Toast ordering - address/hours",
        "url": "https://www.toasttab.com/local/order/aurumca"}],
      yelp_search("Aurum", "Los Altos, CA"), "Aurum 132 State St Los Altos",
      ["15-minute close-time conflicts (2:15 vs 2:30 PM lunch end); lunch unaffected. Phone "
       "(650) 383-5221."],
      phone="(650) 383-5221", coords=[37.3801424, -122.1156664],
      coords_source="restaurantguru geo fields"),
    E("L84", "Cetrella", "Los Altos", "State St, downtown Los Altos",
      "160 State St, Los Altos, CA 94022", "Mediterranean, cocktail bar",
      "Lunch 11:30-2 Tue-Sun (no priced special)", None, None, "Tue-Sun (Mon closed)",
      "11:30 AM - 2:00 PM",
      "No lunch special or prices captured.",
      "11:30 AM - 2:00 PM, 5:00 PM - 9:00 PM",
      "Mon closed; Tue-Sun 11:30 AM - 2:00 PM / 5:00 - 9:00 PM (newest Yelp; older dinner "
      "close 8:30 PM)", True, False, "Los Altos - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Cetrella (address, Mon closed, Tue lunch)",
        "url": "https://www.yelp.com/biz/cetrella-los-altos"},
       {"label": "Restaurantji - Cetrella hours cross-check",
        "url": "https://www.restaurantji.com/ca/los-altos/cetrella-/"}],
      "https://www.yelp.com/biz/cetrella-los-altos", "Cetrella 160 State St Los Altos",
      ["Dinner close drifted 8:30 -> 9:00 PM between captures; lunch unaffected. Official "
       "site cetrella.com not fetched. Phone (650) 948-0400."],
      phone="(650) 948-0400"),
    E("L85", "La Fontaine", "Mountain View", "Castro St, downtown MV",
      "186 Castro St, Mountain View, CA 94041", "French / Californian",
      "Lunch Tue 11:30-2 (no priced special)", None, None, "unknown",
      "Tuesday 11:30 AM - 2:00 PM, 5:00 PM - 9:30 PM",
      "No lunch special or prices captured.",
      "11:30 AM - 2:00 PM, 5:00 PM - 9:30 PM",
      "Tuesday 11:30 AM - 2:00 PM / 5:00 - 9:30 PM (directory, via search index); rest of "
      "week not captured", True, False, "Downtown MV - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp search - La Fontaine Mountain View (address, Tue hours, via search index)",
        "url": yelp_search("La Fontaine", "Mountain View, CA")}],
      yelp_search("La Fontaine", "Mountain View, CA"), "La Fontaine 186 Castro St Mountain View",
      ["WEAK ROW: single-source hours via the search index - verify by phone before going."]),
    E("L86", "Mediterranean Grill House", "Mountain View", "Castro St, downtown MV",
      "650 Castro St, Unit 110, Mountain View, CA 94041", "Mediterranean",
      "Lunch service (no priced special)", None, None, "unknown",
      "Mon-Wed 11:00 AM - 10:00 PM",
      "No lunch special or prices captured.",
      "11:00 AM - 10:00 PM", "Mon-Wed 11:00 AM - 10:00 PM (official site); rest of week "
      "not captured", True, False, "Downtown MV - " + NOT_CUP + ".", "official",
      [{"label": "Mediterranean Grill House official site - address, hours",
        "url": "https://mediterraneangrillhouse.com/"},
       {"label": "Yelp search - Mediterranean Grill House cross-check",
        "url": yelp_search("Mediterranean Grill House", "Mountain View, CA")}],
      yelp_search("Mediterranean Grill House", "Mountain View, CA"),
      "Mediterranean Grill House 650 Castro St Mountain View",
      ["Thu-Sun hours not captured; no prices. Verify by phone."]),
    E("L87", "Cascal", "Mountain View", "Castro St, downtown MV",
      "400 Castro St, Mountain View, CA 94041", "Latin / Spanish",
      "Lunch 11:30-3 (no priced special)", None, None, "unknown",
      "11:30 AM - 3:00 PM",
      "No lunch special or prices captured.",
      "lunch 11:30 AM - 3:00 PM (directory, via search index)",
      "lunch 11:30 AM - 3:00 PM; full dayparts not captured", True, False,
      "Downtown MV - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp search - Cascal Mountain View (address, lunch window, via search index)",
        "url": yelp_search("Cascal", "Mountain View, CA")}],
      yelp_search("Cascal", "Mountain View, CA"), "Cascal 400 Castro St Mountain View",
      ["WEAK ROW: single-source lunch window via the search index - verify by phone."]),
    E("L88", "Ludwig's Biergarten", "Mountain View", "Castro St, downtown MV",
      "383 Castro St, Mountain View, CA 94041", "German / beer garden",
      "Lunch service (no priced special)", None, None, "Tue-Sun (Mon closed per press)",
      "11:30 AM - 9:00 PM",
      "No lunch special or prices captured; under new ownership since Oct 2024.",
      "11:30 AM - 9:00 PM (press) / 11:30 AM - 10:00 PM (official Sun-Thu)",
      "Tue-Fri 11:30 AM - 9:00 PM; Sat 12:00 - 10:00 PM; Sun 11:30 AM - 8:00 PM "
      "(paloaltoonline, Oct 2024) vs Sun-Thu 11:30 AM - 10:00 PM (official site)", True, False,
      "Downtown MV - " + NOT_CUP + ".", "listing",
      [{"label": "Palo Alto Online - Ludwig's address, phone, hours",
        "url": "https://www.paloaltoonline.com/mountain-view/2024/10/07/ludwigs-mountain-view-transitions-to-new-ownership-under-creative-collective-founder-gisela-qasim/"},
       {"label": "Ludwig's official site - hours Sun-Thu 11:30-22",
        "url": "https://ludwigsmv.com/"}],
      yelp_search("Ludwig's Biergarten", "Mountain View, CA"), "Ludwig's Biergarten 383 Castro St Mountain View",
      ["Hours conflict between 2024 press and the official site (Mon/Fri/close times); "
       "Tuesday lunch 11:30 AM is agreed. Phone (650) 282-5342."],
      phone="(650) 282-5342"),
    E("L89", "Don Giovanni's", "Mountain View", "Castro St, downtown MV",
      "235 Castro St, Mountain View, CA 94041", "Italian",
      "Lunch Tue-Fri (no priced special)", None, None, "Tuesday-Friday",
      "11:30 AM - 2:00 PM",
      "No lunch special or prices captured.",
      "11:30 AM - 2:00 PM + dinner", "lunch Tue-Fri 11:30 AM - 2:00 PM (official site); "
      "full week not captured", True, False, "Downtown MV - " + NOT_CUP + ".", "official",
      [{"label": "Don Giovanni official site - address, Tue-Fri lunch",
        "url": "https://dongiovannis.com/"},
       {"label": "Yelp search - Don Giovanni cross-check",
        "url": yelp_search("Don Giovanni", "Mountain View, CA")}],
      yelp_search("Don Giovanni", "Mountain View, CA"), "Don Giovanni 235 Castro St Mountain View",
      ["Dinner hours and prices not captured - verify by phone."]),
    E("L90", "Toki Sushi", "Mountain View", "N Shoreline Blvd",
      "570 N Shoreline Blvd, Suite J, Mountain View, CA 94043", "Japanese: sushi, bento",
      "Bento specials", 8.95, None, "every day", "11:30 AM - 3:00 PM",
      "MV Voice (Dec 2025): bentos from $8.95. An atly reviewer says $13 - conflict, see flags.",
      "11:30 AM - 3:00 PM, 5:00 PM - 9:00 PM",
      "Mon-Thu 11:30 AM - 3:00 PM / 5:00 - 9:00 PM; Fri-Sun 11:30 AM - 9:30 PM (MV Voice) "
      "vs daily split to 9:00 PM (Toast)", True, False, "Mountain View - " + NOT_CUP + ".",
      "listing",
      [{"label": "MV Voice - Toki Sushi address, phone, hours, $8.95 bento",
        "url": "https://www.mv-voice.com/mountain-view/2025/12/09/this-new-japanese-restaurant-offers-bentos-for-just-8-95/"},
       {"label": "Toki Sushi Toast ordering - address/hours",
        "url": "https://www.toasttab.com/local/order/toki-sushi-570-n-shoreline-blvd-suite-j"}],
      yelp_search("Toki Sushi", "Mountain View, CA"), "Toki Sushi 570 N Shoreline Blvd Mountain View",
      ["Bento price conflicts ($8.95 press Dec 2025 vs $13 reviewer) - confirm at the counter. "
       "Fri-Sun close conflicts (9:00 vs 9:30 PM). Phone (650) 887-6368."],
      phone="(650) 887-6368"),
    E("L91", "Kakaroto Japanese Restaurant", "Mountain View", "W Dana St, downtown MV",
      "743 W Dana St, Mountain View, CA 94041", "Japanese",
      "Lunch 11:30-2:30 (no priced special)", None, None, "Tue-Sun (Mon closed)",
      "11:30 AM - 2:30 PM",
      "No lunch special or prices captured.",
      "11:30 AM - 2:30 PM, 5:00 PM - 9:00 PM",
      "Mon closed; Tue-Thu/Sun 11:30 AM - 2:30 PM / 5:00 - 9:00 PM; Fri-Sat dinner to "
      "9:30 PM (Yelp)", True, False, "Downtown MV - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Kakaroto (address, Mon closed, Tue lunch)",
        "url": "https://www.yelp.com/biz/kakaroto-japanese-restaurant-mountain-view"}],
      "https://www.yelp.com/biz/kakaroto-japanese-restaurant-mountain-view",
      "Kakaroto 743 W Dana St Mountain View",
      ["No prices captured. Phone (650) 903-9668."],
      phone="(650) 903-9668"),
    E("L92", "Erik's DeliCafe", "Mountain View", "Grant Rd",
      "1350 Grant Rd, Suite 18, Mountain View, CA 94040", "Deli: sandwiches, salads, soups",
      "Deli lunch (no priced special)", None, None, "every day",
      "opens 9:00 AM weekdays",
      "No lunch special or prices captured.",
      "9:00 AM - 8:00 PM", "Mon-Fri 9:00 AM - 8:00 PM; Sat-Sun 10:00 AM - 7:00 PM (official)",
      True, False, "Mountain View - " + NOT_CUP + ".", "official",
      [{"label": "Erik's DeliCafe official locations - Grant Rd address/hours",
        "url": "https://www.eriksdelicafe.com/locations/"}],
      yelp_search("Erik's DeliCafe", "Mountain View, CA"), "Erik's DeliCafe 1350 Grant Rd Mountain View",
      ["No prices on the locations page. Phone (650) 962-9191."],
      phone="(650) 962-9191"),
    E("L93", "Erik's DeliCafe", "Mountain View", "Charleston Rd",
      "2424 Charleston Rd, Mountain View, CA 94043", "Deli: sandwiches, salads, soups",
      "Deli lunch (no priced special)", None, None, "every day",
      "opens 10:00 AM (11:00 AM Sun)",
      "No lunch special or prices captured.",
      "10:00 AM - 7:00 PM", "Mon-Sat 10:00 AM - 7:00 PM; Sun 11:00 AM - 6:00 PM (official)",
      True, False, "Mountain View - " + NOT_CUP + ".", "official",
      [{"label": "Erik's DeliCafe official locations - Charleston Rd address/hours",
        "url": "https://www.eriksdelicafe.com/locations/"}],
      yelp_search("Erik's DeliCafe", "Mountain View, CA"), "Erik's DeliCafe 2424 Charleston Rd Mountain View",
      ["No prices on the locations page. Phone (650) 962-1212."],
      phone="(650) 962-1212"),
    E("L94", "Tony & Alba's Pizza & Pasta", "San Jose", "Stevens Creek Blvd",
      "3137 Stevens Creek Blvd, San Jose, CA", "Italian: pizza, pasta",
      "Regular menu (August combo deal EXPIRED)", 9.99, 24.50, "Tue-Sun (Mon closed)",
      "Tuesday 11:00 AM - 8:15 PM",
      "Official menu: garlic bread $9.99, Italian salad $12.50, cheese/BYOB pizza $19+, "
      "specialty pizzas $24.50+, meat sauce pasta + meatballs $22+. The $45 'Back To School' "
      "combo was Tue-Thu through August only - expired before Sep 8.",
      "11:00 AM - 8:15 PM", "Mon closed; Tue-Sun from 11:00 AM (Tue to 8:15 PM per "
      "directory, via search index)", True, False, "West San Jose - " + NOT_CUP + ".",
      "official",
      [{"label": "Tony & Alba official menu - prices, address, Tue 11 AM open",
        "url": "https://tonyandalbaspizza.com/menu"},
       {"label": "Tony & Alba official homepage - hours",
        "url": "https://tonyandalbaspizza.com/"}],
      yelp_search("Tony & Alba's", "San Jose, CA"), "Tony & Alba's 3137 Stevens Creek Blvd San Jose",
      ["No active lunch special - the August combo expired. Full weekly hours not captured."]),
    E("L95", "Soong Soong", "San Jose", "Stevens Creek Blvd",
      "3680 Stevens Creek Blvd, Unit C, San Jose, CA", "Chinese (Taiwanese-style)",
      "Lunch Tue 11-2:30 (no priced special)", None, None, "Tue-Sun (Wed closed)",
      "Tuesday 11:00 AM - 2:30 PM",
      "No lunch special or prices captured.",
      "lunch 11:00 AM - 2:30 PM (official site)", "Tue lunch 11:00 AM - 2:30 PM; Wed "
      "closed (official site); full week not captured", True, False,
      "West San Jose - " + NOT_CUP + ".", "official",
      [{"label": "Soong Soong official site - address, Tue lunch, Wed closed",
        "url": "https://soongsoong.com/"},
       {"label": "Yelp search - Soong Soong cross-check",
        "url": yelp_search("Soong Soong", "San Jose, CA")}],
      yelp_search("Soong Soong", "San Jose, CA"), "Soong Soong 3680 Stevens Creek Blvd San Jose",
      ["Dinner hours and prices not captured - verify by phone."]),
    E("L96", "Freedom Burrito", "San Jose", "Stevens Creek Blvd",
      "5239 Stevens Creek Blvd, San Jose, CA 95128 (site text says Santa Clara - conflict)",
      "Mexican: burritos",
      "All-day menu 8-10 (no priced special)", None, None, "every day (assumed)",
      "8:00 AM - 10:00 PM",
      "No lunch special or prices captured.",
      "8:00 AM - 10:00 PM", "Tuesday 8:00 AM - 10:00 PM (official site); rest of week not "
      "captured", True, False, "Stevens Creek corridor - " + NOT_CUP + ".", "conflicting",
      [{"label": "Freedom Burrito official site - address, Tue 8-22 hours",
        "url": "https://freedomburrito.com/"},
       {"label": "Yelp search - Freedom Burrito city/hours cross-check",
        "url": yelp_search("Freedom Burrito", "San Jose, CA")}],
      yelp_search("Freedom Burrito", "San Jose, CA"), "Freedom Burrito 5239 Stevens Creek Blvd",
      ["CITY CONFLICT: official site says Santa Clara but 95128 is a San Jose postcode - "
       "verify the city before navigating. Prices not captured."]),
    E("L97", "Falafel's Drive-In", "San Jose", "Stevens Creek Blvd",
      "2301 Stevens Creek Blvd, San Jose, CA 95128", "Middle Eastern / falafel",
      "Falafel + banana shake combo", 7.50, 14.00, "every day",
      "10:00 AM - 8:00 PM (Sun to 6:00 PM)",
      "Ordering menu: small falafel $7.50, large falafel $9.50, large falafel + banana shake "
      "$14.00, hummus $8.75, fries $5.50.",
      "10:00 AM - 8:00 PM", "Mon-Sat 10:00 AM - 8:00 PM; Sun 10:00 AM - 6:00 PM (Yelp, "
      "restaurantguru agree)", True, False, "West San Jose - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Falafel's Drive-In (address, weekly hours)",
        "url": "https://www.yelp.com/biz/falafels-drive-in-san-jose"},
       {"label": "Falafel's online ordering menu - sandwich/shake prices",
        "url": "https://order.online/store/falafels-drive-in-31486"}],
      "https://www.yelp.com/biz/falafels-drive-in-san-jose",
      "Falafel's Drive-In 2301 Stevens Creek Blvd San Jose",
      ["WARNING: falafels-drive-in.com looks official but states it is a user-generated fan "
       "site - do not cite it. Phone (408) 294-7886."],
      phone="(408) 294-7886", coords=[37.3237033, -121.9350772],
      coords_source="restaurantguru geo fields"),
    E("L98", "Kongunadu", "San Jose", "S De Anza Blvd, West San Jose",
      "1136 S De Anza Blvd, Ste A, San Jose, CA 95129", "South Indian (Kongunadu)",
      "Thali lunch (reviewer $24.99)", 24.99, None, "every day",
      "11:00 AM - 10:30 PM",
      "Reviewer figure: thali $24.99. No published menu prices captured.",
      "11:00 AM - 10:30 PM", "every day 11:00 AM - 10:30 PM (Yelp)", True, False,
      "West San Jose near the Cupertino border - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp - Kongunadu (address, phone, daily hours)",
        "url": "https://www.yelp.com/biz/kongunadu-san-jose-7"}],
      "https://www.yelp.com/biz/kongunadu-san-jose-7", "Kongunadu 1136 S De Anza Blvd San Jose",
      ["Not in Cupertino despite lunch-list placement - West San Jose 95129. Price is a "
       "reviewer figure; official site kongunadu.us not fetched. Phone (669) 251-7262."],
      phone="(669) 251-7262"),
    E("L99", "Pacific Catch", "Cupertino", "Stevens Creek Blvd",
      "19399 Stevens Creek Blvd, Ste 5, Cupertino, CA 95014", "Seafood, tacos, sushi bar",
      "Regular menu (no lunch-only special)", 10.0, 15.0, "every day",
      "11:00 AM - 9:00 PM",
      "Reviewer $10-$15 lunch range; happy hour Mon-Fri 3-6 PM is after the return bus.",
      "11:00 AM - 9:00 PM",
      "Mon-Thu/Sun 11:00 AM - 9:00 PM; Fri-Sat 11:00 AM - 10:00 PM (3 sources agree)",
      True, True, "Open from 11 AM on Stevens Creek Blvd; see computed distance.",
      "listing",
      [{"label": "Restaurantji - Pacific Catch Cupertino (address, hours)",
        "url": "https://www.restaurantji.com/ca/cupertino/pacific-catch-/"},
       {"label": "usmenuguide - Pacific Catch hours/happy-hour cross-check",
        "url": "https://usmenuguide.com/places/united-states/california/cupertino/pacific-catch-cupertino/"}],
      yelp_search("Pacific Catch", "Cupertino, CA"), "Pacific Catch 19399 Stevens Creek Blvd Cupertino",
      ["Price is a reviewer range; official page pacificcatch.com/locations/cupertino/ not "
       "fetched. Phone (408) 899-2604."],
      phone="(408) 899-2604", coords=[37.3235661, -122.0101751],
      coords_source="usmenuguide listing geo"),
    E("L100", "Hong's Gourmet", "Saratoga", "Big Basin Way, downtown Saratoga",
      "14510 Big Basin Way, Ste 9, Saratoga, CA 95070", "Chinese",
      "Lunch service (Yelp menu dishes $8-$37)", 8.0, 37.0, "unknown",
      "Tuesday 11:30 AM - 2:30 PM, 5:00 PM - 9:00 PM",
      "Yelp menu dishes $8-$37; no lunch-only special identified.",
      "11:30 AM - 2:30 PM, 5:00 PM - 9:00 PM",
      "Tuesday 11:30 AM - 2:30 PM / 5:00 - 9:00 PM (Yelp via search index); rest of week "
      "not captured", True, False, "Saratoga - " + NOT_CUP + ".", "listing",
      [{"label": "Yelp search - Hong's Gourmet Saratoga (address, Tue hours, menu prices)",
        "url": yelp_search("Hong's Gourmet", "Saratoga, CA")}],
      yelp_search("Hong's Gourmet", "Saratoga, CA"), "Hong's Gourmet 14510 Big Basin Way Saratoga",
      ["WEAK ROW: single-source hours/prices via the search index - verify by phone."]),
    E("L101", "GOGA Restaurant", "Saratoga", "Big Basin Way, downtown Saratoga",
      "14443 Big Basin Way, Unit C, Saratoga, CA 95070", "Hawaiian / Asian fusion",
      "Lunch (hours UNCERTAIN)", None, None, "unknown",
      "conflicted - see flags",
      "Small family restaurant with a changing menu; no prices captured.",
      "11:00 AM - 2:30 PM / 5:30 - 9:00 PM (Yelp) vs CLOSED Mon-Tue per map.contact - "
      "CONFLICT",
      "conflicting - Tuesday lunch unconfirmed", False, False,
      "Tuesday hours unconfirmed - call (408) 656-8315 before considering.", "conflicting",
      [{"label": "Nextdoor - GOGA address/phone",
        "url": "https://nextdoor.com/pages/indo-cafe/"},
       {"label": "Map.contact - GOGA address/hours (conflicts with Yelp)",
        "url": "https://map.contact/goga-saratoga-california"}],
      yelp_search("GOGA", "Saratoga, CA"), "GOGA 14443 Big Basin Way Saratoga",
      ["MATERIAL CONFLICT: Yelp-style hours vs closed-Mon-Tue - Tuesday lunch unconfirmed. "
       "open_on_trip_date set false until verified."],
      phone="(408) 656-8315", coords=[37.2586086, -122.0331341],
      coords_source="Nextdoor business geo"),
]

assert len(NEW) == 54
specials["entries"].extend(NEW)

specials["search_protocol"]["queries_run"] = 94
specials["search_protocol"]["candidates_found"] = 126
specials["search_protocol"]["added_to_master"] = 101
specials["search_protocol"]["rejected_or_deferred"] = 28
specials["search_protocol"]["cities_covered"].extend(["Mountain View", "Saratoga"])
specials["search_protocol"]["radius_note"] = (
    "Cupertino first, then the 10-15 mi radius (Sunnyvale, Santa Clara, Campbell, West San "
    "Jose, Mountain View, Los Altos, Palo Alto, Los Gatos, Saratoga); far entries are marked "
    "and do not fit the return bus.")
specials["search_protocol"]["notes"].append(
    "2026-09-07 batch 3: 54 new master rows L48-L101 (46 queries: 12 city sweeps + 34 "
    "single-business resolutions). Tue-closed: Oak & Rye, Bywater, The Post. Rejected this "
    "batch: Pluto's (closure report), Halal Street (closed), MacArthur Park + The Basin "
    "(dinner-only).")
save("lunch_specials.json", specials)

# ---------------------------------------------------------------- rejected
rejected = load("lunch_rejected.json")
rejected["rejected"].extend([
    {"id": "R15", "count": 1, "names": ["Pluto's"],
     "name": "Pluto's", "city": "Palo Alto",
     "why": "Closure conflict - menupix reports the University Ave store permanently closed "
            "while Yellow Pages and a directory still show Mon-Fri 11-10 hours. Excluded until "
            "open/closed status is confirmed.",
     "price_hint": "none usable",
     "links": [
         {"label": "menupix - reported permanently closed",
          "url": "https://www.menupix.com/sanmateo/restaurants/5505778/Plutos-Fresh-Food-Palo-Alto-CA"},
         {"label": "Yellow Pages - still lists hours",
          "url": "https://www.yellowpages.com/palo-alto-ca/mip/plutos-633098"}]},
    {"id": "R16", "count": 1, "names": ["Halal Street Xinjiang Cuisine"],
     "name": "Halal Street Xinjiang Cuisine", "city": "Mountain View",
     "why": "Yelp marks both listings CLOSED (174 Castro St). The $24.95 AYCE lunch figure is moot.",
     "price_hint": "$24.95 AYCE lunch (atly listing, moot - closed)",
     "links": [
         {"label": "Yelp - Halal Street (CLOSED)",
          "url": "https://www.yelp.com/biz/halal-street-xinjiang-cuisine-mountain-view"}]},
    {"id": "R17", "count": 2, "names": ["MacArthur Park", "The Basin"],
     "name": "MacArthur Park, The Basin", "city": "Palo Alto / Saratoga",
     "why": "Dinner-only, no lunch service: MacArthur Park Palo Alto (27 University Ave) Tue "
            "4:30-9:00 PM; The Basin Saratoga Mon-Sun 5:00 PM-close.",
     "price_hint": "n/a - dinner only",
     "links": [
         {"label": "MacArthur Park official site (dinner hours)",
          "url": "https://macpark.com/"},
         {"label": "Yelp search - The Basin Saratoga (dinner-only, via search index)",
          "url": "https://www.yelp.com/search?find_desc=The+Basin&find_loc=Saratoga%2C+CA"}]},
])
rejected["distinct_businesses_rejected"] = 28
rejected["note"] = ("17 rows covering 28 distinct businesses; R14 groups the near-miss "
                    "candidates surfaced by the same queries and rejected for the same reason "
                    "(no published lunch special found in this pass).")
save("lunch_rejected.json", rejected)

# ---------------------------------------------------------------- flags
flags = load("flags.json")
flags["transit"][1]["what_we_did"] = (
    "Re-verified 2026-09-07: the bulletin (9-minute peak) is treated as authoritative; the N "
    "Judah route-page frequency table still shows 10 minutes, so re-check on the evening of "
    "9/7. Times were read from the live SFMTA timetable pages for 20260908.")
flags["transit"].extend([
    {"id": "FLAG-10", "severity": "important",
     "title": "Transfer credit corrected: $0.50 TO Muni only, not $2.85",
     "what_we_found": ("No official source supports the earlier $2.85 credit or any "
        "Muni-to-Caltrain credit. Caltrain's regional-transfer-discounts page: $0.50 off Muni "
        "within 1 hour of tagging off Caltrain (tag on and off, Clipper cash value or a "
        "monthly pass including Zone 1; the SFMTA table also shows contactless as eligible). "
        "A Jan-2026 Reddit thread claiming free regional transfers under Clipper 2.0 "
        "contradicts both agencies' current pages and was not used."),
     "what_we_did": ("Return Muni leg set to $2.35; return Clipper totals $11.00 -> $13.35; "
        "cheapest day-total $24.85 -> $27.20. Re-check the Caltrain discounts page on 9/7 in "
        "case Clipper 2.0 changes land."),
     "link": "https://www.caltrain.com/fares/regional-transfer-discounts",
     "rows": [], "link_label": "open the agency page"},
    {"id": "FLAG-11", "severity": "note",
     "title": "Westbound Judah & 19th Ave stop is 15199, not 15201",
     "what_we_found": ("The N Judah schedule pages show westbound Judah & 19th Ave as stop "
        "15199; 15201 is Judah & 22nd Ave. The error was only in the stop number, not in any time."),
     "what_we_did": "Return legs updated to 15199; eastbound boarding stop 15200 is unchanged.",
     "link": "https://www.sfmta.com/routes/schedule/N?direction_id=0",
     "rows": [], "link_label": "open the agency page"},
    {"id": "FLAG-12", "severity": "note",
     "title": "MuniMobile Single Ride passes discontinued Sep 1 2026",
     "what_we_found": ("The SFMTA single-ride page: MuniMobile Single Ride passes ended Sep 1 "
        "2026, one week before the trip."),
     "what_we_did": ("Fare table updated: on Sep 8 a Muni single ride is Clipper/contactless "
        "($2.85) or cash/TVM ($3.00)."),
     "link": "https://www.sfmta.com/fares/single-ride-adult-ages-19-64",
     "rows": [], "link_label": "open the agency page"},
])
flags["lunch"].append({
    "id": "LUNCH-FLAG-11", "severity": "note",
    "title": "Third search batch (54 new rows L48-L101) - deals, Tue closures, conflicts",
    "what_we_found": (
        "Priced lunch specials newly verified: Ginger Cafe $16-$19 (official), Home Eat Santa "
        "Clara $12.99-$14.99 (official), Dusita Thai $13.75 (reviewer), Toki Sushi bento $8.95 "
        "press vs $13 reviewer, TGI's Sushi $13.95-$16.95 (aggregator - re-verify), Clara's "
        "$19 two-course Wed-Fri only (NOT Tuesday), Mastro's lunch from noon (price band to "
        "re-verify). Updates: Home Eat Cupertino floor $12.99 (L03), Galpao official lunch "
        "$46/$59 (L36), Gardenia Mon-closed resolved (L21). Tue-closed: Oak & Rye, Bywater, "
        "The Post (open_on_trip_date=false). Material conflicts: Clara's Tue hours (Yelp open "
        "vs wheree closed), GOGA hours (Tue lunch unconfirmed), Terun Tue lunch (page text vs "
        "JSON-LD), Country Gourmet hours (3 PM vs 9 PM close), Freedom Burrito city/postcode "
        "(site says Santa Clara, 95128 is San Jose). Near-misses folded in, not rows: a "
        "'Saratoga Restaurant Week' hit was Saratoga County NY; Cato's Tacos / El Califas are "
        "trucks with no fixed weekday hours. Warnings: falafels-drive-in.com is a fan site, "
        "not official; Mastro's Santa Clara is a Steakhouse, not an Ocean Club; pholyfe.com "
        "returned HTTP 500. Weak single-source rows needing phone verification: Stick & Wok, "
        "Sprout Cafe, La Fontaine, Cascal, Hong's Gourmet."),
    "what_we_did": ("All 54 added with verification levels and source links; weak rows marked "
                    "'listing' with call-ahead flags; Tue-closed rows kept visible with "
                    "open_on_trip_date=false per the Jake's/Curry Hyuga precedent."),
    "link": "",
    "rows": ["L%02d" % i for i in range(48, 102)],
    "link_label": "open the agency page",
})
flags["updated"] = ACC
save("flags.json", flags)

# ---------------------------------------------------------------- sources
sources = load("sources.json")
for s in sources["sources"]:
    if s["id"] == "S6":
        s["used_for"] = ("Single Ride $2.85 / cash $3.00 / 120 min; Day Pass $5.70; Monthly $86; "
                         "youth 18 and under free; $0.50 inter-agency credit when transferring TO "
                         "Muni from Caltrain within 1 hour; MuniMobile Single Ride passes "
                         "discontinued Sep 1 2026")
    if s["id"] == "S12":
        s["used_for"] = s["used_for"].replace("youth $1/$2/$24", "youth $1 flat all zones")
    if s["id"] == "S15":
        s["used_for"] += ("; re-verified 2026-09-07: SB Sunnyvale TC 7:40 -> De Anza & Homestead "
                          "7:55 -> Stelling 8:03, TC 9:59 -> Stelling 10:20; NB Stelling 11:31 -> "
                          "TC 11:55 (early-backup row)")
sources["sources"].extend([
    {"id": "S31", "agency": "Caltrain",
     "label": "Regional transfer discounts ($0.50 TO Muni only)",
     "url": "https://www.caltrain.com/fares/regional-transfer-discounts",
     "fetch_status": "ok",
     "used_for": ("$0.50 credit TO Muni within 1 hr of Caltrain tag-off (tag on/off, Clipper cash "
                  "value or monthly incl. Zone 1); VTA/SamTrans credits need a monthly pass; no "
                  "Muni-to-Caltrain credit exists")},
    {"id": "S32", "agency": "SFMTA",
     "label": "Adult single-ride fares + MuniMobile Single Ride discontinuation",
     "url": "https://www.sfmta.com/fares/single-ride-adult-ages-19-64",
     "fetch_status": "ok",
     "used_for": ("$2.85 Clipper/contactless, $3.00 cash, 120-min transfer; MuniMobile Single "
                  "Ride passes discontinued Sep 1 2026")},
    {"id": "S33", "agency": "Yelp",
     "label": "Batch-3 Yelp pages (hours/addresses/phones)",
     "url": "https://www.yelp.com/biz/pho-lyfe-sunnyvale-2",
     "fetch_status": "ok via search index",
     "used_for": ("day-by-day hours, addresses, phones for Pho Lyfe, Cam Hung, Home Eat SC, "
                  "Dusita, Il Fornaio, Falafel's, Breakfast Club, TGI's, Willow Street, Super "
                  "Duper, Bywater, The Post, Urfa, Cetrella, Kongunadu, Clara's Junction, Diner "
                  "of LG, Local Union 271, Kakaroto")},
    {"id": "S34", "agency": "Third party (not used for prices)",
     "label": "Batch-3 restaurantji pages (hours/addresses)",
     "url": "https://www.restaurantji.com/ca/sunnyvale/thai-spoons-/",
     "fetch_status": "ok",
     "used_for": ("hours/address cross-checks for Thai Spoons, First Wok, Asia Village, Dumpling "
                  "Depot, 10 Butchers, Dusita, TGI's, Oak & Rye, La Esquina, Italian Brothers, "
                  "Super Duper, The Post, Urfa, Aurum, Cetrella, Pacific Catch")},
    {"id": "S35", "agency": "Restaurant (official)",
     "label": "Batch-3 official restaurant sites (lunch prices, hours, addresses)",
     "url": "https://gingercafe.net/menus/lunchmenu/",
     "fetch_status": "ok",
     "used_for": ("lunch prices/hours/address from gingercafe.net, clarasjunction.com, "
                  "citypizzacampbell.com, tonyandalbaspizza.com, lotusthaibistro.com, "
                  "labohemepaloalto.com, thepastaria.com, laesquinamexlosgatos.com, "
                  "thebywaterca.com, italianbrothers.restaurant, bcmidtown.com, "
                  "dusitathaicuisine.com menu PDF, dumplingdepot-s.com, eriksdelicafe.com, "
                  "mastrosrestaurants.com, mediterraneangrillhouse.com, dongiovannis.com, "
                  "soongsoong.com, freedomburrito.com, terunpizza.com (conflict), ludwigsmv.com "
                  "(conflict)")},
    {"id": "S36", "agency": "Third party (not used for prices)",
     "label": "Batch-3 directories and press (hours/geo cross-checks)",
     "url": "https://restaurantguru.com/Asia-Village-Sunnyvale",
     "fetch_status": "ok",
     "used_for": ("restaurantguru, wheree, Yellow Pages, Tripadvisor, corner.inc, Toast ordering, "
                  "Chowbus, smorefood, zmenu, Slice, usmenuguide, showmelocal, Nextdoor, "
                  "map.contact, MV Voice (Toki $8.95 bento), Palo Alto Online (Ludwig's)")},
    {"id": "S37", "agency": "OpenTable",
     "label": "Batch-3 OpenTable menu/hours blocks",
     "url": "https://www.opentable.com/r/the-bywater-los-gatos",
     "fetch_status": "ok via search index",
     "used_for": ("menu price bands ($7-$33.95 Local Union 271, $21-$27 The Post - both flagged "
                  "for re-verification) and the Bywater Lunch Special note")},
])
save("sources.json", sources)

# ---------------------------------------------------------------- README + docs
readme = os.path.join(ROOT, "README.md")
with open(readme, encoding="utf-8") as fh:
    text = fh.read()
text = text.replace(
    "| **Cost** | **$24.85** round trip with Clipper/contactless (adult), $27.70 without the transfer credit, $31.00 all cash |",
    "| **Cost** | **$27.20** round trip with Clipper/contactless (adult; includes the $0.50 Caltrain-to-Muni credit), $27.70 without the credit, $31.00 all cash |")
text = text.replace(
    "data/lunch_specials.json    47 lunch entries (27 original + 20 new 2026-09-07 batch), hours, days, prices, verification level",
    "data/lunch_specials.json    101 lunch entries (27 original + 20 batch-2 + 54 batch-3, all 2026-09-07), hours, days, prices, verification level")
text = text.replace(
    "data/lunch_rejected.json    24 rejected/deferred candidates (14 rows), each with a reason and a link",
    "data/lunch_rejected.json    28 rejected/deferred candidates (17 rows), each with a reason and a link")
text = text.replace(
    "data/flags.json             18 irregularities found while verifying - all still listed",
    "data/flags.json             23 irregularities found while verifying - all still listed")
text = text.replace(
    "data/sources.json           27 source pages, what each one proved, and the fetch status",
    "data/sources.json           37 source pages, what each one proved, and the fetch status")
text = text.replace("## Flagged irregularities (19)", "## Flagged irregularities (23)")
text = text.replace("Nine transit, ten lunch. Headlines:", "Twelve transit, eleven lunch. Headlines:")
with open(readme, "w", encoding="utf-8") as fh:
    fh.write(text)

verif = os.path.join(ROOT, "docs", "VERIFICATION.md")
with open(verif, encoding="utf-8") as fh:
    vtext = fh.read()
vtext = vtext.replace("the $2.85 Muni credit", "the $0.50 Muni credit")
vtext = vtext.replace("so the $2.85 credit applies", "so the $0.50 credit applies")
with open(verif, "w", encoding="utf-8") as fh:
    fh.write(vtext)

print("batch-3 updates applied: transit/fares/plan, L03/L36/L21/L19/L40, 54 new rows,")
print("3 rejected rows, 4 new flags, 7 new sources, protocol counters, README + docs.")
