with open("backend/app/addon/api/routes_addon.py", "r") as f:
    content = f.read()

import_stmt = "from .routes_cohorts import router as cohorts_router\n"
include_stmt = "router.include_router(cohorts_router, prefix=\"/cohorts\", tags=[\"cohorts\"])\n"

if "routes_cohorts" not in content:
    content = import_stmt + content
    content += "\n" + include_stmt
    
with open("backend/app/addon/api/routes_addon.py", "w") as f:
    f.write(content)
