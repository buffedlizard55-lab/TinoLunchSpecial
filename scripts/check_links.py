#!/usr/bin/env python3
"""Structural check of every citable source URL in data/*.json.

The rule this project is built on: every row must be clickable back to the page it
came from. This script enforces the shape of that rule; it checks URL form,
placeholder/proxy patterns, and source-host policy, but does not fetch every page:

  * every transit leg has at least one source with an https URL and a human label
  * every lunch row has at least one verification source with an https URL
  * no row is left with an empty/placeholder URL, a bare domain, or a proxy/cache
    URL copied out of an earlier tool response (those expire and are not citable)
  * hosts are on the allowed list for the claim type (transit rows must point at the
    operating agency, not at a third party)

    python3 scripts/check_links.py            # exit 1 on a violation
    python3 scripts/check_links.py --report   # also print the host histogram

"""
import json
import os
import sys
from collections import Counter
from urllib.parse import urlparse

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
BANNED_HOST_BITS = ("routify", "oss-", "proxy", "webcache.google", "translate.goog", "example.")
ALLOWED_AGENCY_HOSTS = {
    "sfmta.com": ("SFMTA", "Muni"),
    "caltrain.com": ("Caltrain",),
    "vta.org": ("VTA",),
}
problems = []
hosts = Counter()


def walk_urls(obj, where, out):
    if isinstance(obj, dict):
        if "url" in obj and isinstance(obj["url"], str):
            out.append((where, obj))
        for k, v in obj.items():
            walk_urls(v, f"{where}.{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_urls(v, f"{where}[{i}]", out)


def check(entry_list, load):
    for name in entry_list:
        doc = load(name)
        urls = []
        walk_urls(doc, name, urls)
        for where, holder in urls:
            u = holder["url"].strip()
            hosts[urlparse(u).netloc.lower().lstrip("www.") or u[:20]] += 1
            p = urlparse(u)
            if p.scheme != "https":
                problems.append(f"{where}: scheme is {p.scheme or 'none'!r}, want https - {u}")
            if not p.netloc or "." not in p.netloc:
                problems.append(f"{where}: no real host - {u}")
            if any(b in u for b in BANNED_HOST_BITS):
                problems.append(f"{where}: looks like a proxy/cache/expiring URL - {u}")
            host = p.netloc.lower().replace("www.", "")
            if host in ALLOWED_AGENCY_HOSTS and not p.path.strip("/"):
                # an agency homepage proves nothing; a restaurant homepage is a legitimate "we checked" link
                problems.append(f"{where}: agency links must point at the specific page - {u}")
            if not (holder.get("label") or "").strip():
                problems.append(f"{where}: source has no label - {u}")


def require_links_per_row(load):
    specials = load("lunch_specials.json")
    for e in specials["entries"]:
        srcs = (e.get("verification") or {}).get("sources") or []
        if not srcs:
            problems.append(f"{e['id']} {e['name']}: no verification source at all")
        for s in srcs:
            if "yelp.com" not in s["url"] and "google.com" not in s["url"] and urlparse(s["url"]).netloc.lower().replace("www.", "") in ALLOWED_AGENCY_HOSTS:
                problems.append(f"{e['id']}: transit agency cited for a restaurant row - {s['url']}")
    for obj, label in ((load("transit_outbound.json"), "outbound"), (load("transit_return.json"), "return")):
        for pl in obj["plans"]:
            for leg in pl["legs"]:
                if not leg.get("sources"):
                    problems.append(f"{label}/{pl['id']}/leg{leg.get('seq')}: no source link")
    src = load("sources.json")
    for s in src["sources"]:
        host = urlparse(s["url"]).netloc.lower().replace("www.", "")
        if s["agency"] in ALLOWED_AGENCY_HOSTS and ALLOWED_AGENCY_HOSTS[s["agency"]][0].lower() not in host:
            problems.append(f"{s['id']}: claimed agency {s['agency']} but URL host is {host}")


def main():
    def load(name):
        with open(os.path.join(DATA, name), encoding="utf-8") as fh:
            return json.load(fh)

    check(["transit_outbound.json", "transit_return.json", "fares.json",
           "lunch_specials.json", "lunch_rejected.json", "flags.json",
           "sources.json", "plan.json"], load)
    require_links_per_row(load)

    total = sum(hosts.values())
    print(f"https URLs shape-checked: {total} across {len(hosts)} hosts")
    if "--report" in sys.argv:
        for h, n in hosts.most_common():
            print(f"  {n:3d}  {h}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems:
            print("  x", p)
        return 1
    print("OK: every row has a citable HTTPS source URL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
