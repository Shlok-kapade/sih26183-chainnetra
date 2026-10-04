with open("backend/app/addon/cohorts/service.py", "r") as f:
    content = f.read()

content = content.replace(
    "start_calls = budget.calls_used(case_id) if hasattr(budget, 'calls_used') else getattr(transfers, 'call_count', 0)",
    "start_calls = getattr(transfers, 'call_count', 0)"
)
content = content.replace(
    "end_calls = budget.calls_used(case_id) if hasattr(budget, 'calls_used') else getattr(transfers, 'call_count', 0)",
    "end_calls = getattr(transfers, 'call_count', 0)"
)
content = content.replace(
    "total_coverage = sum(c.coverage_value for c in collectors if c.tier == 'CONVERGENCE_CONFIRMED')",
    "total_coverage = sum(c.coverage_value for c in collectors if c.tier in ('CONVERGENCE_CONFIRMED', 'CONVERGENCE_PROBABLE'))"
)

with open("backend/app/addon/cohorts/service.py", "w") as f:
    f.write(content)
