#!/usr/bin/env python3
"""Build and validate the data files behind the Tino Lunch Special site.

Reads data/*.json, recomputes straight-line distances from the destination,
validates every row (time format, source links, fare arithmetic, time math),
then writes:
  data/generated.js   - window.TINO_DATA = {...}, the single file the browser loads
  data/summary.md     - the same tables in plain markdown, for reading in GitHub

Exit code 1 means a row failed validation, so a bad edit cannot silently ship.

    python3 scripts/build_data.py            # build + validate
    python3 scripts/build_data.py --print     # text itinerary to stdout, no write
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

DEST = (37.3128997, -122.0302984)          # 20387 Gillick Way, Cupertino
HOME = (37.760943, -122.482852)            # 21st Ave & Judah St, SF
DAY = "2026-09-08"
TIME_RE = re.compile(r"^\d{1,2}:\d{2} (?:AM|PM)(?: \(next day\))?$")
URL_RE = re.compile(r"^https?://")

errors, warnings, no_coord_ids = [], [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def minutes(t):
    """'1:12 PM' -> minutes after midnight. None when unparseable or relative."""
    if not t or not isinstance(t, str):
        return None
    # search, not match: values are allowed to be hedged or annotated, e.g.
    # "about 7:55 AM" or "3:43 PM - misses the deadline"
    m = re.search(r"\b(\d{1,2}):(\d{2}) (AM|PM)", t.strip())
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3)
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return h * 60 + mi


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def haversine(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    r = 3958.7613
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def check_times(label, rows):
    for r in rows:
        for field in ("depart", "arrive", "leave_home", "arrive_destination",
                      "leave_destination", "arrive_home", "drive_departure"):
            if field in r and r[field] and "walk" not in str(r[field]):
                if not TIME_RE.match(str(r[field])) and "about" not in str(r[field]) and "until" not in str(r[field]):
                    err(f"{label}: {field} '{r[field]}' is not HH:MM AM/PM")


def validate_transit(obj, label):
    for p in obj["plans"]:
        legs = p["legs"]
        check_times(f"{label}/{p['id']}", [p] + legs)
        # every leg must be traceable and timed
        for leg in legs:
            for key in ("from", "to", "depart", "arrive"):
                if not leg.get(key):
                    err(f"{label}/{p['id']}/leg{leg.get('seq')}: missing {key}")
            srcs = leg.get("sources") or []
            if not srcs:
                err(f"{label}/{p['id']}/leg{leg.get('seq')}: no source link")
            for s in srcs:
                if not URL_RE.match(s.get("url", "")):
                    err(f"{label}/{p['id']}/leg{leg.get('seq')}: bad source url {s.get('url')}")
            if leg.get("travel_min") and leg["travel_min"] < 0:
                err(f"{label}/{p['id']}/leg{leg.get('seq')}: negative travel time")
        # the plan header must agree with its own first and last leg, and the
        # stated duration must be the span those two times actually imply
        first = minutes(p["legs"][0]["depart"])
        last = minutes(p["legs"][-1]["arrive"])
        dep_key = "leave_home" if "leave_home" in p else "leave_destination"
        arr_key = "arrive_destination" if "arrive_destination" in p else "arrive_home"
        # compare the clock times, not the wording: headers are allowed to hedge
        # ("about 2:40 PM") or annotate ("3:43 PM - misses the deadline"), but the
        # minutes must be identical to the leg they summarise.
        for key, leg_val in ((dep_key, p["legs"][0]["depart"]), (arr_key, p["legs"][-1]["arrive"])):
            want = p.get(key)
            if want is None:
                err(f"{label}/{p['id']}: {key} is missing")
                continue
            a, b = minutes(str(want)), minutes(str(leg_val))
            if a is None or b is None:
                warn(f"{label}/{p['id']}: {key}='{want}' could not be parsed against leg '{leg_val}'")
            elif a != b:
                err(f"{label}/{p['id']}: header {key}='{want}' is {abs((a-b+720)%1440-720 if abs(a-b)>720 else a-b)} min off from the leg table's '{leg_val}'")
        if first is not None and last is not None:
            span = (last - first) % (24 * 60)
            if p.get("total_time_min") is None:
                p["total_time_min"] = span
            elif abs(span - p["total_time_min"]) > 3:
                err(f"{label}/{p['id']}: stated total {p['total_time_min']} min contradicts its own leg times ({span} min from "
                    f"{p['legs'][0]['depart']} to {p['legs'][-1]['arrive']})")


def validate_lunch(entries):
    global no_coord_ids
    seen = set()
    for e in entries:
        if e["id"] in seen:
            err(f"duplicate lunch id {e['id']}")
        seen.add(e["id"])
        if not e.get("name") or not e.get("city"):
            err(f"{e['id']}: missing name/city")
        srcs = (e.get("verification") or {}).get("sources") or []
        if not srcs:
            err(f"{e['id']} {e['name']}: no verification source")
        for s in srcs:
            if not URL_RE.match(s.get("url", "")):
                err(f"{e['id']}: bad source url {s.get('url')}")
        if not e.get("address") or not e.get("city"):
            err(f"{e['id']} {e.get('name')}: address or city missing - a row must be locatable")
        lvl = (e.get("verification") or {}).get("level", "")
        if not re.search(r"\d", str(e.get("address", ""))):
            # a row that admits it is unverified may keep a placeholder address; a claimed-verified row may not
            msg = f"address is a placeholder, not a verified street address ({e['address']})"
            if lvl.startswith(("official", "review", "listing", "mixed", "conflicting")):
                err(f"{e['id']} {e['name']}: {msg}")
            else:
                warn(f"{e['id']} {e['name']}: {msg}")
        # distance: compute rather than trust
        c = e.get("coords")
        if c and len(c) == 2:
            d = round(haversine(DEST, (c[0], c[1])), 2)
            if e.get("distance_mi") is None:
                e["distance_mi"] = d
            elif abs(d - e["distance_mi"]) > 0.35:
                warn(f"{e['id']} {e['name']}: stated distance {e['distance_mi']} mi vs computed {d} mi (straight line)")
        else:
            e["distance_mi"] = None
            no_coord_ids.append(e["id"])
        for k in ("price_from", "price_to"):  # price sanity
            v = e["lunch_special"].get(k)
            if v is not None and not (0 < v < 200):
                err(f"{e['id']}: implausible price {v}")
        if e["lunch_special"].get("price_from") and e["lunch_special"].get("price_to"):
            if e["lunch_special"]["price_from"] > e["lunch_special"]["price_to"]:
                err(f"{e['id']}: price_from > price_to")
        for field in ("hours_tuesday", "hours_monday", "hours_wednesday"):
            v = e.get(field)
            if v:
                for tok in re.findall(r"\d{1,2}:\d{2}", v):
                    hh = int(tok.split(":")[0])
                    if hh > 23:
                        err(f"{e['id']}: bad hour in {field}: {tok}")


def parse_dollars(text):
    """Sum every '$x.xx' written in a line, so the stated total can be checked."""
    return round(sum(float(m) for m in re.findall(r"\$(\d+(?:\.\d{1,2})?)", text)), 2)


def validate_fares(fares):
    for a in fares["agencies"]:
        for r in a["rows"]:
            if r["price"] is not None and r["price"] >= 0 and not (0 < r["price"] < 500):
                err(f"fare row implausible: {a['name']} {r['ticket']} {r['price']}")
    for t in fares["day_totals"]:
        stated = round(sum(i["fare"] for i in t["items"]), 2)
        if abs(stated - t["total"]) > 0.005:
            err(f"day total '{t['label']}': items list {stated:.2f} of fares but total says {t['total']:.2f}")


def money(v):
    return "- free" if v == 0 else f"${v:.2f}"


def summary_md(D):
    L = []
    A = L.append
    p = D["plan"]
    A(f"# Verified plan - {p['trip_date_label']}")
    A("")
    A(f"*Origin:* {p['origin']['address']}  ")
    A(f"*Destination:* {p['destination']['address']}  ")
    A(f"*Verified:* {p['verification']['accessed']}")
    A("")
    out = [x for x in D["outbound"]["plans"] if x.get("recommended")][0]
    ret = [x for x in D["retplan"]["plans"] if x.get("recommended")][0]
    A(f"**Leave home {out['leave_home']} -> at the door {out['arrive_destination']}** "
      f"({out['total_time_min']} min, {money(out['cash_cost_usd'])}).  ")
    A(f"**Leave destination {ret['leave_destination']} -> home {ret['arrive_home']}** "
      f"({ret['total_time_min']} min, {money(ret['cash_cost_usd'])}).")
    A("")
    for label, obj in (("Outbound", D["outbound"]), ("Return", D["retplan"])):
        A(f"## {label}")
        for pl in obj["plans"]:
            A("")
            A(f"### {pl['label']}")
            A("")
            A("| # | Mode | Line / service | From | Departs | To | Arrives | Time | Fare | Verified | Sources |")
            A("|---|---|---|---|---|---|---|---|---|---|---|")
            for lg in pl["legs"]:
                src = " ".join(f"[{s['label']}]({s['url']})" for s in lg["sources"])
                A(f"| {lg['seq']} | {lg['mode']} | {lg['line']} | {lg['from']} | {lg['depart']} | "
                  f"{lg['to']} | {lg['arrive']} | {lg['travel_min']} min | {money(lg['fare_usd'])} | "
                  f"{lg['verified']} | {src} |")
    A("")
    A(f"## Fare options for {DAY}")
    A("")
    A("| Option | Total | Note |")
    A("|---|---|---|")
    for t in D["fares"]["day_totals"]:
        A(f"| {t['label']} | ${t['total']:.2f} | {t['caveat']} |")
    A("")
    A("## Lunch specials master list")
    A("")
    A("| ID | Restaurant | City | Address | Lunch special | Price | Days | Window | Tue hours | Verified | Distance | Sources |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for e in D["specials"]["entries"]:
        ls = e["lunch_special"]
        pr = "-" if ls["price_from"] is None else f"${ls['price_from']:.2f}" + (f"- ${ls['price_to']:.2f}" if ls.get("price_to") and ls["price_to"] != ls["price_from"] else "")
        src = " ".join(f"[{s['label']}]({s['url']})" for s in e["verification"]["sources"])
        rev = " ".join(f"[{k.replace('_', ' ')}]({v})" for k, v in (e.get("review_links") or {}).items() if v)
        A(f"| {e['id']} | {e['name']} | {e['city']} | {e['address']} | {ls['name']} | {pr} | "
          f"{ls['days']} | {ls.get('window') or '-'} | {e.get('hours_tuesday') or '-'} | "
          f"{e['verification']['level']} | {e.get('distance_mi') or '-'} mi | {src} {rev} |")
    A("")
    A("## Rejected candidates")
    A("")
    for r in D["rejected"]["rejected"]:
        A(f"- **{r['name']}** ({r['city']}) - {r['why']}" + (f" (price seen elsewhere: {r['price_hint']})" if r.get("price_hint") else ""))
    A("")
    A("## Flags")
    A("")
    for sect in ("transit", "lunch"):
        for f in D["flags"][sect]:
            A(f"- **{f['id']}** ({f['severity']}) {f['title']} - {f['what_we_did']}")
    A("")
    A("## Sources")
    A("")
    for s in D["sources"]["sources"]:
        A(f"- {s['id']} [{s['label']}]({s['url']}) - {s['used_for']}")
    return "\n".join(L) + "\n"


def main():
    as_text = "--print" in sys.argv
    plan = load("plan.json")
    outbound = load("transit_outbound.json")
    retplan = load("transit_return.json")
    fares = load("fares.json")
    specials = load("lunch_specials.json")
    rejected = load("lunch_rejected.json")
    flags = load("flags.json")
    sources = load("sources.json")

    D = {"plan": plan, "outbound": outbound, "retplan": retplan, "fares": fares,
         "specials": specials, "rejected": rejected, "flags": flags, "sources": sources}

    validate_transit(outbound, "outbound")
    validate_transit(retplan, "return")
    validate_lunch(specials["entries"])
    validate_fares(fares)

    # fare cross-check: sum of leg fares must match the plan total
    for obj, label in ((outbound, "outbound"), (retplan, "return")):
        for pl in obj["plans"]:
            s = round(sum(l["fare_usd"] for l in pl["legs"]), 2)
            if pl.get("cash_cost_usd") is not None and abs(s - pl["cash_cost_usd"]) > 0.01:
                err(f"{label}/{pl['id']}: legs add to {s} but cash_cost_usd says {pl['cash_cost_usd']}")

    print(f"lunch entries: {len(specials['entries'])} "
          f"(official {sum(1 for e in specials['entries'] if e['verification']['level'].startswith('official'))}, "
          f"review {sum(1 for e in specials['entries'] if e['verification']['level'].startswith('review'))}, "
          f"unverified {sum(1 for e in specials['entries'] if e['verification']['level'].startswith(('unverif', 'incomp')))})")
    print(f"transit legs validated: "
          f"{sum(len(p['legs']) for p in outbound['plans']) + sum(len(p['legs']) for p in retplan['plans'])}")
    print(f"sources registered: {len(sources['sources'])}; flags: "
          f"{len(flags['transit']) + len(flags['lunch'])}")

    if no_coord_ids:
        warnings.append(f"{len(no_coord_ids)} lunch rows have no captured coordinates, so distance is left blank rather than estimated: " + ", ".join(no_coord_ids))
    if warnings:
        print("\nWARNINGS")
        for w in warnings:
            print("  ~", w)
    if errors:
        print("\nERRORS")
        for e in errors:
            print("  x", e)

    if as_text:
        print("\n" + summary_md(D)[:1200] + "\n... (truncated; write data/summary.md without --print)")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s)")
        return 1

    if not as_text:
        payload = json.dumps(D, ensure_ascii=True, indent=1, separators=(",", ":"))
        with open(os.path.join(DATA, "generated.js"), "w", encoding="utf-8") as fh:
            fh.write("/* Generated by scripts/build_data.py - do not edit; edit data/*.json instead.\n"
                     "   Trip: Tue 2026-09-08. Verified against SFMTA, Caltrain, VTA, restaurant sites, Yelp.\n"
                     "   Missing data is labelled unverified rather than guessed. */\n"
                     "window.TINO_DATA = " + payload + ";\n")
        with open(os.path.join(DATA, "summary.md"), "w", encoding="utf-8") as fh:
            fh.write(summary_md(D))
        # keep the pretty-printed JSON in sync with the distances we computed
        with open(os.path.join(DATA, "lunch_specials.json"), "w", encoding="utf-8") as fh:
            json.dump(specials, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        gen = os.path.getsize(os.path.join(DATA, "generated.js"))
        print(f"\nwrote data/generated.js ({gen/1024:.1f} KiB) and data/summary.md")
    print(f"OK: {len(errors)} errors, {len(warnings)} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
