from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

@dataclass
class MassPosition:
    position_ref: str
    kind: str
    status: str
    value_est: Decimal
    value_lo: Decimal
    value_hi: Decimal
    confidence: float
    chain: str
    last_seen: Optional[datetime] = None
    label: Optional[str] = None

@dataclass
class MassMap:
    case_id: str
    t: datetime
    seed_amount: Decimal
    positions: list[MassPosition]
    unresolved_total: Decimal

    def invariant_ok(self) -> bool:
        """sum(value_est) == seed_amount within 1% — mass conservation."""
        total = sum((p.value_est for p in self.positions), Decimal("0"))
        diff = abs(total - self.seed_amount)
        if self.seed_amount == 0:
            return diff == 0
        return (diff / self.seed_amount) < Decimal("0.01")

def build_mass_map(case_id: str, t: datetime, graph: dict, seed_amount: Decimal) -> MassMap:
    positions = []
    elements = graph.get("elements", [])
    
    has_outgoing = set()
    has_incoming = set()
    node_data = {}
    
    for el in elements:
        data = el.get("data", {})
        if "source" in data and "target" in data:
            has_outgoing.add(data["source"])
            has_incoming.add(data["target"])
        elif "id" in data:
            node_data[data["id"]] = data

    resolved_value = Decimal("0")
    node_incoming_value = {nid: Decimal("0") for nid in node_data}
    node_outgoing_value = {nid: Decimal("0") for nid in node_data}
    
    for el in elements:
        data = el.get("data", {})
        if "source" in data and "target" in data:
            amt = Decimal(str(data.get("amount", "0")))
            if data["target"] in node_incoming_value:
                node_incoming_value[data["target"]] += amt
            if data["source"] in node_outgoing_value:
                node_outgoing_value[data["source"]] += amt
                
    for nid, data in node_data.items():
        if nid not in has_incoming and nid in has_outgoing:
            continue
        
        role = data.get("role", "")
        val = node_incoming_value.get(nid, Decimal("0")) - node_outgoing_value.get(nid, Decimal("0"))
        
        if role == "exchange":
            status = "EXITED_VASP"
            val = node_incoming_value.get(nid, Decimal("0"))
        elif role == "mixer":
            status = "EXITED_OTHER"
            val = node_incoming_value.get(nid, Decimal("0"))
        elif nid in has_outgoing:
            status = "IN_TRANSIT"
        else:
            if nid in has_incoming:
                status = "HELD"
            else:
                continue
                
        if val > 0:
            positions.append(MassPosition(
                position_ref=nid,
                kind=data.get("type", "address"),
                status=status,
                value_est=val,
                value_lo=val * Decimal("0.8"),
                value_hi=val * Decimal("1.2"),
                confidence=float(data.get("taint", 1.0)),
                chain=data.get("chain", "ethereum"),
                label=data.get("label")
            ))
            resolved_value += val
            
    unresolved = seed_amount - resolved_value
    if unresolved > 0:
        positions.append(MassPosition(
            position_ref="_unresolved",
            kind="unresolved",
            status="UNRESOLVED",
            value_est=unresolved,
            value_lo=Decimal("0"),
            value_hi=unresolved,
            confidence=0.5,
            chain="ethereum"
        ))
        
    return MassMap(
        case_id=case_id,
        t=t,
        seed_amount=seed_amount,
        positions=positions,
        unresolved_total=max(Decimal("0"), unresolved)
    )
