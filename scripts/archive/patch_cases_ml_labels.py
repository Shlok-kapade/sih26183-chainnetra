import re

with open("backend/app/api/v1/endpoints/cases.py", "r") as f:
    content = f.read()

# Update create_case
new_logic = """
    if is_demo:
        new_case.exit_type = "EXCHANGE"
        new_case.attribution_tier = "CONFIRMED"
        new_case.exit_entity = "Huobi (Hot Wallet)"
        new_case.urgency_factors = ["High value transfer (+40 pts)", "High velocity cross-border (+30 pts)", "Time since incident < 24h (+20 pts)"]
        new_case.timeline = {"Reported": "Today, 09:10 AM", "First Hop": "Today, 09:15 AM", "Last Seen": "Today, 10:45 AM"}
        
        # Inject the third demo graph
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
        
        # Use our "real" ML model to score it!
        new_case.ml_signals = score_graph(graphs_db[case_id]["elements"])
        
        # Use our "real" label database to find the exit entity!
        entity_info = get_entity_for_address("TKnABDqoTfRms2BNQDUahFqXiR32vufQi8")
        if entity_info:
            new_case.exit_entity = entity_info['entity']
            new_case.exit_type = entity_info['entity_type'].upper()
"""

# Replace the specific block in create_case
pattern = re.compile(r"    if is_demo:.*?    else:", re.DOTALL)
content = re.sub(pattern, new_logic + "\n    else:", content)

with open("backend/app/api/v1/endpoints/cases.py", "w") as f:
    f.write(content)
