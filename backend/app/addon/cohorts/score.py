import yaml
import os
from dataclasses import dataclass
from typing import Optional, List
from app.addon.cohorts.verify import CollectorVerification

@dataclass
class ConvergenceResult:
    collector: str
    is_cluster: bool
    cluster_entity: Optional[str]
    coverage_value: float
    coverage_breadth: float
    time_compactness: float
    conservation_error: float
    score: float
    tier: str
    false_positive_note: Optional[str] = None

def load_weights():
    # default weights
    weights = {
        'coverage_value': 0.40,
        'coverage_breadth': 0.20,
        'time_compactness': 0.15,
        'conservation_error': 0.15,
        'novelty': 0.10
    }
    path = os.path.join(os.path.dirname(__file__), "../../../config/addon/convergence.yaml")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'weights' in data:
                    weights.update(data['weights'])
        except Exception:
            pass
    return weights

def score_collectors(verifications: List[CollectorVerification], verified: bool = True) -> List[ConvergenceResult]:
    weights = load_weights()
    results = []
    
    for v in verifications:
        # novelty is 1.0 by default unless we know it's not novel
        novelty = 1.0
        
        score = (
            weights['coverage_value'] * v.coverage_value +
            weights['coverage_breadth'] * v.coverage_breadth +
            weights['time_compactness'] * v.time_compactness +
            weights['conservation_error'] * max(0.0, 1.0 - v.conservation_error) +
            weights['novelty'] * novelty
        )
        
        tier = "NONE"
        if score >= 0.80 and verified:
            tier = "CONVERGENCE_CONFIRMED"
        elif score >= 0.50:
            tier = "CONVERGENCE_PROBABLE"
            
        results.append(ConvergenceResult(
            collector=v.collector,
            is_cluster=v.is_cluster,
            cluster_entity=v.cluster_entity,
            coverage_value=v.coverage_value,
            coverage_breadth=v.coverage_breadth,
            time_compactness=v.time_compactness,
            conservation_error=v.conservation_error,
            score=score,
            tier=tier,
            false_positive_note=v.false_positive_note
        ))
        
    return results
