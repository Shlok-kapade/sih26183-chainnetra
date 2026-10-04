import asyncio
from backend.app.addon.adapters_fixture import FixtureTransferPort, FixtureLabelPort, FixtureTracePort, FixtureBudgetPort
from backend.app.addon.cohorts.service import process_cohort
from scripts.addon.synth_scatter import generate_scatter

async def main():
    transfers, collectors = generate_scatter(seed=42, n_recipients=100, n_collectors=2, seed_amount=10000.0)
    port = FixtureTransferPort()
    port.transfers = transfers
    labels = FixtureLabelPort()
    trace = FixtureTracePort()
    budget = FixtureBudgetPort(100000)
    report = await process_cohort("eval_case", "ETH", "origin_wallet", "USDT", None, None, port, labels, trace, budget)
    for c in report.collectors:
        print(c.collector, c.tier)

asyncio.run(main())
