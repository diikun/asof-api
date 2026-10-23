# Roadmap

Plans, not promises — dates are not fixed. Changes to the API stay compatible within `/api/v1`.

## Next: coins — “who can change the rules”

A passport for networks and their tokens that are not issued by a company, answering the same core question from the rules layer: **who can change what, and how**.

Planned fields (draft, may change):

| Field | Question |
|---|---|
| `change_process` | How protocol changes are proposed and adopted (for example BIPs, EIPs), as the project's own documentation describes it |
| `activation` | How a change is switched on (signalling, hard fork at a block or time) |
| `client_diversity` | Which node clients exist and who maintains them |
| `supply_rules` | Where the issuance schedule is defined and who could change it |
| `privileged_keys` | Admin, upgrade or pause keys of major contracts on the network (on-chain measurement) |
| `foundations` | Organisations that fund or coordinate development, with their own statements |

Same rules as today: every statement has a source and a quote, Unknown stays visible, no scores.

First candidates: Bitcoin, Ethereum.

## Later

- More tokenized assets and stablecoins (tokenized Treasury funds, more gold tokens, USDT, USDS).
- RFC 3161 time-stamps for archived snapshots (`timestamp_token`), so the date of each archived version can be checked independently.
- More languages on the site (ES, TR, ZH).
- A mobile app on the same open data.

Ideas and requests: open an issue.
