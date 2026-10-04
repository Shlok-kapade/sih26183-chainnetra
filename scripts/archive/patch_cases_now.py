import re

with open("backend/app/api/v1/endpoints/cases.py", "r") as f:
    content = f.read()

content = content.replace("Timestamp: {now.isoformat()}", "Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")

with open("backend/app/api/v1/endpoints/cases.py", "w") as f:
    f.write(content)
