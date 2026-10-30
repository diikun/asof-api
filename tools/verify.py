#!/usr/bin/env python3
"""Check an AsOf evidence pack on your own machine.

    python3 verify.py https://asof.pro/data/evidence/paxg.json
    python3 verify.py paxg.json --no-tsa      # skip the RFC 3161 check (no openssl)

For every document in the pack:
  1. downloads the daily manifest and checks its SHA-256;
  2. finds the document's entry in the manifest and recomputes the Merkle root
     from the entry and its path;
  3. with openssl, verifies each RFC 3161 time-stamp token over the manifest.
Then lists which facts rest on which time-stamped document versions.

Python 3.8+ standard library only. Exit code 0 when everything checks out.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

UA = "AsOf-verify/0.1 (+https://asof.pro/developers/)"


def fetch(src: str) -> bytes:
    if os.path.exists(src):
        with open(src, "rb") as f:
            return f.read()
    req = urllib.request.Request(src, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def leaf_bytes(doc: dict) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")


def root_from_path(leaf: bytes, path: list) -> str:
    h = hashlib.sha256(b"\x00" + leaf).digest()
    for step in path:
        s = bytes.fromhex(step["hash"])
        h = hashlib.sha256(b"\x01" + (s + h if step["side"] == "L" else h + s)).digest()
    return h.hex()


def check_tsa(manifest: bytes, ts: dict, tmp: str) -> str:
    ossl = shutil.which("openssl")
    if not ossl:
        return "skipped (openssl not found)"
    name = ts["url"].rsplit("/", 1)[-1]
    folder = os.path.join(tmp, ts["url"].rsplit("/", 2)[-2])
    os.makedirs(folder, exist_ok=True)
    tsr = os.path.join(folder, name)
    data = os.path.join(folder, "manifest.json")
    with open(tsr, "wb") as f:
        f.write(fetch(ts["url"]))
    with open(data, "wb") as f:
        f.write(manifest)
    ca = chain = None
    for url in ts.get("ltv", []):
        path = os.path.join(folder, url.rsplit("/", 1)[-1])
        with open(path, "wb") as f:
            f.write(fetch(url))
        if path.endswith("-ca.pem"):
            ca = path
        elif path.endswith("-chain.pem"):
            chain = path
    if not ca:
        ca = next((p for p in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt") if os.path.exists(p)), None)
    args = [ossl, "ts", "-verify", "-in", tsr, "-data", data]
    if ca:
        args += ["-CAfile", ca]
    if chain:
        args += ["-untrusted", chain]
    r = subprocess.run(args, capture_output=True, text=True)
    return "OK" if r.returncode == 0 else "FAILED: " + (r.stdout + r.stderr).strip().splitlines()[-1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", help="evidence pack: URL or file")
    ap.add_argument("--no-tsa", action="store_true", help="skip the RFC 3161 time-stamp check")
    a = ap.parse_args()
    pack = json.loads(fetch(a.pack))
    print("AsOf evidence pack: {} ({}), as of {}".format(pack["name"], pack["asset_id"], pack["as_of"]))
    ok = True
    manifests, tsa_done, verified = {}, {}, set()
    with tempfile.TemporaryDirectory() as tmp:
        for e in pack["documents"]:
            m, doc = e["manifest"], e["document"]
            if m["url"] not in manifests:
                manifests[m["url"]] = fetch(m["url"])
            raw = manifests[m["url"]]
            parsed = json.loads(raw)
            checks = {
                "manifest sha256": hashlib.sha256(raw).hexdigest() == m["sha256"],
                "entry in manifest": doc in parsed["documents"],
                "merkle path": root_from_path(leaf_bytes(doc), e["merkle_path"]) == m["merkle_root"] == parsed["merkle_root"],
            }
            good = all(checks.values())
            ok &= good
            if good:
                verified.add((doc["source_id"], doc["sha256_text"], m["date"]))
            print("{} {} · {} · first stamped {} · {}".format("✓" if good else "✗", doc["source_id"], doc["sha256_text"][:16],
                                                       m["date"], ", ".join(k for k, v in checks.items() if not v) or "ok"))
            if not a.no_tsa:
                for ts in e["timestamps"]:
                    key = ts["url"]
                    if key not in tsa_done:
                        tsa_done[key] = check_tsa(raw, ts, tmp)
                        print("    RFC 3161 {} ({}): {}".format(ts["tsa"], ts.get("gen_time") or m["date"], tsa_done[key]))
                        ok &= not tsa_done[key].startswith("FAILED")
    days = {(s, sha): d for s, sha, d in verified}
    print("\nFacts:")
    for f in pack["facts"]:
        own = days.get((f["source_id"], f.get("snapshot_sha256")))
        later = days.get((f["source_id"], f.get("latest_sha256")))
        where = ("quoted version time-stamped no later than {}".format(own) if own else
                 "quote found in the latest version, time-stamped no later than {}".format(later) if later else "no time-stamped version")
        print("  {} {} — {}".format("✓" if own or later else "·", f["id"], where))
    print("\n" + pack.get("limits", ""))
    print("RESULT: {}".format("all checks passed" if ok else "SOME CHECKS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
