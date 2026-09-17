#!/usr/bin/env python3
"""Screen candidate restaurant names against the master list and the reject list.

Usage:
    python3 scripts/screen_candidates.py data/research/pass25_candidates.json

Reads {"candidates": [{"name": ..., "city": ...}, ...]} and prints, for every
candidate, whether the master list or the reject list already carries it.
A candidate is only "new" when neither list has it - passing the screen is not
proof of a lunch special, it only means the name is not already recorded.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def tokens(s):
    return {t for t in norm(s).split() if t not in {"the", "and", "of", "a"}}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data/research/pass25_candidates.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    master = json.load(open(os.path.join(ROOT, "data/lunch_specials.json"), encoding="utf-8"))["entries"]
    rejects = json.load(open(os.path.join(ROOT, "data/lunch_rejected.json"), encoding="utf-8"))["rejected"]

    index = {}
    for e in master:
        index.setdefault(norm(e["name"]) + "|" + norm(e.get("city", "")), ("master", e["id"]))
    for r in rejects:
        index.setdefault(norm(r.get("name", "")) + "|" + norm(r.get("city", "")), ("reject", r.get("id") or "-"))
    tok = {}
    for key, (kind, i) in index.items():
        name = key.split("|")[0]
        for t in tokens(name):
            tok.setdefault(t, set()).add((kind, i, name))

    fresh, known = [], []
    for c in data["candidates"]:
        key = norm(c["name"]) + "|" + norm(c.get("city", ""))
        hit = index.get(key)
        if hit:
            known.append((c, hit))
            continue
        near = {v for t in tokens(c["name"]) for v in tok.get(t, ())}
        near = {v for v in near if v[0] == "master"}
        if near:
            known.append((c, ("name-overlap", ",".join(sorted(v[1] for v in near)))))
        else:
            fresh.append(c)
    print(f"candidates: {len(data['candidates'])}  fresh: {len(fresh)}  already known: {len(known)}")
    print("\n== FRESH (not in master or reject list) ==")
    for c in fresh:
        print(f"  {c['name']}  ({c.get('city','')})  {c.get('lead','')}")
    print("\n== ALREADY KNOWN ==")
    for c, hit in known:
        print(f"  {c['name']} ({c.get('city','')}) -> {hit[0]} {hit[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
