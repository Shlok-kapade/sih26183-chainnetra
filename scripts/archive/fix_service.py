import re
with open("backend/app/addon/cohorts/service.py", "r") as f:
    content = f.read()

content = content.replace("class CohortReport:", "class CohortReport:\n    case_id: str\n    analysis_type: str\n    origin_address: str\n    analysis_time_ms: int\n    notes: List[str]")

with open("backend/app/addon/cohorts/service.py", "w") as f:
    f.write(content)
