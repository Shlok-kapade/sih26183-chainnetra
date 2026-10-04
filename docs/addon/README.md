# ChainNetra ADD-ON pack (new files only)

For a repo that already contains the base ChainNetra build. **Nothing in your existing spec files needs editing.** These files add two capabilities:
1. **Scatter–gather cohort tracing** (one wallet -> up to ~100k wallets -> convergence).
2. **Freeze-Optimal Tracing (FOT)** — the core invention (mass map, freeze levers, planner, value-of-information tracing, live frontier watch).

## How to use
1. Copy this folder into the repo as `docs/addon/` (all files stay new; nothing overwritten).
2. Open the repo in Antigravity. Paste `ADDON_AGENTS.md` into a Workspace rule (or keep it at `docs/addon/ADDON_AGENTS.md` and tell the agent to read it).
3. Run the prompts in `05_BUILD_PLAN_AND_PROMPTS.md` in order. Step 0 makes the agent audit your existing code first, so the add-on fits whatever structure you actually have.

## Files
| File | Purpose |
|---|---|
| ADDON_AGENTS.md | Rules for the agent (additive-only integration) |
| 00_ADDON_OVERVIEW.md | What is added, ports/adapters seam, folder layout, feature flags |
| 01_SCATTER_GATHER_ADDON.md | Cohort detection, sample–vote–verify, convergence scoring |
| 02_FOT_CORE_ADDON.md | The core invention, full spec |
| 03_INTEGRATION_DATA_API_UI.md | New tables (own migration), new routers, new UI files |
| 04_EVAL_ADDON.md | Replay evaluation, synthetic scenarios, metrics |
| 05_BUILD_PLAN_AND_PROMPTS.md | Phases + copy-paste prompts |
| 06_PPT_AND_GUIDE_ADDON.md | Slide inserts for your teammate + plain-language explanation |
