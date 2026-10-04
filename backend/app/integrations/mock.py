import asyncio
from datetime import datetime, timezone


async def mock_ncrp_sync():
    """Mock integration: Polling NCRP portal for new complaints"""
    return [
        {
            "external_ref": f"NCRP-{int(datetime.now().timestamp())}",
            "source": "ncrp",
            "chain": "tron",
            "address": "TLJ3q1U8H7k4ZcW5L1H8L1rXz4L1RzXzL1",
            "reported_amount": 50000.0,
            "reported_asset": "USDT",
            "reported_at": datetime.now(timezone.utc)
        }
    ]

async def mock_sahyog_push(case_id: int, report_hash: str):
    """Mock integration: Push final intel report to SAHYOG"""
    await asyncio.sleep(1)
    return {"status": "success", "sahyog_ref": f"SHY-{case_id}"}
