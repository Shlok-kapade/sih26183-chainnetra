# 03 — Integration: Data, API, UI (all new files)

## New tables (one new Alembic revision; do not alter existing tables)
- `addon_cohorts(id, case_id, origin_addr, chain, asset, n_members, s_total, amount_median, amount_cv, t_start, t_end, layer, truncated, kind[SCATTER|DUST_DISPERSAL])`
- `addon_cohort_members(cohort_id, address, received_amount, ts)` — index on `address` and `(cohort_id, address)`
- `addon_cohort_edges(cohort_id, dst_ref, dst_kind[address|cluster|entity], votes, value, coverage_value, coverage_breadth, time_compactness, conservation_error, score, tier, verified)`
- `addon_mass_snapshots(case_id, t, position_ref, kind, status, value_est, value_lo, value_hi)`
- `addon_plans(id, case_id, t, ev_total, ev_lo, ev_hi, params_hash, illustrative_priors)`
- `addon_plan_actions(plan_id, rank, lever, target_ref, expected_secured, lo, hi, deadline, eta_hours, prereqs_json, doc_ref)`
- `addon_watches(case_id, position_ref, hazard, next_check, status)`
- `addon_action_outcomes(plan_action_id, outcome, ts, notes)`
Use the same DB session/base conventions as the existing project (discover in REPO_MAP.md).

## New API routes (new router files, registered with one line; same auth/RBAC dependencies as existing routes)
`GET /cases/{id}/cohorts` · `GET /cohorts/{id}` · `GET /cohorts/{id}/members?page=` · `GET /cohorts/{id}/convergence`
`GET /cases/{id}/plan` · `POST /cases/{id}/plan/recompute` (lever overrides, K) · `GET /cases/{id}/mass-map?t=` · `POST /cases/{id}/watch` · `POST /plan-actions/{id}/outcome`
Events (SSE/jobs): `plan_changed`, `mass_moved`, `cohort_found`.
Findings JSON: add an optional `addon` object (`cohorts[]`, `plan`, `unaccounted_mass`, `illustrative_priors`) — additive, schema-versioned, never change existing fields.

## Jobs (use the existing job runner)
`addon.detect_cohorts(case_id)` after trace completion · `addon.compute_plan(case_id)` after cohorts · `addon.watch_tick(case_id)` scheduled while a watch is active.

## UI (new files; minimal nav registration)
- **Action Plan tab** (hero): ranked actions with expected-secured interval and countdown ("expected value halves in ~X h") · mass-map Sankey with time slider · what-if sliders (lever success, latency, K) · "act now vs trace more" indicator with VOI explanation · live watch feed · banner "Priors are assumptions".
- **Cohort super-node + drawer**: label "Scatter cohort · 100,000 wallets · median 0.42 USDT · 3 h"; amount and arrival-time histograms; paginated member table; Sankey origin -> cohort -> collectors -> exit; chips "unaccounted %" and "verified / estimated". Never render 100k nodes in Cytoscape.
- Reuse the existing design system/components; discover them in REPO_MAP.md.

## Reports (additive)
Provide `addon/report_section.py` that returns extra sections (Action Plan, cohort convergence, assumptions + limitations) to be appended by the existing report generator via a registered hook, or as a separate downloadable `plan_report.pdf` if no hook exists (preferred, zero edits).
