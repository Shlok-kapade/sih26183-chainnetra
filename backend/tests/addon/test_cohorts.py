import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import pytest
from datetime import datetime
from app.addon.adapters_fixture import FixtureTransferPort, FixtureLabelPort, FixtureTracePort, FixtureBudgetPort
from app.addon.cohorts.service import process_cohort
from app.addon.cohorts.detect import detect_scatter
from app.addon.cohorts.sample_vote import sample_vote
from app.addon.cohorts.verify import verify_collectors
from app.addon.cohorts.score import score_collectors
from scripts.addon.synth_scatter import generate_scatter, generate_benign_airdrop, generate_dust_attack

@pytest.mark.asyncio
async def test_detect_scatter_basic():
    transfers, _ = generate_scatter(42, 100, 1, 10000.0)
    port = FixtureTransferPort()
    port.transfers = transfers
    
    scatter = await detect_scatter(port, "ETH", "origin_wallet", "USDT", None, None, k_scatter=50)
    assert scatter is not None
    assert scatter.n == 100
    assert scatter.kind == 'scatter'

@pytest.mark.asyncio
async def test_detect_scatter_too_few():
    transfers, _ = generate_scatter(42, 10, 1, 1000.0)
    port = FixtureTransferPort()
    port.transfers = transfers
    
    scatter = await detect_scatter(port, "ETH", "origin_wallet", "USDT", None, None, k_scatter=50)
    assert scatter is None

@pytest.mark.asyncio
async def test_detect_dust_dispersal():
    transfers = generate_dust_attack(42, 100)
    port = FixtureTransferPort()
    port.transfers = transfers
    
    scatter = await detect_scatter(port, "ETH", "attacker_wallet", "ETH", None, None, k_scatter=50)
    assert scatter is not None
    assert scatter.kind == 'dust_dispersal'

@pytest.mark.asyncio
async def test_verify_collectors_coverage():
    transfers, collectors = generate_scatter(42, 100, 1, 10000.0)
    port = FixtureTransferPort()
    port.transfers = transfers
    labels = FixtureLabelPort()
    
    scatter = await detect_scatter(port, "ETH", "origin_wallet", "USDT", None, None, k_scatter=50)
    candidates = await sample_vote(scatter, port, labels, "ETH", "USDT", m=300)
    assert len(candidates) > 0
    assert candidates[0].destination == collectors[0]
    
    verifications = await verify_collectors(scatter, candidates, port, labels, "ETH", "USDT")
    assert verifications[0].coverage_value > 0.95

@pytest.mark.asyncio
async def test_score_confirmed():
    transfers, _ = generate_scatter(42, 100, 1, 10000.0)
    port = FixtureTransferPort()
    port.transfers = transfers
    labels = FixtureLabelPort()
    
    scatter = await detect_scatter(port, "ETH", "origin_wallet", "USDT", None, None, k_scatter=50)
    candidates = await sample_vote(scatter, port, labels, "ETH", "USDT", m=300)
    verifications = await verify_collectors(scatter, candidates, port, labels, "ETH", "USDT")
    
    results = score_collectors(verifications, verified=True)
    assert results[0].tier == 'CONVERGENCE_CONFIRMED'

@pytest.mark.asyncio
async def test_score_none():
    transfers, _ = generate_scatter(42, 100, 1, 10000.0)
    # create decoy verifications
    from app.addon.cohorts.verify import CollectorVerification
    v = CollectorVerification("decoy", False, None, 0.1, 0.1, 0.0, 1.0)
    results = score_collectors([v], verified=True)
    assert results[0].tier == 'NONE'

@pytest.mark.asyncio
async def test_benign_airdrop_no_expansion():
    transfers = generate_benign_airdrop(42, 100)
    port = FixtureTransferPort()
    port.transfers = transfers
    labels = FixtureLabelPort()
    trace = FixtureTracePort()
    budget = FixtureBudgetPort(1000)
    
    report = await process_cohort("c1", "ETH", "airdrop_contract", "TOKEN", None, None, port, labels, trace, budget)
    assert len(report.collectors) == 0

@pytest.mark.asyncio
async def test_dust_not_expanded():
    transfers = generate_dust_attack(42, 100)
    port = FixtureTransferPort()
    port.transfers = transfers
    labels = FixtureLabelPort()
    trace = FixtureTracePort()
    budget = FixtureBudgetPort(1000)
    
    report = await process_cohort("c1", "ETH", "attacker_wallet", "ETH", None, None, port, labels, trace, budget)
    assert report.scatter_event.kind == 'dust_dispersal'
    assert report.unaccounted_mass == 1.0
    assert len(report.collectors) == 0
