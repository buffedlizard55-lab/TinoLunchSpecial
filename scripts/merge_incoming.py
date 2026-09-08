#!/usr/bin/env python3
"""Merge researched batches in data/incoming/*.json into the master lunch list.

Every entry in an incoming batch must carry the source URLs it was read from;
this script only checks shape, dedupes and assigns IDs - the proof lives in the
row itself. It never invents a value: a field that was not captured stays empty
and the row keeps the verification level the researcher gave it.

    python3 scripts/merge_incoming.py          # merge every new batch file
    python3 scripts/merge_incoming.py --dry    # report only, write nothing
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
INCOMING = os.path.join(DATA, "incoming")
DAY = "2026-09-07"

REQUIRED = ("name", "city", "address")


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def street_key(addr):
    m = re.search(r"(\d+)\s+(.*)", str(addr or ""))
    return norm(m.group(0)) if m else norm(addr)


def main():
    dry = "--dry" in sys.argv
    master = load(os.path.join(DATA, "lunch_specials.json"))
    entries = master["entries"]
    highest = max(int(e["id"][1:]) for e in entries)
    seen_name = {norm(e["name"]) + "|" + norm(e["city"]) for e in entries}
    seen_addr = {street_key(e["address"]) for e in entries if e.get("address")}
    rejected = load(os.path.join(DATA, "lunch_rejected.json"))
    rej_names = {norm(r["name"]) + "|" + norm(r.get("city", "")) for r in rejected["rejected"]}

    added, skipped, rej_added, problems, superseded = [], [], [], [], []

    for path in sorted(glob.glob(os.path.join(INCOMING, "*.json"))):
        batch = load(path)
        for raw in batch.get("entries", []):
            missing = [k for k in REQUIRED if not raw.get(k)]
            if missing:
                problems.append(f"{os.path.basename(path)}: {raw.get('name')} missing {missing}")
                continue
            key = norm(raw["name"]) + "|" + norm(raw["city"])
            if key in seen_name:
                skipped.append(f"{raw['name']} ({raw['city']}) - already in the master list")
                continue
            if street_key(raw.get("address")) in seen_addr:
                skipped.append(f"{raw['name']} ({raw['city']}) - address already listed")
                continue
            if key in rej_names:
                if raw.get("supersedes_rejection"):
                    # a later pass verified lunch service / an address: drop the old
                    # rejection so the verified row can be listed
                    rejected["rejected"] = [r for r in rejected["rejected"]
                                            if norm(r.get("name", "")) + "|" + norm(r.get("city", "")) != key]
                    rej_names.discard(key)
                    superseded.append(f"{raw['name']} ({raw['city']}) - earlier rejection superseded: {raw['supersedes_rejection']}")
                else:
                    skipped.append(f"{raw['name']} ({raw['city']}) - already in the rejected list")
                    continue
            highest += 1
            e = dict(raw)
            e["id"] = "L%03d" % highest
            e.setdefault("lunch_special", {})
            ls = e["lunch_special"]
            for k in ("name", "price_from", "price_to", "days", "window", "includes"):
                ls.setdefault(k, None)
            e.setdefault("cuisine", "not captured")
            e.setdefault("area", "")
            e.setdefault("hours_tuesday", "not captured")
            e.setdefault("days_open", "not captured")
            e.setdefault("open_on_trip_date", None)
            e.setdefault("fits_return_bus", {"ok": False, "note": "not assessed"})
            e.setdefault("flags", [])
            e.setdefault("review_links", {})
            e.setdefault("coords", None)
            v = e.setdefault("verification", {})
            v.setdefault("level", "unverified")
            v.setdefault("accessed", DAY)
            v.setdefault("sources", [])
            if not v["sources"]:
                problems.append(f"{os.path.basename(path)}: {raw['name']} has no source link")
                continue
            e["added_in"] = os.path.basename(path)
            entries.append(e)
            seen_name.add(key)
            seen_addr.add(street_key(e["address"]))
            added.append(e)

        for r in batch.get("rejected", []):
            key = norm(r.get("name", "")) + "|" + norm(r.get("city", ""))
            if key in rej_names or key in seen_name:
                continue  # already rejected, or listed by a verified row
            r.setdefault("searched", DAY)
            rejected["rejected"].append(r)
            rej_names.add(key)
            rej_added.append(r)

        for s in batch.get("sources", []):
            pass  # sources are registered in data/sources.json by hand, with the URL that proved them

    print(f"batch files: {len(glob.glob(os.path.join(INCOMING, '*.json')))}")
    print(f"added: {len(added)}  rejected: {len(rej_added)}  skipped: {len(skipped)}")
    for s in skipped:
        print("  -", s)
    for s in superseded:
        print("  ^", s)
    for p in problems:
        print("  x", p)

    if problems:
        print("\nFAILED: fix the rows above before merging")
        return 1
    if dry:
        return 0

    entries.sort(key=lambda e: int(e["id"][1:]))
    master["entries"] = entries
    with open(os.path.join(DATA, "lunch_specials.json"), "w", encoding="utf-8") as fh:
        json.dump(master, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(DATA, "lunch_rejected.json"), "w", encoding="utf-8") as fh:
        json.dump(rejected, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"\nmerged {len(added)} entries; master list now {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
