import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import asyncio
import os
import time
from app.addon.adapters_fixture import FixtureTransferPort, FixtureLabelPort, FixtureTracePort, FixtureBudgetPort
from app.addon.cohorts.service import process_cohort
from scripts.addon.synth_scatter import generate_scatter

async def run_eval():
    os.makedirs("docs/evaluation", exist_ok=True)
    results_path = "docs/evaluation/ADDON_RESULTS.md"
    
    with open(results_path, "w") as f:
        f.write("# Cohorts Evaluation Results (SYNTHETIC)\n\n")
    
    for n in [100, 1000]:
        transfers, collectors = generate_scatter(seed=42, n_recipients=n, n_collectors=2, seed_amount=10000.0)
        
        port = FixtureTransferPort()
        port.transfers = transfers
        labels = FixtureLabelPort()
        trace = FixtureTracePort()
        budget = FixtureBudgetPort(100000)
        
        start_time = time.time()
        report = await process_cohort("eval_case", "ETH", "origin_wallet", "USDT", None, None, port, labels, trace, budget)
        duration = time.time() - start_time
        
        api_calls = report.api_calls_used
        naive_calls = n # 1 for origin, then 1 for each recipient
        
        # calculate precision/recall
        found_collectors = set(c.collector for c in report.collectors if c.tier in ('CONVERGENCE_CONFIRMED', 'CONVERGENCE_PROBABLE'))
        true_collectors = set(collectors)
        
        tp = len(found_collectors & true_collectors)
        fp = len(found_collectors - true_collectors)
        fn = len(true_collectors - found_collectors)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        with open(results_path, "a") as f:
            f.write(f"## SYNTHETIC Scatter N={n}\n")
            f.write(f"- True Collectors: {len(true_collectors)}\n")
            f.write(f"- Found Confirmed: {len(found_collectors)}\n")
            f.write(f"- Precision: {precision:.2f}\n")
            f.write(f"- Recall: {recall:.2f}\n")
            f.write(f"- API Calls Used: {api_calls}\n")
            f.write(f"- Naive Expand-All Calls: {naive_calls}\n")
            f.write(f"- Runtime (s): {duration:.2f}\n")
            f.write(f"- Unaccounted Mass: {report.unaccounted_mass:.2f}\n\n")

if __name__ == "__main__":
    asyncio.run(run_eval())
