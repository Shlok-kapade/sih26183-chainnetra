# 04 — Tracing, Attribution, Patterns, Risk

## Taint model
- Default **haircut (proportional)**: outflow from an address carries taint proportional to the tainted share of its balance/inflow. Options: `poison` (any mixed output fully tainted) and `fifo`, selectable in `trace.yaml`. Document that taint is an attribution convention for fungible assets, not physical coin tracking.
- Trace **one asset at a time** (e.g., USDT-TRC20), plus native asset; swaps create a new trace leg (below).

## Engine (`trace/engine.py`)
Inputs: seed address, chain, asset, optional reported amount/time, policy (`bfs|guided`), budget B (API calls), depth D (default 6), min_taint (default 1% of seed amount), fan-out cap per node (top-N by value), time window.
Loop (guided): priority queue of frontier nodes -> pop best -> fetch outgoing transfers (cached, budgeted) -> update edge taint -> classify each new node (labels, M1) -> apply termination check -> push children with priority from M3 (`bfs` uses hop order).
**Termination reasons (enumerated, always recorded)**: `REACHED_VASP_CONFIRMED`, `REACHED_VASP_PROBABLE`, `EXIT_P2P_OTC_SUSPECTED`, `EXIT_MIXER`, `EXIT_BRIDGE_UNRESOLVED`, `EXIT_SANCTIONED`, `DORMANT` (no outflow > N days), `BELOW_MIN_TAINT`, `DEPTH_LIMIT`, `BUDGET_EXHAUSTED`, `DATA_UNAVAILABLE`, `CONTRACT_UNKNOWN`. The result must never present a truncated trace as complete.

## Swap & bridge handling
- Detect DEX router/bridge contracts from curated lists. For EVM swaps, fetch the tx's token transfers (same tx hash) and continue the trace on the output asset (`SWAP_HOP` edge, taint carried by value share). For TRON DEX routers, same approach with tx-level TRC20 events.
- Bridges: emit `BRIDGE_EXIT_UNRESOLVED` with source tx; optionally search the destination chain for a matching inbound transfer (amount within ~1%, time within a configurable window, known bridge relayer) and attach as **POSSIBLE** cross-chain link with the matching evidence. Never auto-CONFIRM cross-chain links.
- Mixers: terminate with `EXIT_MIXER`; list post-mixer candidate outputs only as low-confidence hints (off by default).

## Attribution tiers (`attribution/`)
| Tier | Rule |
|---|---|
| CONFIRMED | Exact address match in a dated, sourced label file (`exchange_*`, sanctioned, etc.). |
| PROBABLE | Deposit-funnel evidence: address forwards ≥ X% of inflow (default 80%) within tau to a CONFIRMED VASP address, from ≥ N distinct senders (default 5) AND M1 p(exchange_deposit or hot) ≥ 0.8; or cluster membership (DAR) with a CONFIRMED VASP address. |
| POSSIBLE | M1 probability 0.5–0.8, or a single weak signal, or heuristic exit types (P2P/OTC, cross-chain match). |
| UNATTRIBUTED | Insufficient or contradictory evidence; reason recorded. |
Each attribution stores: entity, entity_type, tier, numeric confidence, evidence list (tx hashes, label source URLs/dates, feature contributions), model versions, limitations text. Confidence is separate from risk score.

## Deterministic pattern detectors (`patterns/`) — each returns `{pattern, score, evidence_tx_refs, false_positive_note}`
- `fan_out`: one address splits to many within window.
- `fan_in`: many addresses consolidate into one.
- `rapid_forwarding`: median dwell < threshold across ≥ N hops.
- `peel_chain`: repeated (large remainder forwarded, small piece peeled) pattern.
- `dormancy_burst`: long inactivity then rapid dispersal.
- `structuring`: many near-equal / just-below-threshold amounts.
- `round_trip`: value returns to origin cluster.
Unit-test each on synthetic cases with hypothesis/property tests; document benign lookalikes (payment processors, market makers, sweeps).

## Risk engine (`risk/`)
Score 0–100 from weighted signals in `risk_weights.yaml`: sanctions exposure, taint share reaching illicit-labeled entities, M1 illicit probability, pattern scores, M4 anomaly score, velocity/time-to-cash-out, exit type. Return: score, band (LOW 0–24, MEDIUM 25–49, HIGH 50–74, CRITICAL 75–100), **separate confidence**, itemized signals (raw value, weight, points), and list of signals that could not be evaluated (they reduce confidence; they never count as "safe"). The score is a prioritization aid, not a probability of guilt.

## Freeze/KYC request draft (`reports/freeze_request.py`)
Template with: case ref, VASP name/nodal contact placeholders, addresses, tx hashes, timestamps, amounts, attribution tier + evidence summary, request for account hold/KYC preservation, placeholders for legal authority reference and officer details. Watermark "DRAFT — for investigator review; no legal reference auto-filled". Never sent automatically.

## Evidence & reproducibility
- Every raw provider response: stored + SHA-256 + retrieval time.
- Report manifest: case id, seed, config hash, label-file versions/hashes, model versions, provider list, mode (live/fixture), code git SHA, generation time, SHA-256 of the report itself.
- State clearly in reports: hashes prove file integrity since capture, not truth of provider data or court admissibility.
