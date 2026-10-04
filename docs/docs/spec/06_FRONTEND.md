# 06 — Frontend Spec

Design: clean, dense, investigator-grade dashboard. Dark mode default + light. Keyboard accessible, WCAG AA contrast, responsive down to tablet. Loading skeletons, empty states, error banners. Global mode badge: LIVE / FIXTURE. Every screen surfaces limitations and confidence.

## Pages
1. **Login**.
2. **Triage Queue (home)**: table of cases ranked by urgency; columns = ref, chain, amount at risk, exit type, tier badge, risk band, ETA-to-cash-out, freshness, status. Row expand shows urgency components. Bulk import button (CSV drag-drop with validation preview). Filters: chain, tier, exit type, band.
3. **New Case**: address + chain (auto-detect from format) + amount/time + policy (guided/BFS) + budget slider (API calls) + mode.
4. **Case Workspace** (tabs):
   - **Overview**: headline card "Likely cash-out: <entity|exit type> — <tier>, confidence x%", amount at risk, time window, termination reasons, top 3 evidence bullets, limitations banner, buttons: Report, Freeze draft, Rerun.
   - **Graph**: Cytoscape fcose layout. Node color = role/exit type; shape = chain; size = taint value; edge width = taint share; edge label = amount. Controls: hop filter, min-taint slider, time slider/replay animation, collapse fan-outs, search address, highlight main path, cluster hulls. Click node -> side drawer: labels, M1 role probabilities (bar chart), **SHAP "why"**, transfers list with explorer links, attribution evidence. Export PNG/SVG.
   - **Timeline**: swimlane of transfers by hop with dwell times; shows freeze window.
   - **Patterns**: detected patterns with score, evidence, false-positive notes.
   - **Attribution**: table of addresses with tier, entity, confidence, evidence; CONFIRMED/PROBABLE/POSSIBLE/UNATTRIBUTED filters.
   - **Risk**: itemized signals table (raw, weight, points), unevaluated signals, confidence.
   - **Evidence**: raw response hashes, manifest, audit trail, verify-hash tool (upload report -> recompute SHA-256).
   - **Trace Efficiency** (differentiator): chart of exits found vs API calls for this case comparing the chosen policy with a BFS re-simulation from cache.
5. **Model Center**: model cards, metrics tables/plots (PR curves, reliability diagram, confusion matrices, leave-one-exchange-out table), version selector. Data comes from `metrics.json` (no hardcoded numbers).
6. **Label Explorer**: search/filter labels with source + license; admin import.
7. **Admin**: users, config viewer (trace/risk YAML, read-only), audit log viewer.

## UX details
- Progress via SSE with stage names (Ingesting → Tracing → Classifying → Patterns → Attribution → Report) and API-call counter vs budget.
- Confidence badges: CONFIRMED (solid), PROBABLE, POSSIBLE (outlined), UNATTRIBUTED (gray). Always paired with a tooltip that explains the tier rule.
- Never show a bare score without its confidence and the "investigative lead, not proof" note.
- Copy-to-clipboard for addresses/hashes; deep links to public explorers (Tronscan, Etherscan, mempool.space).
- Print-friendly report preview.
