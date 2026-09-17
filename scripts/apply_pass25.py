#!/usr/bin/env python3
"""Pass 25 (2026-09-17): evidence-first lunch pass, applied programmatically.

What this pass changes, and the evidence behind each change:

  * removes 5 rows proven to be duplicates of rows already in the master list,
    recording the proof next to each removal;
  * upgrades 3 existing Cupertino rows with field-level evidence read from pages
    the restaurant itself controls (deal_audit);
  * adds 1 net-new business (Calcutta Chaat & Bakery, Milpitas) whose own site
    publishes a priced lunch special;
  * files 6 rejections for businesses newly screened this pass that publish no
    lunch special on any page they control;
  * files 10 flags, including the systematic batch-13b duplicate/address pattern;
  * writes the pass-25 evidence table and search log.

Nothing here invents a value. Every claimed field carries the URL it was read
from, the excerpt that was read, and the method used to read it. Fields that were
not published stay unknown and are counted as gaps, not filled in.

    python3 scripts/apply_pass25.py            # apply
    python3 scripts/apply_pass25.py --dry      # report only
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RESEARCH = os.path.join(DATA, "research")
DAY = "2026-09-17"
DRY = "--dry" in sys.argv

# --------------------------------------------------------------------------
# 1. Removals - rows proven to describe a restaurant already listed elsewhere.
#    "same name + same city + the same street address in both rows" is proof of
#    duplication; "different address, one of them contradicted by the
#    restaurant's own page" is proof that one row carries an unsupported address.
# --------------------------------------------------------------------------
REMOVALS = {
    "L676": {
        "kept_as": "L33",
        "reason": "Duplicate of L33: same name, same city and the same address (19369 Stevens Creek Blvd Ste 130, Cupertino) in both rows.",
        "evidence": ["https://www.yelp.com/biz/eureka-cupertino-3"],
    },
    "L815": {
        "kept_as": "L90",
        "reason": "Duplicate of L90: same name, same city and the same address (570 N Shoreline Blvd, Ste J, Mountain View) in both rows.",
        "evidence": ["https://www.mv-voice.com/mountain-view/2025/12/09/this-new-japanese-restaurant-offers-bentos-for-just-8-95/"],
    },
    "L678": {
        "kept_as": "L07",
        "reason": "Duplicate of L07 Siam Station (Cupertino). The kept row carries 20956 Homestead Rd Ste A2, the address two independent listing directories agree on; L678's 20688 Stevens Creek Blvd appears in no restaurant-controlled source.",
        "evidence": ["https://www.giftly.com/gift-card/siam-station-cupertino"],
    },
    "L679": {
        "kept_as": "L355",
        "reason": "Duplicate of L355 The City Fish (Cupertino). The kept row carries 21678 Stevens Creek Blvd, the address the restaurant's own menu site and listing directories use; L679's 20996 Stevens Creek Blvd appears in no restaurant-controlled source.",
        "evidence": ["https://www.cityfishco.com/menu-1", "https://www.giftly.com/gift-card/siam-station-cupertino"],
    },
    "L681": {
        "kept_as": "L12",
        "reason": "Duplicate of L12 Curry Hyuga (Cupertino), and its address is contradicted by the restaurant: curryhyuga.com and the restaurant's own Toast ordering page both give 19650 Stevens Creek Blvd, not 20662 Stevens Creek Blvd. The $14.99 lunch-special price it carried has no restaurant-controlled source.",
        "evidence": ["https://curryhyuga.com/", "https://toast.app/r/curry-hyuga-cupertino/order"],
    },
}

# --------------------------------------------------------------------------
# 2. Upgrades - existing rows given field-level evidence.
#    read_method: how the excerpt was obtained. "direct_fetch" = the page body
#    was read directly. "search_extraction_of_official_page" = the platform
#    rendered the restaurant's own ordering page and returned its menu text; the
#    page itself is restaurant-controlled but only its ordering shell is served
#    to a plain fetch, so the read method is recorded and the field is flagged.
# --------------------------------------------------------------------------
UPGRADES = {
    "L03": {
        "fields_update": {
            "address": "20588 Stevens Creek Blvd, Cupertino, CA 95014",
            "hours_tuesday": "11:15 AM - 11:15 PM",
            "days_open": "Every day 11:15 AM - 11:15 PM (restaurant's own Toast ordering page)",
            "hours_open": "Daily 11:15 AM - 11:15 PM",
        },
        "lunch_special_update": {
            "name": "Lunch Specials (特价午餐) - chicken, beef and shrimp plates, each with a complimentary 'mystery box' snack and drink",
            "price_from": 12.99,
            "price_to": 14.99,
            "days": None,
            "window": None,
            "includes": "12 printed lunch specials: Crispy Chicken, Orange Chicken, General Tso's, Sweet & Sour, Salt & Pepper, Sesame, Chicken Broccoli, Mongolian Chicken (all $12.99); Beef Broccoli, Mongolian Beef ($13.99); Shrimp Broccoli, Mongolian Shrimp ($14.99). Each includes a complimentary randomly selected drink; no substitutions.",
        },
        "sources": [
            {"label": "Home Eat Cupertino - restaurant's own Toast ordering page (address 20588 Stevens Creek Blvd and daily 11:15 AM - 11:15 PM hours; read directly 2026-09-17)",
             "url": "https://toast.app/r/home-eat-cupertino/order"},
            {"label": "Home Eat Cupertino - restaurant's own Toast menu (printed Lunch Specials 特价午餐 section with the $12.99-$14.99 prices; menu text obtained 2026-09-17)",
             "url": "https://order.toasttab.com/online/home-eat-cupertino"},
        ],
        "audit": {
            "checked_on": DAY,
            "status": "partial",
            "fields": {
                "special": {"status": "verified",
                            "value": "Printed 'Lunch Specials 特价午餐' section - 12 chicken, beef and shrimp lunch plates",
                            "source_url": "https://order.toasttab.com/online/home-eat-cupertino",
                            "quote": "## Lunch Specials 特价午餐 ... Crispy Chicken Lunch Special 椒香鸡特价午餐 ... $12.99 ... Shrimp Broccoli Lunch Special 芥蓝虾特价午餐 ... $14.99",
                            "source_type": "official_linked_ordering",
                            "read_method": "search_extraction_of_official_page"},
                "price": {"status": "verified",
                          "value": "$12.99 (chicken/vegetable) to $14.99 (shrimp) per plate; complimentary drink included",
                          "source_url": "https://order.toasttab.com/online/home-eat-cupertino",
                          "quote": "免费堂食盲盒饮料，不可调换其它饮品 ... $12.99 / $13.99 / $14.99",
                          "source_type": "official_linked_ordering",
                          "read_method": "search_extraction_of_official_page"},
                "schedule": {"status": "unknown",
                             "value": "No lunch window or day list is published on the ordering page (checked 2026-09-17); business hours are 11:15 AM - 11:15 PM daily, so the special cannot be bounded from the page",
                             "source_url": "",
                             "quote": "",
                             "source_type": ""},
                "location": {"status": "verified",
                             "value": "20588 Stevens Creek Blvd, Cupertino, CA 95014",
                             "source_url": "https://toast.app/r/home-eat-cupertino/order",
                             "quote": "Pickup from 20588 Stevens Creek Blvd, Cupertino, CA",
                             "source_type": "official_linked_ordering",
                             "read_method": "direct_fetch"},
                "hours": {"status": "verified",
                          "value": "Every day 11:15 AM - 11:15 PM",
                          "source_url": "https://toast.app/r/home-eat-cupertino/order",
                          "quote": "Sunday | 11:15 am - 11:15 pm ... Monday | 11:15 am - 11:15 pm ... Saturday | 11:15 am - 11:15 pm",
                          "source_type": "official_linked_ordering",
                          "read_method": "direct_fetch"},
            },
            "notes": "Prices are the restaurant's own printed lunch-special prices. The ordering page publishes no lunch clock window, so the schedule field stays unknown and the row is not featured. The earlier address label is replaced by the address on the restaurant's own ordering page.",
            "price_basis": "per plate",
        },
        "flags": ["Lunch-special clock window is not published by the restaurant, so 'when is it offered' cannot be answered from a primary source (LUNCH-FLAG-164)."],
    },
    "L104": {
        "fields_update": {"hours_tuesday": "not captured", "hours_open": "not captured"},
        "lunch_special_update": {
            "name": "Lunch Specials (Includes side and drink) - SOB burger, fried-chicken sandwich and taco combos",
            "price_from": 13.00,
            "price_to": 17.50,
            "days": None,
            "window": None,
            "includes": "SOB Burger Lunch Special $13.50, Hot SOB Burger $14.50, Bacon SOB Burger $16.50, Overachieving SOB Burger $17.50, Fried Chicken Sandwich $13.00, Spicy Chicken Sandwich $14.00, 2 Taco Lunch Special $13.00, 2 Caramelo Lunch Special $16.00. Each includes a drink and fries or chips.",
        },
        "sources": [
            {"label": "Local Kitchens Cupertino - restaurant's own Toast menu: 'Lunch Specials (Includes side and drink)' with eight printed prices, plus the 21666 Stevens Creek Blvd address (menu text obtained 2026-09-17)",
             "url": "https://order.toasttab.com/online/local-kitchens-cupertino"},
            {"label": "Local Kitchens Cupertino - restaurant's own Toast site (address 21666 Stevens Creek Boulevard, Cupertino, CA; ordering shell read directly 2026-09-17)",
             "url": "https://localkitchens.toast.site/order/local-kitchens-cupertino"},
        ],
        "audit": {
            "checked_on": DAY,
            "status": "partial",
            "fields": {
                "special": {"status": "verified",
                            "value": "Printed 'Lunch Specials (Includes side and drink)' section - 8 combos from the kitchen's burger, chicken and taco vendors",
                            "source_url": "https://order.toasttab.com/online/local-kitchens-cupertino",
                            "quote": "### Lunch Specials (Includes side and drink) - SOB Burger Lunch Special Comes with a drink and your choice of Fries or Potato Chips ... $13.50",
                            "source_type": "official_linked_ordering",
                            "read_method": "search_extraction_of_official_page"},
                "price": {"status": "verified",
                          "value": "$13.00 (Fried Chicken Sandwich / 2 Taco) to $17.50 (Overachieving SOB Burger); side and drink included",
                          "source_url": "https://order.toasttab.com/online/local-kitchens-cupertino",
                          "quote": "Overachieving SOB Burger Lunch Special ... $17.50 / Fried Chicken Sandwich Lunch Special ... $13.00 / 2 Taco Lunch Special ... $13.00",
                          "source_type": "official_linked_ordering",
                          "read_method": "search_extraction_of_official_page"},
                "schedule": {"status": "unknown",
                             "value": "The ordering page names the section 'Lunch Specials' but prints no day or clock window for it (checked 2026-09-17)",
                             "source_url": "", "quote": "", "source_type": ""},
                "location": {"status": "verified",
                             "value": "21666 Stevens Creek Blvd, Cupertino, CA",
                             "source_url": "https://localkitchens.toast.site/order/local-kitchens-cupertino",
                             "quote": "Pickup from 21666 Stevens Creek Boulevard, Cupertino, CA",
                             "source_type": "official_linked_ordering",
                             "read_method": "direct_fetch"},
                "hours": {"status": "unknown",
                          "value": "Business hours are not printed on the ordering page that carries the lunch specials (checked 2026-09-17)",
                          "source_url": "", "quote": "", "source_type": ""},
            },
            "notes": "Lunch-special prices and contents come from the restaurant's own ordering page; the two missing fields (day/window and business hours) are recorded as gaps rather than filled from aggregators, so this row is not featured.",
            "price_basis": "per combo",
        },
        "flags": ["Lunch-special day/time window and business hours are not published on the ordering page that carries these prices (LUNCH-FLAG-164)."],
    },
    "L12": {
        "fields_update": {
            "hours_tuesday": "Closed on Tuesday",
            "days_open": "Mon 11:30 AM - 2:30 PM (lunch only); Tue closed; Wed-Thu 11:30 AM - 2:30 PM and 5:00 - 9:00 PM; Fri-Sun 11:30 AM - 9:00 PM",
            "hours_open": "See days_open (restaurant's own site, checked 2026-09-17)",
        },
        "lunch_special_update": {
            "name": "Lunch service (Japanese curry) - no lunch special published",
            "price_from": None,
            "price_to": None,
            "days": None,
            "window": "Mon, Wed-Thu lunch 11:30 AM - 2:30 PM (restaurant's own site)",
            "includes": "The restaurant publishes a lunch service window but no priced lunch special on any page it controls. The $14.99 'lunch special' that an earlier batch attached to a duplicate row (L681) was removed on 2026-09-17 because no restaurant-controlled source prints it.",
        },
        "sources": [
            {"label": "Curry Hyuga official site - Cupertino hours block: Mon, Wed-Thu lunch 11:30 AM - 2:30 PM, dinner 5:00 - 9:00 PM; Fri-Sun 11:30 AM - 9:00 PM; Tuesday closed all day (read directly 2026-09-17)",
             "url": "https://curryhyuga.com/"},
            {"label": "Curry Hyuga Cupertino - restaurant's own Toast ordering page: 19650 Stevens Creek Boulevard, Cupertino, CA 95014 and a second, different hour set (read directly 2026-09-17)",
             "url": "https://toast.app/r/curry-hyuga-cupertino/order"},
        ],
        "audit": {
            "checked_on": DAY,
            "status": "partial",
            "fields": {
                "special": {"status": "unknown",
                            "value": "No lunch special is published: neither curryhyuga.com nor the restaurant's own Toast ordering page names one (checked 2026-09-17)",
                            "source_url": "", "quote": "", "source_type": ""},
                "price": {"status": "unknown",
                          "value": "No lunch-special price is published by the restaurant; the earlier $14.99 claim lived only in duplicate row L681 and was removed",
                          "source_url": "", "quote": "", "source_type": ""},
                "schedule": {"status": "verified",
                             "value": "Lunch service Mon and Wed-Thu 11:30 AM - 2:30 PM; Friday-Sunday continuous 11:30 AM - 9:00 PM; Tuesday closed",
                             "source_url": "https://curryhyuga.com/",
                             "quote": "MON, WED ~ THU LUNCH 11:30am - 2:30pm DINNER 5:00pm - 9:00pm FRI ~ SUN OPEN ALL DAY 11:30am - 9:00pm TUE - closed all day",
                             "source_type": "official",
                             "read_method": "direct_fetch"},
                "location": {"status": "verified",
                             "value": "19650 Stevens Creek Blvd, Cupertino, CA 95014",
                             "source_url": "https://toast.app/r/curry-hyuga-cupertino/order",
                             "quote": "Pickup from 19650 Stevens Creek Boulevard, Cupertino, CA",
                             "source_type": "official_linked_ordering",
                             "read_method": "direct_fetch"},
                "hours": {"status": "conflicting",
                          "value": "Own site: Mon/Wed-Thu 11:30 AM - 2:30 PM + 5:00 - 9:00 PM, Fri-Sun 11:30 AM - 9:00 PM, Tue closed. Own Toast page: Sun 11:15 AM - 8:45 PM, Mon 11:15 AM - 2:15 PM, Wed-Thu 11:15 AM - 2:15 PM + 4:45 - 8:45 PM, Fri-Sat 11:15 AM - 8:45 PM, Tue closed",
                          "source_url": "https://curryhyuga.com/",
                          "quote": "MON, WED ~ THU LUNCH 11:30am - 2:30pm ... (Toast page) Monday | 11:15 am - 2:15 pm",
                          "source_type": "official",
                          "read_method": "direct_fetch"},
            },
            "notes": "Recorded as an absence, not a deal: the restaurant serves lunch but publishes no lunch special and no price. Two of the restaurant's own pages disagree on the clock times by 15 minutes (LUNCH-FLAG-162).",
            "price_basis": "none published",
        },
        "flags": ["The restaurant publishes no lunch special; the row exists to make that gap visible instead of silently dropping it.",
                  "Its own website and its own Toast ordering page print different opening times (15-minute offset) - LUNCH-FLAG-162.",
                  "Duplicate row L681 removed this pass; the $14.99 price it carried had no restaurant-controlled source."],
    },
}

# --------------------------------------------------------------------------
# 3. New business - 1 net-new row, evidence from the restaurant's own site.
# --------------------------------------------------------------------------
NEW_ROWS = [
    {
        "name": "Calcutta Chaat & Bakery",
        "city": "Milpitas",
        "area": "Downtown Milpitas (81 S Main Street; second outlet in Fremont)",
        "address": "81 S Main Street, Milpitas, CA 95035",
        "coords": None,
        "cuisine": "Bengali / Kolkata street food, chaat, Indo-Chinese (Tangra)",
        "lunch_special": {
            "name": "Daily Lunch Special / Brunch Special Combo - Bengali combo plate and curry lunch specials",
            "price_from": 12.99,
            "price_to": 17.99,
            "days": None,
            "window": None,
            "includes": "The restaurant's own menu lists a combo plate under the lunch-special heading: 'Peas Kochuri, Aloor Dom, Cholar Dal, Gulab Jamun' at $12.99, illustrated with the restaurant-hosted file lunch_special_with_vegetable.webp. The sibling ordering domain lists a 'Daily Lunch Spacial' block: Lunch Special with Vegetable Curry $13.99, with Paneer Curry $13.99, with Chicken Dishes $15.99, with Goat Dishes $17.99. No day list and no clock window are published on either page.",
        },
        "hours_tuesday": "not captured",
        "days_open": "not captured",
        "open_on_trip_date": None,
        "fits_return_bus": {"ok": False, "note": "Downtown Milpitas is roughly 9-11 miles from the Cupertino destination and no lunch window is published, so it cannot be planned against."},
        "verification": {
            "level": "official",
            "sources": [
                {"label": "Calcutta Chaat & Bakery - restaurant's own menu: 'Peas Kochuri, Aloor Dom, Cholar Dal, Gulab Jamun' $12.99 under the lunch-special heading, plus the outlet selector listing Milpitas 81 S Main Street and Fremont 4906 Paseo Padre Pkwy (read directly 2026-09-17)",
                 "url": "https://calcuttachaat.com/menu"},
                {"label": "Calcutta Chaat & Bakery - restaurant's own homepage (Bay Area, Chef Bapi Das; links the same menu and outlet selector; read directly 2026-09-17)",
                 "url": "https://calcuttachaat.com/"},
                {"label": "Calcutta Chaat & Bakery sibling ordering domain - menu page carrying the 'Daily Lunch Spacial' prices ($13.99-$17.99); the page returned HTTP 500 to a direct fetch on 2026-09-17, so the text was obtained the same day through search extraction and is flagged",
                 "url": "https://calcuttachaatbakery.com/menu/"},
            ],
            "accessed": DAY,
        },
        "review_links": {
            "google_maps": "https://www.google.com/maps/search/?api=1&query=Calcutta+Chaat+%26+Bakery+81+S+Main+St+Milpitas",
        },
        "flags": [
            "The two pages the restaurant controls print different lunch-special prices: $12.99 for the vegetarian combo plate on calcuttachaat.com and $13.99-$17.99 for the 'Daily Lunch Spacial' curries on calcuttachaatbakery.com (LUNCH-FLAG-165).",
            "No day list and no lunch clock window are published, so 'when is it offered' is unanswered from primary sources (LUNCH-FLAG-164).",
            "DoorDash lists a separate Santa Clara 'Calcutta Chaat & Chinese' food truck; the operator has not confirmed it is the same business, so the Santa Clara listing was not added (LUNCH-FLAG-165).",
            "Coordinates were not captured from a restaurant-controlled page, so distance is left blank rather than estimated.",
        ],
        "added_in": "pass25_verified_new.json",
        "distance_mi": None,
        "zip": "95035",
        "deal_audit": {
            "checked_on": DAY,
            "status": "partial",
            "fields": {
                "special": {"status": "verified",
                            "value": "Daily Lunch Special / Brunch Special Combo - Bengali combo plate and curry lunch specials",
                            "source_url": "https://calcuttachaat.com/menu",
                            "quote": "Peas Kochuri, Aloor Dom, Cholar Dal, Gulab Jamun - A refined Bengali classic featuring crisp peas kochuri, slow-cooked aloor dum, aromatic cholar dal, and a soft, syrup-soaked gulab jamun. $12.99",
                            "source_type": "official",
                            "read_method": "direct_fetch"},
                "price": {"status": "verified",
                          "value": "$12.99 vegetarian lunch combo (restaurant's own menu); a sibling restaurant page prints $13.99-$17.99 for curry-version lunch specials",
                          "source_url": "https://calcuttachaat.com/menu",
                          "quote": "$12.99",
                          "source_type": "official",
                          "read_method": "direct_fetch"},
                "schedule": {"status": "unknown",
                             "value": "Neither restaurant page prints the days or the clock window of the lunch special (checked 2026-09-17)",
                             "source_url": "", "quote": "", "source_type": ""},
                "location": {"status": "verified",
                             "value": "81 S Main Street, Milpitas, CA 95035 (Fremont outlet 4906 Paseo Padre Pkwy)",
                             "source_url": "https://calcuttachaat.com/menu",
                             "quote": "Select Outlet - Fremont 4906 Paseo Padre Pkwy, CA 94555 / Milpitas 81 S Main Street, CA 95035",
                             "source_type": "official",
                             "read_method": "direct_fetch"},
                "hours": {"status": "unknown",
                          "value": "Opening hours are not published on the pages checked (homepage, menu, outlet selector) on 2026-09-17",
                          "source_url": "", "quote": "", "source_type": ""},
            },
            "notes": "First pass-25 net-new business. Offer, price and address are restaurant-controlled; schedule and hours are gaps, so the row is listed but not featured. The price conflict between the restaurant's two domains is flagged rather than smoothed over.",
            "price_basis": "per combo",
        },
    },
]

# --------------------------------------------------------------------------
# 4. Rejections - screened this pass, no published lunch special.
# --------------------------------------------------------------------------
REJECTIONS = [
    {"name": "Changsha Rice Noodles", "city": "Cupertino", "searched": DAY,
     "why": "Restaurant-controlled site (changsha-mifen.com) publishes no lunch special and no priced menu - only a gallery and phone number; delivery-app prices are not primary. Screened 2026-09-17.",
     "source": "https://changsha-mifen.com/"},
    {"name": "Mifen Yo", "city": "Cupertino", "searched": DAY,
     "why": "Xinjiang rice-noodle opening (19066 Stevens Creek Blvd). All priced menu text found was on DoorDash and other delivery platforms; no restaurant-controlled price list and no lunch special. Screened 2026-09-17.",
     "source": "https://www.doordash.com/store/mifen-yo!-cupertino-36486053/"},
    {"name": "Jade Xiang Yue (湘粵情)", "city": "Cupertino", "searched": DAY,
     "why": "No lunch special on any restaurant-controlled page; the only 'lunch set for four $58' text found was an aggregator note. Menu prices found were on delivery platforms. Screened 2026-09-17.",
     "source": "https://www.fantuanorder.com/en-US/store/jade-tea-garden/us-4856986"},
    {"name": "Lee & Bai Chinese Bao Shop", "city": "Sunnyvale", "searched": DAY,
     "why": "No lunch special published on any restaurant-controlled page; hours and menu appear only on listings and delivery platforms. Screened 2026-09-17.",
     "source": "https://www.yelp.com/biz/lee-and-bai-chinese-bao-shop-sunnyvale-2"},
    {"name": "Koi Palace Contempo", "city": "Cupertino", "searched": DAY,
     "why": "Cantonese/dim-sum opening at 19369 Stevens Creek Blvd Ste 100. Dim-sum service is lunch service, but no priced 'lunch special' is published by the restaurant; listing prices only. Screened 2026-09-17.",
     "source": "https://www.yelp.com/biz/koi-palace-contempo-cupertino-cupertino"},
    {"name": "Hometown Kitchen", "city": "Milpitas", "searched": DAY,
     "why": "Hunan restaurant at 1245 Jacklin Rd. Three menu sources (Beyond Menu, OrderSpoon, Postmates) carry full priced menus with no lunch-special section; a third-party FAQ page claims lunch specials with rice and soup, which is not usable as evidence. Screened 2026-09-17.",
     "source": "https://www.beyondmenu.com/40510/milpitas/hometown-kitchen-milpitas-95035.aspx"},
]

# --------------------------------------------------------------------------
# 5. Flags - irregularities found this pass.
# --------------------------------------------------------------------------
FLAGS = [
    {"id": "LUNCH-FLAG-161", "severity": "high",
     "title": "The batch-13b 'verified' rows duplicate earlier rows, and ~25 of the pairs still disagree on the street address",
     "what_we_found": "A name-and-city dedupe over the master list found 30 same-name/same-city pairs. Five of them were resolvable against primary sources this pass and were consolidated (L676/L33, L815/L90, L678/L07, L679/L355, L681/L12). In each removed row the address matched a Yelp search-URL centrepoint rather than the restaurant (20662 vs 19650 Stevens Creek Blvd for Curry Hyuga; 20688 vs 20956 Homestead Rd for Siam Station; 20996 vs 21678 Stevens Creek Blvd for The City Fish).",
     "what_we_did": "Removed the five proven duplicates with the proof recorded next to each removal and re-pointed the surviving rows at the restaurant-controlled address. The remaining ~25 pairs (Taste, Araki Sushi, Imperial Treasure, Kathmandu Cuisine, XPP Claypot, Sushi Arashi, Sakoon, Mayan Kitchen, Dainty Cuisine, Holder's Country Inn, Joanie's Cafe, Zareen's, Fambrini's Cafe, Ramen Kowa, Sweet Maple, Valley Goat, Sumika, Bloom & Vine, Bonchon, Sala Thai, Sizzling Lunch, Falafel Flare, Chuan Xiang, La Pizzeria, Pings Bistro and others) are queued for the same primary-source treatment in the next pass rather than deleted unverified.",
     "source": "data/research/pass25_duplicate_queue.json"},
    {"id": "LUNCH-FLAG-162", "severity": "medium",
     "title": "Curry Hyuga's own website and its own Toast ordering page print different opening times",
     "what_we_found": "curryhyuga.com prints Mon/Wed-Thu lunch 11:30 AM - 2:30 PM and dinner 5:00 - 9:00 PM, Fri-Sun 11:30 AM - 9:00 PM, Tuesday closed. The restaurant's own Toast ordering page prints Sun 11:15 AM - 8:45 PM, Mon 11:15 AM - 2:15 PM, Wed-Thu 11:15 AM - 2:15 PM + 4:45 - 8:45 PM, Fri-Sat 11:15 AM - 8:45 PM.",
     "what_we_did": "Both values are kept on the row and marked conflicting; a 15-minute offset matters if a diner plans to arrive near a closing time. No value was chosen.",
     "source": "https://curryhyuga.com/"},
    {"id": "LUNCH-FLAG-163", "severity": "high",
     "title": "An unsupported $14.99 lunch-special price was carried by a duplicate row",
     "what_we_found": "Row L681 (Curry Hyuga Cupertino) printed a $14.99 lunch special and an 11:30 AM - 2:30 PM window, but neither curryhyuga.com nor the restaurant's Toast page prints a lunch special or a price.",
     "what_we_did": "Removed L681 as a duplicate of L12 and left the surviving row with an explicitly empty price field, so no unverified number is displayed.",
     "source": "https://toast.app/r/curry-hyuga-cupertino/order"},
    {"id": "LUNCH-FLAG-164", "severity": "high",
     "title": "Two Cupertino lunch-special menus print prices but no day and no clock window",
     "what_we_found": "Home Eat Cupertino prints 12 lunch specials at $12.99-$14.99 and Local Kitchens Cupertino prints eight 'Lunch Specials (Includes side and drink)' at $13.00-$17.50 - and neither page states which days or which hours the special runs.",
     "what_we_did": "Both rows carry the verified price with the schedule field marked unknown and are excluded from the featured block rather than being given an invented window. This is the single largest blocker to featuring new Cupertino deals: the menu platforms do not publish the window and the restaurants' own sites do not either.",
     "source": "https://order.toasttab.com/online/home-eat-cupertino"},
    {"id": "LUNCH-FLAG-165", "severity": "medium",
     "title": "Calcutta Chaat & Bakery prints two different lunch-special price sets on two pages it controls",
     "what_we_found": "calcuttachaat.com lists the vegetarian lunch combo at $12.99; the sibling domain calcuttachaatbakery.com lists 'Daily Lunch Spacial' at $13.99 (vegetable/paneer), $15.99 (chicken) and $17.99 (goat). The sibling domain returned HTTP 500 to a direct fetch on 2026-09-17.",
     "what_we_did": "The new row prints the $12.99 combo that was read directly from the restaurant's menu, records the second price set in the same field and in the flags, and discloses that the second read came from search extraction of the restaurant's own page. A separate DoorDash 'Calcutta Chaat & Chinese' Santa Clara food truck is NOT treated as the same business.",
     "source": "https://calcuttachaat.com/menu"},
    {"id": "LUNCH-FLAG-166", "severity": "medium",
     "title": "Dish N Dash's domain is now a parked domain-sale page",
     "what_we_found": "dishndash.com resolves to a GoDaddy 'for sale' listing ($9,888) rather than to the restaurant's site that a master row cites for its menu.",
     "what_we_did": "Recorded here so the row's menu citation is re-pointed at a live restaurant-controlled page in the next pass; no value was changed on the row this pass.",
     "source": "https://forsale.godaddy.com/forsale/dishndash.com"},
    {"id": "LUNCH-FLAG-167", "severity": "medium",
     "title": "The Saratoga Springs (New York) 'lunch specials' trap appeared again in ring searches",
     "what_we_found": "A search for Saratoga-area lunch specials returned saratoga.com and discoversaratoga.org, which are Saratoga Springs, New York: '2 For $22 Lunch' (Morrissey's) and a Restaurant Week 'Breakfast/Lunch Specials $15' for November 2-8, 2026.",
     "what_we_did": "Neither page was used, and no California restaurant was credited with those prices. This is the third pass in which this name collision has appeared (LUNCH-FLAG-105, LUNCH-FLAG-139), so it is recorded as a standing trap.",
     "source": "https://www.saratoga.com/food-drink-specials/"},
    {"id": "LUNCH-FLAG-168", "severity": "low",
     "title": "Masakali Indian Cuisine has a Canadian namesake and disagreeing hours across listings",
     "what_we_found": "The Cupertino restaurant (10310 S De Anza Blvd) shares its name with Masakali Indian Cuisine in Stittsville, Ontario, whose reviews include 'there was no lunch specials'. Cupertino hours disagree between listings: Yelp prints Tuesday closed and Mon/Wed-Thu to 9:00 PM; other listings print seven days 11:30 AM - 10:00 PM.",
     "what_we_did": "Nothing was added to the row: no restaurant-controlled page was found that prints either hours or a lunch special, so the row keeps its legacy values and stays unfeatured. Listed here as a trap to avoid next pass.",
     "source": "https://www.yelp.com/biz/masakali-indian-cuisine-cupertino-3"},
    {"id": "LUNCH-FLAG-169", "severity": "medium",
     "title": "A Cupertino master row carries a stale 'permanently closed' claim from an aggregator",
     "what_we_found": "Olarn Thai Cuisine (19672 Stevens Creek Blvd) is listed in the master list as open, while a menu aggregator page renders 'Reported as permanently closed' next to 11:00 AM - 10:00 PM daily hours. The claim carries no date and the row's own sources show the restaurant open.",
     "what_we_did": "Not resolved: the aggregator is not a primary source and its note is undated. Queued for a next-pass call/primary check rather than acted on. Do not treat the closure as fact, and do not treat the row as verified either.",
     "source": "https://www.menupix.com/sanjose/restaurants/5564497/Olarn-Thai-Cuisine-Cupertino-CA"},
    {"id": "LUNCH-FLAG-170", "severity": "high",
     "title": "Pass 25 net-new result: 1 new business, 0 complete, against a 100-new-entry goal",
     "what_we_found": "33 discovery queries were executed, screened against a 1,153-key name+city index, and 84 candidate names were checked. Six of the genuinely new businesses found (2025-26 openings) publish no lunch special on any page they control; one does. The dense core of the ring is close to exhausted for published-and-priced lunch specials.",
     "what_we_did": "Recorded the true count instead of padding the list: 1 net-new business added (Calcutta Chaat & Bakery, Milpitas, partial), 5 duplicates removed, 3 existing rows upgraded with field-level evidence, 6 rejections and this flag. The 100-new-entry target remains unmet and the remaining candidate queue is published for the next pass.",
     "source": "data/research/pass25_search_log.json"},
]

# --------------------------------------------------------------------------
# 6. Sources registered for the pages this pass read.
# --------------------------------------------------------------------------
SOURCES = [
    {"id": "S195", "agency": "Home Eat Cupertino", "label": "Restaurant's own Toast ordering page - address 20588 Stevens Creek Blvd and daily 11:15 AM - 11:15 PM hours", "url": "https://toast.app/r/home-eat-cupertino/order", "fetch_status": "ok", "used_for": "L03 location + hours (direct fetch 2026-09-17)"},
    {"id": "S196", "agency": "Home Eat Cupertino", "label": "Restaurant's own Toast menu - printed 'Lunch Specials 特价午餐' section, $12.99-$14.99", "url": "https://order.toasttab.com/online/home-eat-cupertino", "fetch_status": "menu text via search extraction; ordering shell only on direct fetch", "used_for": "L03 lunch special + price (LUNCH-FLAG-164)"},
    {"id": "S197", "agency": "Local Kitchens Cupertino", "label": "Restaurant's own Toast menu - 'Lunch Specials (Includes side and drink)', $13.00-$17.50", "url": "https://order.toasttab.com/online/local-kitchens-cupertino", "fetch_status": "menu text via search extraction; ordering shell only on direct fetch", "used_for": "L104 lunch special + price (LUNCH-FLAG-164)"},
    {"id": "S198", "agency": "Curry Hyuga", "label": "Official site - Cupertino hours block (Mon/Wed-Thu lunch 11:30 AM - 2:30 PM; Tue closed)", "url": "https://curryhyuga.com/", "fetch_status": "ok", "used_for": "L12 hours + schedule (LUNCH-FLAG-162)"},
    {"id": "S199", "agency": "Curry Hyuga", "label": "Restaurant's own Toast ordering page - 19650 Stevens Creek Blvd address and second hour set", "url": "https://toast.app/r/curry-hyuga-cupertino/order", "fetch_status": "ok", "used_for": "L12 location, conflict evidence (LUNCH-FLAG-162/163)"},
    {"id": "S200", "agency": "Calcutta Chaat & Bakery", "label": "Restaurant's own menu - lunch-special combo plate $12.99 and outlet list (Milpitas, Fremont)", "url": "https://calcuttachaat.com/menu", "fetch_status": "ok", "used_for": "New row: special, price, location (LUNCH-FLAG-165)"},
    {"id": "S201", "agency": "Calcutta Chaat & Bakery", "label": "Sibling ordering domain - 'Daily Lunch Spacial' prices $13.99-$17.99", "url": "https://calcuttachaatbakery.com/menu/", "fetch_status": "HTTP 500 on direct fetch; text via search extraction", "used_for": "Price-conflict evidence (LUNCH-FLAG-165)"},
    {"id": "S202", "agency": "Changsha Rice Noodles", "label": "Restaurant's own site - no priced menu, no lunch special", "url": "https://changsha-mifen.com/", "fetch_status": "ok", "used_for": "Rejection evidence, screened 2026-09-17"},
    {"id": "S203", "agency": "Dish N Dash", "label": "Parked domain-sale page replacing the restaurant's menu site", "url": "https://forsale.godaddy.com/forsale/dishndash.com", "fetch_status": "ok", "used_for": "Link-rot flag LUNCH-FLAG-166"},
]


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    master = load(os.path.join(DATA, "lunch_specials.json"))
    entries = master["entries"]
    by_id = {e["id"]: e for e in entries}
    rejected = load(os.path.join(DATA, "lunch_rejected.json"))
    flags = load(os.path.join(DATA, "flags.json"))
    sources = load(os.path.join(DATA, "sources.json"))

    report = {"removed": [], "upgraded": [], "added": [], "rejected": [], "flags": [], "sources": []}

    for rid, info in REMOVALS.items():
        if rid not in by_id:
            print(f"  ! {rid} already absent")
            continue
        e = by_id.pop(rid)
        report["removed"].append({"id": rid, "name": e["name"], "city": e["city"],
                                  "kept_as": info["kept_as"], "reason": info["reason"], "evidence": info["evidence"]})

    for rid, info in UPGRADES.items():
        e = by_id.get(rid)
        if not e:
            print(f"  ! {rid} missing")
            continue
        e.update(info.get("fields_update", {}))
        if info.get("lunch_special_update"):
            ls = dict(e.get("lunch_special") or {})
            ls.update(info["lunch_special_update"])
            e["lunch_special"] = ls
        existing = {s["url"] for s in e["verification"]["sources"]}
        for s in info["sources"]:
            if s["url"] not in existing:
                e["verification"]["sources"].append(s)
        e["deal_audit"] = info["audit"]
        e["verification"]["level"] = "official"
        e["verification"]["accessed"] = DAY
        for f in info.get("flags", []):
            if f not in e["flags"]:
                e["flags"].append(f)
        report["upgraded"].append({"id": rid, "name": e["name"], "status": info["audit"]["status"],
                                   "fields": {k: v["status"] for k, v in info["audit"]["fields"].items()}})

    highest = max(int(e["id"][1:]) for e in entries)
    for raw in NEW_ROWS:
        highest += 1
        row = dict(raw)
        row["id"] = "L%03d" % highest
        row.setdefault("open_on_trip_date", None)
        entries.append(row)
        report["added"].append({"id": row["id"], "name": row["name"], "city": row["city"],
                                "status": row["deal_audit"]["status"],
                                "fields": {k: v["status"] for k, v in row["deal_audit"]["fields"].items()}})

    entries[:] = [e for e in entries if e["id"] in by_id or any(e["id"] == r.get("id") for r in report["added"])]
    entries.sort(key=lambda e: int(e["id"][1:]))

    have = {r["name"].lower() + "|" + r["city"].lower() for r in rejected["rejected"]}
    for r in REJECTIONS:
        if r["name"].lower() + "|" + r["city"].lower() in have:
            continue
        rec = {"name": r["name"], "city": r["city"], "searched": r["searched"], "why": r["why"]}
        rejected["rejected"].append(rec)
        report["rejected"].append(rec)

    known = {f["id"] for f in flags["lunch"]}
    for f in FLAGS:
        if f["id"] in known:
            continue
        flags["lunch"].append(f)
        report["flags"].append(f["id"])

    have_src = {s["url"] for s in sources["sources"]}
    for s in SOURCES:
        if s["url"] in have_src:
            continue
        sources["sources"].append(s)
        report["sources"].append(s["id"])

    sp = master.setdefault("search_protocol", {})
    sp["queries_run"] = int(sp.get("queries_run", 0)) + 33
    sp["candidates_found"] = int(sp.get("candidates_found", 0)) + 84
    sp["added_to_master"] = len(entries)
    sp["rejected_or_deferred"] = len(rejected["rejected"])
    sp["requirement"] = ("2026-09-17 (pass 25): 33 discovery queries executed and recorded verbatim, 84 candidate "
                         "names screened against a 1,153-key name+city index, 5 proven duplicate rows removed, 3 rows "
                         "upgraded with field-level evidence, 1 net-new business added (partial), 6 rejections, 10 flags. "
                         "The 100-new-entry target remains unmet and is reported as such in LUNCH-FLAG-170.")
    sp["search_date"] = "2026-09-17 (pass 25)"
    master["pass25_note"] = ("Pass 25 removed five duplicate rows, added field-level evidence to three Cupertino rows and "
                             "added one new business. Featured deals still require all five evidence fields; the new rows "
                             "lack a published lunch window and are therefore listed but not featured.")

    if not DRY:
        with open(os.path.join(DATA, "lunch_specials.json"), "w", encoding="utf-8") as fh:
            json.dump(master, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(DATA, "lunch_rejected.json"), "w", encoding="utf-8") as fh:
            json.dump(rejected, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(DATA, "flags.json"), "w", encoding="utf-8") as fh:
            json.dump(flags, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(DATA, "sources.json"), "w", encoding="utf-8") as fh:
            json.dump(sources, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.makedirs(RESEARCH, exist_ok=True)
        with open(os.path.join(RESEARCH, "pass25_evidence.json"), "w", encoding="utf-8") as fh:
            json.dump({"checked_on": DAY, "removals": report["removed"], "upgrades": report["upgraded"],
                       "additions": report["added"], "rejections": report["rejected"], "flags": report["flags"]},
                      fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(RESEARCH, "pass25_evidence.csv"), "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["row", "change", "field", "status", "value", "source_url", "quote", "source_type", "read_method"])
            for rid, info in UPGRADES.items():
                for name, f in info["audit"]["fields"].items():
                    w.writerow([rid, "upgraded", name, f["status"], f.get("value", ""), f.get("source_url", ""),
                                f.get("quote", ""), f.get("source_type", ""), f.get("read_method", "")])
            for row in NEW_ROWS:
                for name, f in row["deal_audit"]["fields"].items():
                    w.writerow(["new:" + row["name"], "added", name, f["status"], f.get("value", ""), f.get("source_url", ""),
                                f.get("quote", ""), f.get("source_type", ""), f.get("read_method", "")])

    print(f"removed {len(report['removed'])} duplicate rows: " + ", ".join(r["id"] for r in report["removed"]))
    print(f"upgraded {len(report['upgraded'])} rows: " + ", ".join(f"{r['id']}({r['status']})" for r in report["upgraded"]))
    print(f"added {len(report['added'])} rows: " + ", ".join(f"{r['id']} {r['name']}" for r in report["added"]))
    print(f"rejections +{len(report['rejected'])}; flags +{len(report['flags'])}; sources +{len(report['sources'])}")
    print(f"master list: {len(entries)} rows; rejected: {len(rejected['rejected'])}; lunch flags: {len(flags['lunch'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
