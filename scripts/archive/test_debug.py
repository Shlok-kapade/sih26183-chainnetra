import asyncio
from backend.app.addon.adapters_fixture import FixtureTransferPort, FixtureLabelPort
from backend.app.addon.cohorts.detect import detect_scatter
from backend.app.addon.cohorts.sample_vote import sample_vote
from backend.app.addon.cohorts.verify import verify_collectors
from scripts.addon.synth_scatter import generate_scatter

async def main():
    transfers, collectors = generate_scatter(42, 100, 1, 10000.0)
    port = FixtureTransferPort()
    port.transfers = transfers
    labels = FixtureLabelPort()
    
    scatter = await detect_scatter(port, "ETH", "origin_wallet", "USDT", None, None, k_scatter=50)
    candidates = await sample_vote(scatter, port, labels, "ETH", "USDT", m=300)
    print("Candidates:", candidates)
    
    verifications = await verify_collectors(scatter, candidates, port, labels, "ETH", "USDT")
    print("Verifications:", verifications)

asyncio.run(main())
