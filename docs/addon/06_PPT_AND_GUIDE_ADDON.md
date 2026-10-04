# 06 — PPT inserts + plain-language guide for the new parts (standalone; does not modify your existing PPT brief)

## A. What the new parts are (for you)
- **Scatter–gather cohorts**: when one wallet splits money into thousands of tiny transfers and later merges it again, ChainNetra treats the thousands of wallets as one *cohort*, samples a few hundred to see where they send money, votes on likely collector wallets, then verifies against *all* cohort wallets by checking the collector's incoming transfers. It reports how much was accounted for and how much is unaccounted.
- **Freeze-Optimal Tracing (core invention)**: instead of only saying "this address is an exchange", ChainNetra estimates where the stolen money probably is *now* (with uncertainty), knows two freeze levers (exchange hold; stablecoin-issuer blacklist of an address) with delays, and picks the actions with the highest expected secured value. It also decides whether one more tracing step is worth the delay, and a live watch updates the plan when funds move.
- **What is NOT claimed as new**: scatter–gather detection (known AML pattern), GNNs, contrastive subgraph embeddings. **Assumptions**: freeze success/latency numbers are illustrative priors; we test how stable the plan is when they change.

## B. Slide inserts (give to your teammate)
**Insert after "Proposed Solution" — Slide: Core Innovation — Freeze-Optimal Tracing**
- Most tools answer "what is this address?"; investigators need "what should I freeze, where, by when?"
- Mass map: where the stolen money probably is now (with uncertainty bounds)
- Two freeze levers: exchange hold · stablecoin-issuer address blacklist (+ legal escalation)
- Planner: picks actions with highest expected secured value (greedy, provable (1−1/e) bound)
- Smart tracing: spends API calls only where they improve the plan; "act now vs trace more"
- Live watch: plan updates when funds move
Visual: left = money map over time (Sankey); right = ranked action list with countdowns.
Footer note: "Success/latency values are illustrative priors; robustness tested by sensitivity analysis."

**Insert in "Technical Approach" — Slide: Split-and-Converge Tracing**
- Scatter to thousands of wallets → treated as one *cohort*
- Sample → vote → verify against the full set (no need to query every wallet)
- Output: collectors + coverage % + unaccounted %
- Handles look-alikes: airdrops, bulk withdrawals, dust attacks
Visual: origin → fan of dots → 2 collector nodes → exchange.

**Insert in "AI/ML Models" table**
| M8 | Probability funds move in the next Δ | Survival model (LightGBM) |
| M9 (stretch) | Link complaints from the same operation | Split-half contrastive embeddings |

**Insert in "Impact"**: "Aims to increase the share of stolen value frozen by prioritising actions by expected secured value (to be measured in replay evaluation)."

**Claim wording (use as written):** "To our knowledge, existing open work focuses on detection/classification and tracing heuristics; we are not aware of an open framework that plans freeze actions by expected secured value, separating exchange holds from stablecoin-issuer blacklists and deciding when to trace more vs act." Do not say "first in the world". Do not quote results until `ADDON_RESULTS.md` exists.

## C. Extra jury questions
- *Where do the freeze success rates come from?* They are configurable assumptions; the contribution is the decision framework and its robustness; real rates can be learned from outcome logs.
- *Can the issuer really freeze it?* Stablecoin issuers have frozen funds on law-enforcement request; it needs official channels and is not guaranteed.
- *Is scatter–gather new?* No, it is a known pattern; our contribution is budget-aware verification and feeding the result into freeze planning.
- *How do you handle 100k wallets with free APIs?* Enumerate once, sample for votes, verify via collector inbound with set membership — roughly n/200 + a few hundred calls instead of n.
