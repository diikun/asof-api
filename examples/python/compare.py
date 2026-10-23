#!/usr/bin/env python3
"""Compare two AsOf passports question by question.

    python3 compare.py paxg xaut
    python3 compare.py usdc eurc --lang de

Shows what each issuer's documents say, side by side, with the evidence label.
It does not rank or score: the differences are the result.
Standard library only. Data: CC BY 4.0, "AsOf by Diikun LAB".
"""
import argparse
import json
import os
import textwrap
import urllib.request

BASE = os.environ.get("ASOF_BASE", "https://asof.diikunapp.workers.dev")  # moving to https://asof.pro

LAYERS = ["summary", "legal", "exit", "backing", "rules"]
CHAIN_KEYS = [  # on-chain measurements worth putting next to each other
    ("upgradeable_proxy", "Contract code can be replaced (proxy)"),
    ("proxy_admin_is_contract", "Proxy admin is a contract (vs single key)"),
    ("owner_is_contract", "Owner is a contract (vs single key)"),
    ("paused", "Transfers paused now"),
]


# Send a descriptive User-Agent: Cloudflare may refuse the default "Python-urllib" one.
UA = "asof-api-example/1.0 (+https://github.com/diikun/asof-api)"


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fact_text(p, field, lang):
    facts = [f for f in p["facts"] if f["field"] == field]
    if not facts:
        return "Unknown"
    f = facts[0]
    text = (f.get("translations") or {}).get(lang) if lang != "en" else None
    return "{} [{}]".format(text or f["text"], f["evidence"])


def measure(p, key):
    vals = [m.get("value") for m in p["measurements"] if m["key"] == key]
    if not vals:
        return "—"
    v = vals[0]
    return {True: "yes", False: "no"}.get(v, str(v))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--lang", default="en", help="en, de, fr, ru, uk, ar (text only; quotes stay original)")
    ap.add_argument("--width", type=int, default=46)
    args = ap.parse_args()

    a = get("/api/v1/passports/{}.json".format(args.a))
    b = get("/api/v1/passports/{}.json".format(args.b))

    order = {}
    for p in (a, b):
        for item in p["facts"] + p["unknowns"]:
            order.setdefault(item["field"], LAYERS.index(item["layer"]) if item["layer"] in LAYERS else 9)
    fields = sorted(order, key=lambda f: (order[f], f))

    w = args.width
    print("{:<20} | {:<{w}} | {}".format("", "{} (as of {})".format(a["name"], a["as_of"][:10]),
                                         "{} (as of {})".format(b["name"], b["as_of"][:10]), w=w))
    print("-" * (20 + 2 * w + 6))
    for field in fields:
        left = textwrap.wrap(fact_text(a, field, args.lang), w) or [""]
        right = textwrap.wrap(fact_text(b, field, args.lang), w) or [""]
        for i in range(max(len(left), len(right))):
            print("{:<20} | {:<{w}} | {}".format(field if i == 0 else "",
                                                 left[i] if i < len(left) else "",
                                                 right[i] if i < len(right) else "", w=w))
        print()
    print("From the blockchain")
    for key, label in CHAIN_KEYS:
        print("  {:<42} {:<{w}} {}".format(label, measure(a, key), measure(b, key), w=w // 2))
    print("\nSource: AsOf by Diikun LAB, {0}/en/assets/ — CC BY 4.0. Not investment advice.".format(BASE))


if __name__ == "__main__":
    main()
