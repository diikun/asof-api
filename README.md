# AsOf — open API and passport format

**AsOf** (by Diikun LAB) is a read-only public archive of *what stands behind a token, as of a date*. For each token it records what the issuer's own documents say about four questions, with a verbatim quote, the source and the date for every statement:

| Layer | Question |
|---|---|
| Legal | Who owes the holder? Who is the issuer, under which law and licence? |
| Exit | How do I get out — redeem, at what minimum, with which fees, and when can redemption be suspended? |
| Backing | What backs the token, who holds it, and who checks it? |
| Rules | Who can freeze, mint, upgrade the contract or change the terms? |

What the documents do not answer is listed as **Unknown** — never hidden, never scored. On-chain facts (supply, upgradeable proxy, admin keys, pause and blacklist roles) are read directly from the blockchain with the block number.

This repository is the **public side** of AsOf: API documentation, the open passport format, and examples for comparing tokens and monitoring changes. The AsOf pipeline itself is not in this repository.

🌐 Site: **https://asof.pro** · 🇷🇺 [README на русском](README.ru.md)

---

## Quick start

No key, no sign-up. Every file can be read from any website (CORS) or server.

```bash
curl https://asof.pro/api/v1/passports/paxg.json
```

```js
const p = await (await fetch("https://asof.pro/api/v1/passports/usdc.json")).json();
console.log(p.name, "as of", p.as_of, p.counts);
```

| Endpoint | Content |
|---|---|
| `/api/v1/index.json` | All assets, counters, time of the last run |
| `/api/v1/passports/{id}.json` | One passport: facts with quotes and sources, on-chain measurements, archived sources, unknowns |
| `/api/v1/changes.json` | Detected changes in the issuers' documents (short passages, dates of the old and new version) |
| `/api/v1/scenarios.json` | What if…: seven events — which questions each token's documents answer, what the contract shows |
| `/api/v1/evidence/{id}.json` | Evidence pack of one passport: manifest entries, Merkle paths, RFC 3161 tokens — check with [`tools/verify.py`](tools/verify.py) |
| `/api/v1/schema.json` | JSON Schema of the passport format |
| `/feed.xml` | Change log as an Atom feed |
| `/data/proofs/index.json` | Daily RFC 3161 time-stamps of the archive, with LTV data |

Assets today (28):

| Group | Assets |
|---|---|
| Gold | `paxg` PAX Gold, `xaut` Tether Gold |
| US-dollar stablecoins | `usdt` Tether USD, `usdc` USD Coin, `pyusd` PayPal USD, `rlusd` Ripple USD, `usdg` Global Dollar, `usdp` Pax Dollar, `gho` GHO, `usde` Ethena USDe (synthetic dollar) |
| Euro stablecoins | `eurc` Euro Coin, `eurcv` EUR CoinVertible (Société Générale – FORGE) |
| Funds and notes | `benji` Franklin OnChain U.S. Government Money Fund, `ustb` Invesco Short Duration US Government Securities Fund, `uscc` Bitwise Crypto Carry Fund, `usyc` US Yield Coin, `ousg` Ondo Short-Term US Government Treasuries, `usdy` Ondo US Dollar Yield, `tbill` OpenEden TBILL, `syrupusdc` Maple syrupUSDC |
| Crypto tokens | `uni` Uniswap, `link` Chainlink, `steth` Lido Staked ETH, `ldo` Lido DAO, `ena` Ethena, `aave` Aave, `crv` Curve DAO, `ens` Ethereum Name Service |

The current list is always in `/api/v1/index.json`.

Full reference: **[docs/api.md](docs/api.md)** · Format: **[docs/format.md](docs/format.md)**

## What you can build

| Use | Example |
|---|---|
| **Compare** any two tokens field by field — same asset, different promises (on the site: asof.pro/en/compare/) | [`examples/python/compare.py`](examples/python/compare.py), [`examples/javascript/compare.mjs`](examples/javascript/compare.mjs) |
| **Monitor** a token you hold or list: new or removed facts, a quote that disappeared from the issuer's document, a source that stopped answering, a new proxy admin, owner or implementation, a paused contract | [`examples/python/monitor.py`](examples/python/monitor.py), [`examples/github-action-monitor.yml`](examples/github-action-monitor.yml) |
| **Embed** a passport card on your site; it updates by itself | [`examples/embed/index.html`](examples/embed/index.html) |

```bash
python3 examples/python/compare.py paxg xaut
python3 examples/python/monitor.py usdc        # exit code 1 when something changed
```

The examples use only the standard library (Python 3.8+, Node 18+).

## Rules the data follows

- No statement without a source and a verbatim quote (at most 300 characters).
- The publication date of a document and the date AsOf fetched it are separate fields.
- **Unknown** stays visible; missing evidence is shown neither as good nor as bad.
- No scores, ratings, rankings, recommendations, trading or affiliate links.
- Full documents are not republished — only hashes, dates, short quotes and links.
- **Proof of date (LTV):** every day the SHA-256 fingerprints of all archived documents are time-stamped under RFC 3161 by FreeTSA and DigiCert, with certificate chains and revocation lists stored for long-term validation. Anyone can check them with `openssl ts -verify` — see [docs/api.md](docs/api.md#proof-of-date-rfc-3161-ltv).
- Contract addresses come from the issuers' documentation and are checked on-chain.

Evidence labels: **confirmed** — stated in an issuer document (terms, MiCA white paper, attestation, risk disclosure, address list); **claimed** — stated on a product page or in product documentation; **Unknown** — no approved fact.

## Licence and attribution

- Data, documentation and the passport format: **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**. Credit **“AsOf by Diikun LAB”** with a link to the passport.
- Quotes inside facts are short excerpts of the issuers' documents and remain the issuers' text.
- Example code in `examples/`: **MIT**. See [LICENSE](LICENSE).

**A request, not a licence condition:** when you show AsOf data, show the as-of date, keep Unknown visible, and do not turn the data into scores, ratings or advice.

AsOf collects and archives public information. It is not investment, legal or tax advice and does not rate products.

## Roadmap

Coins are next: a **“who can change the rules”** passport for networks like Bitcoin and Ethereum — how protocol changes are proposed and adopted, client diversity, who controls upgrade keys of major contracts. See [ROADMAP.md](ROADMAP.md).

## Corrections and contact

Found something wrong or outdated — as an issuer, a lawyer or a reader? Open an issue with the page and the source, or write to diikunapp@gmail.com. Confirmed errors are corrected and the correction is dated.

Operator: Pakto (Dmitriy Diikun), Hettstedt, Germany · [Impressum](https://asof.pro/de/impressum/)
