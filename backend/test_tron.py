import asyncio
from app.ingest.tron import TronGridClient
import logging
import os

logging.basicConfig(level=logging.INFO)
os.environ['TRONGRID_API_KEY'] = '18c5f8a5-f476-4454-b755-760ca190e265'

async def main():
    client = TronGridClient(api_key=os.environ['TRONGRID_API_KEY'])
    # Try a known Tron address
    addr = 'TKnABDqoTfRms2BNQDUahFqXiR32vufQi8'
    txs = await client.get_transfers(addr, limit=5)
    print(f"Found {len(txs)} txs")
    for tx in txs:
        print(tx)

asyncio.run(main())
