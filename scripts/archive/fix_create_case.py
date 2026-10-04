import re

with open("backend/app/api/v1/endpoints/cases.py", "r") as f:
    content = f.read()

# Define exactly what create_case should look like
new_create_case = r"""
@router.post("/", response_model=Case)
def create_case(case_in: CaseCreate):
    case_id = f"CASE-{len(cases_db) + 7281:04d}"
    now = datetime.datetime.now(datetime.timezone.utc)
    
    new_case = Case(
        id=case_id,
        created_at=now,
        updated_at=now,
        **case_in.model_dump()
    )

    is_demo = "Pig Butchering" in case_in.title

    if is_demo:
        new_case.exit_type = "EXCHANGE"
        new_case.attribution_tier = "CONFIRMED"
        new_case.exit_entity = "Huobi (Hot Wallet)"
        new_case.urgency_factors = ["High value transfer (+40 pts)", "High velocity cross-border (+30 pts)", "Time since incident < 24h (+20 pts)"]
        new_case.timeline = {"Reported": "Today, 09:10 AM", "First Hop": "Today, 09:15 AM", "Last Seen": "Today, 10:45 AM"}
        
        graphs_db[case_id] = {
            "elements": [
                { "data": { "id": "victim", "label": "Victim\\n2.5M USDT", "role": "victim", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": "scammer1", "label": "Scammer\\nCollection", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": "layer1", "label": "Layering 1", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": "layer2", "label": "Layering 2", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8", "label": "Binance\\nHot Wallet", "role": "exchange", "taint": 0.0, "type": "exchange" } },
                
                { "data": { "source": "victim", "target": "scammer1", "amount": "2.5M USDT" } },
                { "data": { "source": "scammer1", "target": "layer1", "amount": "2.5M USDT" } },
                { "data": { "source": "layer1", "target": "layer2", "amount": "2.5M USDT" } },
                { "data": { "source": "layer2", "target": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8", "amount": "2.5M USDT" } }
            ]
        }
        
        new_case.ml_signals = score_graph(graphs_db[case_id]["elements"])
        
        entity_info = get_entity_for_address("TKnABDqoTfRms2BNQDUahFqXiR32vufQi8")
        if entity_info:
            new_case.exit_entity = entity_info['entity']
            new_case.exit_type = entity_info['entity_type'].upper()
    else:
        new_case.exit_type = "UNKNOWN"
        new_case.attribution_tier = "UNATTRIBUTED"
        new_case.exit_entity = "Unknown"
        new_case.urgency_factors = ["Unknown"]
        new_case.timeline = {"Reported": "Today", "First Hop": "Unknown", "Last Seen": "Unknown"}
        new_case.ml_signals = {"exchange": 0.0, "mixer": 0.0, "service": 0.0}
        
        graphs_db[case_id] = {
            "elements": [
                { "data": { "id": "victim", "label": "Victim", "role": "victim", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": "unknown", "label": "Unknown", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "source": "victim", "target": "unknown", "amount": f"{new_case.amount_at_risk} {new_case.asset}" } }
            ]
        }

    cases_db[case_id] = new_case
    return new_case
"""

# Replace the entire function using regex
pattern = re.compile(r"@router\.post\(\"/\", response_model=Case\)\ndef create_case.*?return new_case", re.DOTALL)

# Handle literal \n properly by using a lambda replacement
content = re.sub(pattern, lambda m: new_create_case.strip(), content)

with open("backend/app/api/v1/endpoints/cases.py", "w") as f:
    f.write(content)
