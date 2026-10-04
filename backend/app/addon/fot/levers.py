from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from .mass_map import MassMap
import yaml
import os

@dataclass
class LeverOption:
    lever_type: str
    target_ref: str
    p_success: float
    latency_hours: float
    hold_validity_days: int
    applicable_value: Decimal
    illustrative: bool = True

def get_lever_options(mass_map: MassMap) -> list[LeverOption]:
    levers_path = os.path.join(os.path.dirname(__file__), "../../../config/addon/levers.yaml")
    config = {}
    if os.path.exists(levers_path):
        with open(levers_path, "r") as f:
            config = yaml.safe_load(f) or {}
            
    options = []
    
    for pos in mass_map.positions:
        if pos.status == "EXITED_VASP":
            ent_config = config.get("entities", {}).get(pos.position_ref, {})
            options.append(LeverOption(
                lever_type="VASP_HOLD",
                target_ref=pos.position_ref,
                p_success=ent_config.get("p_success", 0.5),
                latency_hours=ent_config.get("latency_hours", 24.0),
                hold_validity_days=ent_config.get("hold_validity_days", 7),
                applicable_value=pos.value_est
            ))
        elif pos.status == "HELD":
            if pos.chain == "ethereum":
                options.append(LeverOption(
                    lever_type="ISSUER_BLACKLIST",
                    target_ref=pos.position_ref,
                    p_success=0.8,
                    latency_hours=48.0,
                    hold_validity_days=365,
                    applicable_value=pos.value_est
                ))
            else:
                options.append(LeverOption(
                    lever_type="WATCH",
                    target_ref=pos.position_ref,
                    p_success=0.1,
                    latency_hours=0.0,
                    hold_validity_days=0,
                    applicable_value=pos.value_est
                ))
        elif pos.status == "IN_TRANSIT":
            options.append(LeverOption(
                lever_type="WATCH",
                target_ref=pos.position_ref,
                p_success=0.1,
                latency_hours=0.0,
                hold_validity_days=0,
                applicable_value=pos.value_est
            ))
            
    return options
