import re

with open("backend/app/api/v1/endpoints/cases.py", "r") as f:
    content = f.read()

# Add import
import_stmt = "from app.attribution import get_entity_for_address\n"
if "from app.attribution" not in content:
    content = import_stmt + content

# When case is returned, we can try to find attribution
with open("backend/app/api/v1/endpoints/cases.py", "w") as f:
    f.write(content)
