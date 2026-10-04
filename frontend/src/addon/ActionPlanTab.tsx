import { useState, useEffect } from 'react';
import type { Plan } from './api';
import { fetchPlan, recomputePlan } from './api';

export default function ActionPlanTab({ caseId }: { caseId: string }) {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(false);
  const [seedAmount, setSeedAmount] = useState('9000');

  useEffect(() => {
    loadPlan();
  }, [caseId]);

  const loadPlan = async () => {
    try {
      const p = await fetchPlan(caseId);
      if (p && !(p as any).message) setPlan(p as any);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRecompute = async () => {
    setLoading(true);
    try {
      const p = await recomputePlan(caseId, parseFloat(seedAmount));
      setPlan(p);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 20 }}>
      <div style={{ backgroundColor: '#fff3cd', color: '#856404', padding: 10, marginBottom: 20, borderRadius: 4 }}>
        ⚠️ Priors (p_success, latency) are ILLUSTRATIVE assumptions — not real-world freeze rates
      </div>
      
      <div style={{ marginBottom: 20 }}>
        <input 
          type="number" 
          value={seedAmount} 
          onChange={e => setSeedAmount(e.target.value)}
          style={{ marginRight: 10, padding: 5 }}
        />
        <button onClick={handleRecompute} disabled={loading} style={{ padding: '5px 10px' }}>
          {loading ? 'Recomputing...' : 'Recompute Plan'}
        </button>
      </div>

      {plan ? (
        <div>
          <h3>Expected Secured: ${Number(plan.ev_total).toFixed(2)} [${Number(plan.ev_lo).toFixed(2)} - ${Number(plan.ev_hi).toFixed(2)}]</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {plan.actions?.map((a: any) => (
              <li key={a.rank} style={{ border: '1px solid #ccc', margin: '10px 0', padding: 10, borderRadius: 4 }}>
                <strong>#{a.rank} 
                  <span style={{ 
                    marginLeft: 10, padding: '2px 6px', borderRadius: 4, color: 'white',
                    backgroundColor: a.lever === 'VASP_HOLD' ? 'orange' : a.lever === 'ISSUER_BLACKLIST' ? 'blue' : a.lever === 'LEGAL_ESCALATION' ? 'red' : 'gray'
                  }}>
                    {a.lever}
                  </span>
                </strong>
                <div style={{ marginTop: 5 }}>Target: {a.target_ref || a.target || 'unknown'}</div>
                <div>Expected secured: ${Number(a.expected_secured).toFixed(2)} [${Number(a.expected_secured_lo).toFixed(2)} - ${Number(a.expected_secured_hi).toFixed(2)}]</div>
                <div style={{ display: 'inline-block', backgroundColor: '#e9ecef', padding: '2px 6px', borderRadius: 10, fontSize: '0.8em', marginTop: 5 }}>
                  {a.eta_hours}h to execute
                </div>
                <div style={{ fontStyle: 'italic', fontSize: '0.8em', marginTop: 5, color: '#666' }}>{a.illustrative_note}</div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div>No plan available. Recompute first.</div>
      )}
    </div>
  );
}
