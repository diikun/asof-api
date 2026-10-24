#!/usr/bin/env python3
"""Watch AsOf passports and report what changed since the last run.

    python3 monitor.py usdc paxg               # compare with .asof-monitor.json, then update it
    python3 monitor.py usdc --state my.json

Reports:
  - facts added or removed, Unknown fields filled or opened
  - a quote that is no longer found in the issuer's latest document
  - a source that stopped answering, or whose text changed
  - on-chain changes: proxy admin, implementation, owner, minter, pauser,
    blacklister, paused, whether the contract is upgradeable
    (total supply only with --supply, it moves every day)

Exit code: 0 nothing changed, 1 something changed, 2 error. First run saves a baseline.
Standard library only. Data: CC BY 4.0, "AsOf by Diikun LAB".
"""
import argparse
import json
import os
import sys
import urllib.request

BASE = os.environ.get("ASOF_BASE", "https://asof.pro")
WATCH_CHAIN = ["upgradeable_proxy", "proxy_pattern", "proxy_implementation", "proxy_admin", "proxy_admin_is_contract",
               "owner", "owner_is_contract", "master_minter", "pauser", "blacklister", "paused"]


# Send a descriptive User-Agent: Cloudflare may refuse the default "Python-urllib" one.
UA = "asof-api-example/1.0 (+https://github.com/diikun/asof-api)"


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def snapshot(p, supply):
    keys = WATCH_CHAIN + (["total_supply"] if supply else [])
    return {
        "as_of": p["as_of"],
        "facts": {f["id"]: {"field": f["field"], "text": f["text"], "quote_ok": f.get("quote_in_latest_snapshot")}
                  for f in p["facts"]},
        "unknowns": sorted(u["field"] for u in p["unknowns"]),
        "sources": {s["id"]: {"status": s.get("last_status"), "sha": s.get("sha256_text"), "url": s["url"]}
                    for s in p["sources"]},
        "chain": {"{}@{}".format(m["key"], m.get("chain_id", "")): m.get("value")
                  for m in p["measurements"] if m["key"] in keys},
    }


def diff(old, new):
    out = []
    for fid in sorted(set(new["facts"]) - set(old["facts"])):
        out.append("new fact {}: {}".format(fid, new["facts"][fid]["text"]))
    for fid in sorted(set(old["facts"]) - set(new["facts"])):
        out.append("fact removed {} ({})".format(fid, old["facts"][fid]["field"]))
    for fid in sorted(set(old["facts"]) & set(new["facts"])):
        o, n = old["facts"][fid], new["facts"][fid]
        if n["quote_ok"] is False and o["quote_ok"] is not False:
            out.append("quote of {} is no longer found in the issuer's latest document".format(fid))
        if n["text"] != o["text"]:
            out.append("wording of {} changed: {}".format(fid, n["text"]))
    for f in sorted(set(new["unknowns"]) - set(old["unknowns"])):
        out.append("field now Unknown: {}".format(f))
    for sid, n in sorted(new["sources"].items()):
        o = old["sources"].get(sid)
        if o is None:
            out.append("new source {}: {}".format(sid, n["url"]))
        elif n["status"] != o["status"]:
            out.append("source {} status {} -> {}".format(sid, o["status"], n["status"]))
        elif n["sha"] and o["sha"] and n["sha"] != o["sha"]:
            out.append("source {} text changed: {}".format(sid, n["url"]))
    for key in sorted(set(old["chain"]) | set(new["chain"])):
        if old["chain"].get(key) != new["chain"].get(key):
            out.append("on-chain {}: {} -> {}".format(key, old["chain"].get(key), new["chain"].get(key)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+", help="asset ids, e.g. usdc paxg")
    ap.add_argument("--state", default=".asof-monitor.json")
    ap.add_argument("--supply", action="store_true", help="also report total supply changes")
    args = ap.parse_args()

    try:
        state = json.load(open(args.state)) if os.path.exists(args.state) else {}
    except ValueError:
        state = {}
    changed = False
    for aid in args.ids:
        try:
            p = get("/api/v1/passports/{}.json".format(aid))
        except Exception as e:  # noqa: BLE001 - report and keep going
            print("{}: could not fetch ({})".format(aid, e), file=sys.stderr)
            return 2
        snap = snapshot(p, args.supply)
        if aid not in state:
            print("{}: baseline saved (as of {})".format(aid, p["as_of"]))
        else:
            lines = diff(state[aid], snap)
            if lines:
                changed = True
                print("{} — changes since {} (now as of {}):".format(p["name"], state[aid]["as_of"], p["as_of"]))
                for line in lines:
                    print("  - " + line)
            else:
                print("{}: no changes (as of {})".format(aid, p["as_of"]))
        state[aid] = snap
    with open(args.state, "w") as fh:
        json.dump(state, fh, indent=1, sort_keys=True)
    print("Source: AsOf by Diikun LAB — CC BY 4.0. Passport: {}/en/assets/<id>/".format(BASE))
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
