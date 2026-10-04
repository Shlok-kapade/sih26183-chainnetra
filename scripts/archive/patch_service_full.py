import re
with open("backend/app/addon/cohorts/service.py", "r") as f:
    content = f.read()

content = content.replace("""        return CohortReport(
            scatter_event=None,
            collectors=[],
            unaccounted_mass=1.0,
            api_calls_used=end_calls - start_calls,
            estimated_not_verified=False
        )""", """        return CohortReport(
            case_id=case_id,
            analysis_type="scatter_gather",
            origin_address=origin,
            analysis_time_ms=0,
            notes=["No scatter event detected."],
            scatter_event=None,
            collectors=[],
            unaccounted_mass=1.0,
            api_calls_used=end_calls - start_calls,
            estimated_not_verified=False
        )""")

content = content.replace("""        return CohortReport(
            scatter_event=scatter,
            collectors=[],
            unaccounted_mass=1.0,
            api_calls_used=end_calls - start_calls,
            estimated_not_verified=False
        )""", """        return CohortReport(
            case_id=case_id,
            analysis_type="scatter_gather",
            origin_address=origin,
            analysis_time_ms=0,
            notes=["Dust dispersal detected, skipping convergence."],
            scatter_event=scatter,
            collectors=[],
            unaccounted_mass=1.0,
            api_calls_used=end_calls - start_calls,
            estimated_not_verified=False
        )""")

content = content.replace("""    return CohortReport(
        scatter_event=scatter,
        collectors=collectors,
        unaccounted_mass=unaccounted_mass,
        api_calls_used=end_calls - start_calls,
        estimated_not_verified=False
    )""", """    return CohortReport(
        case_id=case_id,
        analysis_type="scatter_gather",
        origin_address=origin,
        analysis_time_ms=0,
        notes=[],
        scatter_event=scatter,
        collectors=collectors,
        unaccounted_mass=unaccounted_mass,
        api_calls_used=end_calls - start_calls,
        estimated_not_verified=False
    )""")

with open("backend/app/addon/cohorts/service.py", "w") as f:
    f.write(content)
