# 02 — Data Sources (free only)

> Verify each endpoint with one live call and record a fixture before coding against it. Free-tier limits change; never hard-code limits in business logic — read from `providers.yaml`.

## On-chain providers
| Chain | Provider | Notes |
|---|---|---|
| TRON | TronGrid `GET https://api.trongrid.io/v1/accounts/{addr}/transactions/trc20` (params: `limit<=200`, `only_confirmed`, `min_timestamp`, `max_timestamp`, `contract_address`, `fingerprint` for paging) and `/v1/accounts/{addr}/transactions` for TRX | Header `TRON-PRO-API-KEY`. USDT-TRC20 contract `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`. Free key has daily quota + QPS cap; 429/403/503 -> backoff. |
| Ethereum/EVM | Etherscan V2 `https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist|txlistinternal|tokentx&address=...` | Free plan supports only selected chains and has per-second/day caps; "free API not supported for this chain" is possible -> fall back to Blockscout. Per-query result window is limited (window by block ranges). USDT-ERC20 `0xdAC17F958D2ee523a2206206994597C13D831ec7`. |
| EVM fallback | Blockscout public instances, e.g. `https://eth.blockscout.com/api/v2/addresses/{addr}/transactions` and `/token-transfers` | Free, no key for basic use; paginated via `next_page_params`. |
| Bitcoin | mempool.space `GET /api/address/{addr}/txs` and `/txs/chain/{last_seen_txid}`; Esplora-compatible fallback (blockstream.info) | No key. Paginated. |
| Solana (stretch) | Public RPC `getSignaturesForAddress` + `getTransaction`, optional free Helius key | Only if time permits. |

Adapter contract (`ingest/base.py`): `async fetch_transfers(address, *, since=None, until=None, asset=None, max_pages=N) -> AsyncIterator[Transfer]` plus `validate_address(str) -> bool`. Every HTTP response goes through `cache.py`.

## Cache & evidence store
Table `raw_responses(id, provider, url, params_json, status, body, sha256, retrieved_at, case_id?)`. Cache key = provider+url+params. TTL configurable (immutable history = long TTL; "latest" queries short). Never mutate stored bodies. This table is the evidence layer.

## Rate limiting
Token bucket per provider (rate from config), global concurrency cap, jittered exponential backoff, circuit breaker after repeated failures, and a **per-case API-call budget** (used by the guided tracer; see 04).

## Address validation
- TRON: base58check, starts `T`, 34 chars. EVM: `0x` + 40 hex (validate EIP-55 checksum if mixed case). BTC: base58check (1/3) or bech32/bech32m (bc1...).

## Label sources (each row stored with provenance)
Label CSV schema: `address,chain,entity,entity_type,source,source_url,retrieved_at,license,label_confidence` where `entity_type in {exchange_hot, exchange_deposit, exchange_cold, mixer, bridge, dex, sanctioned, scam, phishing, service, unknown}`.

| Source | Use | Notes |
|---|---|---|
| OFAC SDN digital-currency addresses (Treasury export / 0xB10C mirror) | sanctioned | Public domain. Refresh via CLI. |
| Exchange proof-of-reserves address disclosures (Binance and other exchanges that publish wallet lists) | exchange_hot/cold (CONFIRMED tier) | Collect into `data/labels/por_*.csv` with `source_url` + date. First-party provenance; not complete. |
| Open labeled-address repos (Ethereum/BTC exchange, mixer, scam labels) e.g. consolidated community label repos | training + lookup | Check each licence; store licence column. |
| Kaggle/Etherscan-derived Ethereum fraud datasets (scam vs non-scam addresses) | M1/M2 training | Reproduce via provided pipelines if data files are not in repo. |
| Phishing/scam blocklists (e.g. MetaMask eth-phishing-detect, ScamSniffer DB) | scam/phishing labels | Verify licence + freshness. |
| Elliptic Bitcoin dataset (and Elliptic++ if accessible) | BTC illicit-tx benchmark | Standard temporal split; see 03. |
| Bridge / DEX router / mixer contract lists | swap & bridge handling | Curate manually from official docs into `data/labels/contracts_*.csv`. |

**Weak labels for deposit addresses**: derive with the Deposit-Address-Reuse heuristic (Victor 2020): an address receiving from many distinct EOAs and forwarding (similar amount, short delay) to a known exchange main address is an exchange deposit address. Requires the exchange main-address seed list above. Tag such labels `source=weak_DAR`, `label_confidence=weak`.

## Ground-truth construction for evaluation
1. **Entity-labeled set**: addresses with known entity (exchange/mixer/bridge/scam) from open sources.
2. **Trace-labeled set** (for M3): for seed illicit addresses (OFAC, scam lists) expand k hops in cached graphs; label each intermediate node with "reached a labeled VASP within k hops (y/n) and after how many hours".
3. **Elliptic** for BTC illicit scoring.
Document limitations: labels are incomplete, biased to large exchanges, and weak labels can be wrong. Report this in model cards.

## Demo data
Record 4–6 real public cases (e.g., OFAC-listed wallets, well-documented public scam/hack addresses) as fixtures via `make fixtures`. Never present them as Indian fraud complaints; they are public demonstration seeds. Add synthetic cases from `scripts/synth_laundering.py` labeled SYNTHETIC.
