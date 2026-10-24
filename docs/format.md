# Passport format — `asof-passport` v0.1

A passport records what the documents of one token's issuer say, **as of a date**, about four questions: who owes the holder, how to get out, what backs it, and who can change the rules. Every statement points to a verbatim quote in an archived document. What the documents do not answer is listed, not hidden. The format has no score, rating or recommendation field, by design.

JSON Schema: [`schema/asof-passport-0.1.schema.json`](../schema/asof-passport-0.1.schema.json). Licence: CC BY 4.0. Anyone may publish passports in this format.

## Top-level fields

| Field | Meaning |
|---|---|
| `schema` | Always `"asof-passport/0.1"` |
| `id`, `name`, `ticker`, `type`, `category` | Identity of the asset; `type` is `rwa`, `stablecoin` or `coin` |
| `as_of` | Time of the run the passport was built from (ISO 8601, UTC) |
| `issuer` | Issuer name and jurisdiction as the documents state them |
| `deployments[]` | Chain, chain id, contract address, decimals; `address_source` is the issuer page that lists the address; `onchain_check` records `symbol()` and `decimals()` read from the chain |
| `facts[]` | Approved statements, each tied to a verbatim quote and a source |
| `unknowns[]` | Every expected field without an approved fact — never omitted |
| `measurements[]` | Values read directly from the blockchain, with block number and time; measurements, not editorial statements |
| `sources[]` | Every document archived for the asset: last check, status, SHA-256 of the extracted text, number of versions |
| `counts` | Number of confirmed and claimed facts and of unknown fields — not a score |

## Fact

| Field | Meaning |
|---|---|
| `id` | `asset.field.n` — `n` is never reused after a fact is removed |
| `layer`, `field` | Which question the fact answers (table below) |
| `text` | Plain-language statement in English, approved by the editor |
| `translations`, `translated_by`, `translated_from` | Machine translations of `text` and the English text they were made from; the quote is never translated |
| `quote` | Verbatim words from the source, at most 300 characters |
| `section` | Section, clause or page in the source, if it has one |
| `source_id`, `source_url`, `source_owner` | The document and who publishes it |
| `snapshot_sha256` | SHA-256 of the extracted text of the archived version the quote was taken from |
| `published_at` | Only if the document itself states a date; never replaced by `fetched_at` |
| `fetched_at` | When AsOf first archived that version |
| `approved_at`, `approved_via` | When and how the editor approved the fact |
| `evidence` | `confirmed` or `claimed` |
| `quote_in_latest_snapshot` | Set on every build: `true` if the quote is still in the newest archived version, `false` if not, `null` if the source was never archived |

## Evidence labels

- **confirmed** — stated in an issuer document: terms, MiCA white paper, key information document, attestation or reserves report, risk disclosure, address list.
- **claimed** — stated by the issuer on a product page, in product documentation or an announcement; no independent document.
- **Unknown** — an expected field with no approved fact. A gap in the archived documents, not a verdict.

## Questions (fields)

| Layer | Field | Meaning |
|---|---|---|
| summary | `what_you_get` | What one token represents, in the issuer's words |
| legal | `issuer_obligation` | Who owes the holder, and on what basis (claim, ownership, custody) |
| legal | `holder_rights` | Rights the holder has against the issuer or a custodian |
| legal | `regulator` | Licence or authorisation the issuer states, and the authority |
| legal | `governing_law` | Law that governs the terms and where disputes go |
| exit | `redemption_cash` | Whether and how tokens can be redeemed for money |
| exit | `redemption_in_kind` | Physical delivery of the underlying (commodity tokens only) |
| exit | `eligibility` | Who may buy from or redeem with the issuer |
| exit | `fees` | Fees the documents state |
| exit | `suspension` | When redemption or issuance can be delayed or suspended |
| backing | `reserve_assets` | What backs the tokens |
| backing | `custody` | Where and by whom the backing is held |
| backing | `attestation` | Who checks the backing, how often, and the limits of that check |
| rules | `freeze` | Who can freeze tokens or block addresses |
| rules | `upgrade` | Who can replace the contract code or migrate the token |
| rules | `mint` | How new tokens are created and who controls it |
| rules | `amend_terms` | Who can change the terms, and with what notice |

## Rules a passport follows

- No fact without a source and a verbatim quote of at most 300 characters.
- Publication date and fetch date are separate; one never stands in for the other.
- Unknown fields stay in `unknowns`; missing evidence is shown neither as good nor as bad.
- Full documents are not published; only hashes, dates, short quotes and links.
- Each archived version is listed in a daily manifest time-stamped under RFC 3161 with long-term validation data; `sources[].timestamp_token` points to that proof ([api.md](api.md#proof-of-date-rfc-3161-ltv)).
- Contract addresses come from the issuer's documentation and are checked on-chain.

## Versioning

`0.x`: fields may be added. A field is never renamed or removed within a major version. The API path carries the major version (`/api/v1`).
