with open("backend/app/addon/cohorts/verify.py", "r") as f:
    content = f.read()

content = content.replace("async for item in transfers.incoming(chain, query_addr, asset, since=t_start, until=t_end, max_pages=10):", "print('Querying inbound:', query_addr, t_start, t_end)\n        async for item in transfers.incoming(chain, query_addr, asset, since=t_start, until=t_end, max_pages=10):\n            print('Yielded item:', item)")

with open("backend/app/addon/cohorts/verify.py", "w") as f:
    f.write(content)
