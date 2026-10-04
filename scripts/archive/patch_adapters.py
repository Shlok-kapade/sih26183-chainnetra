import re

with open("backend/app/addon/adapters_fixture.py", "r") as f:
    content = f.read()

# Replace FixtureTransferPort
new_port = """class FixtureTransferPort:
    def __init__(self):
        self.call_count = 0
        self.transfers = [] # list of Transfer objects
    async def outgoing(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        self.call_count += 1
        for t in self.transfers:
            if t.from_addr == address and t.chain == chain and t.asset == asset:
                if since and t.ts < since: continue
                if until and t.ts > until: continue
                yield t
    async def incoming(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        self.call_count += 1
        for t in self.transfers:
            if t.to_addr == address and t.chain == chain and t.asset == asset:
                if since and t.ts < since: continue
                if until and t.ts > until: continue
                yield t
"""
content = re.sub(r'class FixtureTransferPort:.*?yield \{\}', new_port, content, flags=re.DOTALL)

with open("backend/app/addon/adapters_fixture.py", "w") as f:
    f.write(content)
