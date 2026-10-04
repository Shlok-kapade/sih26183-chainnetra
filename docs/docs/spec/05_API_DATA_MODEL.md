# 05 — API & Data Model

## Tables (PostgreSQL; Alembic migrations)
- `users(id, email, password_hash, role[investigator|supervisor|admin], created_at)`
- `complaints(id, external_ref, source[manual|csv|api|ncrp_mock|sahyog_mock], chain, address, reported_amount, reported_asset, reported_at, received_at, status)` — no victim PII.
- `cases(id, complaint_id, owner_id, status, mode[live|fixture], config_hash, created_at)`
- `jobs(id, case_id, kind, status, progress, error, payload_json, created_at, started_at, finished_at)`
- `raw_responses(id, provider, url, params_json, status, body, sha256, retrieved_at, case_id)`
- `transfers(id, case_id, chain, tx_hash, log_index, ts, from_addr, to_addr, asset, amount, kind, raw_ref)`
- `addresses(id, case_id, chain, address, first_seen, last_seen, is_contract, cluster_id, role_probs_json, model_version)`
- `edges(id, case_id, src, dst, asset, total_amount, tx_count, first_ts, last_ts, taint_share, tx_refs_json)`
- `labels(id, address, chain, entity, entity_type, source, source_url, retrieved_at, license, label_confidence)`
- `attributions(id, case_id, address, tier, entity, entity_type, confidence, evidence_json, model_versions_json, limitations)`
- `patterns(id, case_id, pattern, score, evidence_json, fp_note)`
- `exits(id, case_id, exit_type, address, tier, confidence, path_json, amount_at_risk, eta_hours, termination_reason)`
- `risk(id, case_id, score, band, confidence, signals_json, unevaluated_json)`
- `triage(id, case_id, urgency, components_json, computed_at)`
- `reports(id, case_id, format, path, sha256, manifest_json, generated_at)`
- `audit_log(id, ts, user_id, action, entity, entity_id, ip, detail_json)` — append-only (no UPDATE/DELETE grants; enforce in code + DB role).
- `model_registry(name, version, metrics_json, created_at, active)`

## REST API (`/api/v1`, JWT bearer)
| Method | Path | Purpose |
|---|---|---|
| POST | /auth/login | token |
| POST | /complaints | single complaint intake (address, chain, amount, time, ref) with validation |
| POST | /complaints/bulk | CSV/JSON bulk import; returns per-row validation |
| GET | /complaints | list + filters |
| POST | /cases | create case from complaint; enqueue pipeline job |
| GET | /cases/{id} | summary: risk, exits, attributions, termination reasons |
| GET | /cases/{id}/graph | nodes/edges (filters: hops, min_taint, time range) |
| GET | /cases/{id}/transfers | paginated raw canonical transfers |
| GET | /cases/{id}/evidence | raw response hashes + manifest |
| GET | /cases/{id}/events | SSE job progress |
| POST | /cases/{id}/rerun | rerun with different policy/budget |
| GET | /cases/{id}/report?format=pdf|json|csv | generate/download report |
| GET | /cases/{id}/freeze-request | draft text (docx/txt/pdf) |
| GET | /triage | ranked queue with urgency components |
| GET | /labels, POST /labels/import | label explorer / admin import |
| GET | /models | registry + metrics + model cards |
| GET | /health, /version | liveness, git SHA, mode |
All list endpoints paginate. Errors use RFC7807-style problem JSON. OpenAPI docs enabled.

## Alert/Finding schema (JSON, stable, versioned `schema_version: 1`)
```json
{
  "schema_version": 1,
  "case_id": "…",
  "generated_at": "ISO-8601",
  "mode": "live|fixture",
  "seed": {"chain": "tron", "address": "T…", "asset": "USDT-TRC20", "reported_amount": 1000.0},
  "exits": [{
    "exit_type": "VASP|P2P_OTC_SUSPECTED|PRIVATE_WALLET|MIXER|BRIDGE|DEX_SWAP|SANCTIONED|UNKNOWN",
    "entity": "ExchangeName|null",
    "tier": "CONFIRMED|PROBABLE|POSSIBLE|UNATTRIBUTED",
    "confidence": 0.0,
    "address": "…",
    "path": ["…"],
    "amount_at_risk": 0.0,
    "eta_hours": null,
    "evidence": [{"type": "tx|label|feature", "ref": "…", "detail": "…"}],
    "termination_reason": "REACHED_VASP_CONFIRMED"
  }],
  "risk": {"score": 0, "band": "HIGH", "confidence": 0.0, "signals": [], "unevaluated": []},
  "patterns": [],
  "limitations": ["…"],
  "model_versions": {"m1": "…", "m3": "…"},
  "manifest_sha256": "…"
}
```

## Integration stubs (no real access assumed)
`ComplaintSource` interface with adapters: `CsvSource`, `JsonWebhookSource`, `NcrpMockSource`, `SahyogMockSource` (fixtures shaped like plausible complaint exports). Document in `docs/INTEGRATION.md` that production integration with NCRP/SAHYOG needs official approvals and schema agreement.

## Bulk intake behavior
Validate each row, dedupe by (chain, address), auto-create cases, run pipeline with per-case budget, update `triage` incrementally, expose queue immediately with "processing" states.
