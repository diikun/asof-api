# API reference (v1)

Base URL: `https://asof.pro`.

The API is a set of static JSON files, rebuilt and republished after every AsOf run. There is no key, no sign-up and no rate limit on our side. CORS is enabled (`Access-Control-Allow-Origin: *`) on `/api/*`, `/data/*`, `/schema/*`, `/feed.xml` and `/embed.js`.

## Endpoints

### `GET /api/v1/index.json`

```json
{
  "generated_at": "2026-10-23T21:29:00Z",
  "last_successful_run": "2026-10-23T18:01:36Z",
  "assets": [
    {"id": "paxg", "name": "PAX Gold", "ticker": "PAXG", "type": "rwa", "category": "gold",
     "issuer": "Paxos Trust Company, NA", "jurisdiction": "United States",
     "deployments": [{"chain": "ethereum", "chain_id": 1, "address": "0x4580…Af78"}],
     "last_changed_at": null,
     "as_of": "…", "counts": {"confirmed": 16, "claimed": 1, "unknown": 0}}
  ]
}
```

### `GET /api/v1/passports/{id}.json`

One passport. Format: [format.md](format.md), JSON Schema: `/api/v1/schema.json`. Main parts:

| Field | Meaning |
|---|---|
| `as_of` | Time of the run the passport was built from |
| `facts[]` | Approved statements: `field`, `text` (English), `translations` (machine), `quote` (verbatim, ≤ 300 chars), `section`, `source_url`, `source_owner`, `snapshot_sha256`, `published_at` (only if the document states it), `fetched_at`, `approved_at`, `evidence` (`confirmed`/`claimed`), `quote_in_latest_snapshot` |
| `unknowns[]` | Expected fields without an approved fact |
| `measurements[]` | On-chain readings: `key`, `value`, `block`, `read_at`, `chain_id` |
| `sources[]` | Archived documents: `last_checked_at`, `last_status`, `last_changed_at`, `sha256_text`, `versions`, `timestamp_token` (path of the daily proof that covers this exact version, see [Proof of date](#proof-of-date-rfc-3161-ltv)) |
| `deployments[]` | Contract address per chain, the issuer page that lists it, and the on-chain `symbol()`/`decimals()` check |
| `counts` | Number of confirmed and claimed facts and of unknown fields — not a score |

On-chain measurement keys (where the contract exposes them): `total_supply`, `upgradeable_proxy` (`true` or `"not_detected"`), `proxy_pattern`, `proxy_implementation`, `proxy_admin`, `proxy_admin_is_contract`, `owner`, `owner_is_contract`, `master_minter`, `pauser`, `blacklister` (each with `_is_contract`), `paused`, and for gold tokens the reference feed `feed_xau_usd`, `feed_xau_usd_fresh`.

`*_is_contract: false` means the address is a single-key account; `true` means a smart contract (for example a multisig or a timelock). AsOf does not judge either.

### `GET /api/v1/changes.json`

Detected changes in the archived documents: `asset_id`, `source_id`, `url`, `detected_at`, previous and new SHA-256, and `passages[]` with short `removed`/`added` excerpts (≤ 300 characters each).

### `GET /feed.xml`

The same changes as an Atom feed — usable in any feed reader.

### `GET /api/v1/schema.json`

JSON Schema of the passport (`asof-passport/0.1`). Also in this repository: [schema/](../schema/).

### `GET /data/proofs/index.json` — proof of date (RFC 3161, LTV)

Daily proofs, newest first. See [Proof of date](#proof-of-date-rfc-3161-ltv).

## Proof of date (RFC 3161, LTV)

Every day AsOf writes a manifest of all archived documents and has its SHA-256 time-stamped by two independent RFC 3161 time-stamping authorities, **FreeTSA** and **DigiCert**. For each day, `/data/proofs/{date}/` holds:

| File | Content |
|---|---|
| `manifest.json` | `asof-manifest/0.1`: for every document `source_id`, `asset_id`, `url`, `sha256_text`, `sha256_raw`, `first_seen`; a `merkle_root`; `previous` (hashes of the previous day's manifest and tokens) |
| `freetsa.tsr`, `digicert.tsr` | RFC 3161 time-stamp responses over the SHA-256 of `manifest.json` |
| `*-chain.pem`, `freetsa-ca.pem` | Certificate chain of each authority |
| `*-crl-N.crl` | Certificate revocation lists valid at that moment (long-term validation, LTV) |
| `proof.json` | Summary: `manifest_sha256`, `merkle_root`, `documents`, `previous`, and per token `tsa`, `gen_time`, `serial`, `verified`, `ltv` |

Because each manifest includes the previous day's hashes, the proofs form a chain: every day re-stamps everything before it. The certificates and CRLs are stored so a token can still be checked after the certificates expire or a service closes.

Check it yourself:

```bash
D=2026-10-24; B=https://asof.pro/data/proofs/$D
curl -O $B/manifest.json -O $B/freetsa.tsr -O $B/freetsa-ca.pem -O $B/digicert.tsr
openssl ts -verify -in freetsa.tsr -data manifest.json -CAfile freetsa-ca.pem      # Verification: OK
openssl ts -verify -in digicert.tsr -data manifest.json -CAfile /etc/ssl/cert.pem  # system root store
```

To tie one document to a date: take `sources[].sha256_text` from a passport, find the same `source_id` and `sha256_text` in the manifest of the day in `timestamp_token`. The token then shows that this version existed no later than its `gen_time`.

What it does not prove: that the documents are true. FreeTSA and DigiCert are public RFC 3161 services, not qualified trust services under eIDAS. Only fingerprints are published; full documents stay in AsOf's private archive.

## Freshness

- Documents are archived once a day at 05:00 UTC; on-chain values are read in the same run.
- Facts appear after the editor approves them; the site is republished within the hour.
- Use `as_of` (passport) and `generated_at` (index) to show how fresh your copy is. Please show this date to your users.

Cache tip: send `If-None-Match` with the previous `ETag`; unchanged files answer `304`.

Send a descriptive `User-Agent` (for example `my-app/1.0 (+https://example.com)`). Cloudflare may refuse requests that carry a library default such as `Python-urllib`.

## Versions

`/api/v1` stays compatible: fields may be **added**, never renamed or removed. A breaking change gets `/api/v2`, and v1 keeps working for at least six months after that. Older `/data/...` paths keep working too.

## Embedding

```html
<div data-asof="paxg" data-lang="en"></div>
<script src="https://asof.pro/embed.js" async></script>
```

Or, where scripts are not allowed: `<iframe src="https://asof.pro/en/embed/paxg/" style="width:100%;max-width:560px;height:620px;border:0"></iframe>`. Languages: `en`, `de`, `fr`, `ru`, `uk`, `ar`. No cookies, no tracking.

## Licence

CC BY 4.0 — credit “AsOf by Diikun LAB” with a link to the passport. Quotes remain the issuers' text.
