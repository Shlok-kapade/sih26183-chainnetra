import re

with open("backend/app/addon/adapters_fixture.py", "r") as f:
    content = f.read()

content = content.replace("""    async def incoming(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        self.call_count += 1
        yield {}""", "")

with open("backend/app/addon/adapters_fixture.py", "w") as f:
    f.write(content)
