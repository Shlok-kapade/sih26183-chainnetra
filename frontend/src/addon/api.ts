const BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

export interface PlanAction {
  rank: number; lever: string; target: string;
  expected_secured: number; expected_secured_lo: number; expected_secured_hi: number;
  eta_hours: number; deadline_hours: number | null; illustrative_note: string;
}

export interface Plan {
  case_id: string; ev_total: number; ev_lo: number; ev_hi: number;
  illustrative_priors: boolean; illustrative_note: string; actions: PlanAction[];
}

export const fetchPlan = (caseId: string): Promise<Plan> =>
  fetch(`${BASE}/api/v1/cases/${caseId}/plan`).then(r => r.json());

export const recomputePlan = (caseId: string, seedAmount: number, K = 5) =>
  fetch(`${BASE}/api/v1/cases/${caseId}/plan/recompute`, {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ seed_amount: seedAmount, K }),
  }).then(r => r.json());

export const fetchMassMap = (caseId: string) =>
  fetch(`${BASE}/api/v1/cases/${caseId}/mass-map`).then(r => r.json());

export const fetchCohorts = (caseId: string) =>
  fetch(`${BASE}/api/v1/cases/${caseId}/cohorts`).then(r => r.json());
