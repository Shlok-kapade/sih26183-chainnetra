import { useState, useEffect } from 'react';

interface WatchStatus {
  case_id: string;
  watching: boolean;
  position_ref?: string;
  status?: string;
  last_hazard?: number;
  note?: string;
}

interface WatchFeedProps {
  caseId: string;
}

const BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

export default function WatchFeed({ caseId }: WatchFeedProps) {
  const [status, setStatus] = useState<WatchStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [position, setPosition] = useState('');
  const [value, setValue] = useState('');
  const [seedAmount, setSeedAmount] = useState('');

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${BASE}/api/v1/cases/${caseId}/watch`);
      const data = await res.json();
      setStatus(data);
    } catch {}
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, [caseId]);

  const startWatch = async () => {
    setLoading(true);
    try {
      await fetch(`${BASE}/api/v1/cases/${caseId}/watch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          position_ref: position,
          value: parseFloat(value),
          seed_amount: parseFloat(seedAmount),
        }),
      });
      await fetchStatus();
    } finally {
      setLoading(false);
    }
  };

  const hazardColor = (h: number) =>
    h > 0.20 ? '#ef4444' : h > 0.10 ? '#f97316' : '#22c55e';

  return (
    <div style={{ padding: '16px', fontFamily: 'monospace' }}>
      <h3 style={{ marginBottom: 8 }}>👁️ Frontier Watch</h3>
      <div style={{
        background: '#fef3c7', border: '1px solid #f59e0b',
        borderRadius: 6, padding: '8px 12px', marginBottom: 16, fontSize: 12,
      }}>
        ⚠️ Hazard estimates use ILLUSTRATIVE model coefficients — not calibrated to real-world data.
      </div>
      {!status?.watching ? (
        <div>
          <p style={{ color: '#6b7280' }}>No active watch.</p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
            <input placeholder="Position ref (address)" value={position}
              onChange={e => setPosition(e.target.value)}
              style={{ padding: '4px 8px', borderRadius: 4, border: '1px solid #d1d5db', flex: 2 }} />
            <input placeholder="Value" value={value}
              onChange={e => setValue(e.target.value)}
              style={{ padding: '4px 8px', borderRadius: 4, border: '1px solid #d1d5db', flex: 1 }} />
            <input placeholder="Seed amount" value={seedAmount}
              onChange={e => setSeedAmount(e.target.value)}
              style={{ padding: '4px 8px', borderRadius: 4, border: '1px solid #d1d5db', flex: 1 }} />
          </div>
          <button onClick={startWatch} disabled={loading || !position || !value || !seedAmount}
            style={{ background: '#3b82f6', color: 'white', border: 'none', borderRadius: 4,
              padding: '6px 16px', cursor: 'pointer', opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Starting...' : 'Start Watch'}
          </button>
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <span style={{
              width: 10, height: 10, borderRadius: '50%',
              background: status.status === 'triggered' ? '#ef4444' : '#22c55e',
              display: 'inline-block',
            }} />
            <span style={{ fontWeight: 600 }}>
              {status.status === 'triggered' ? 'Movement Detected!' : 'Watching'}
            </span>
          </div>
          <div style={{ fontSize: 13, color: '#374151' }}>
            <div><strong>Position:</strong> {status.position_ref}</div>
            {status.last_hazard !== undefined && (
              <div style={{ marginTop: 6 }}>
                <strong>Hazard (1h):</strong>{' '}
                <span style={{ color: hazardColor(status.last_hazard), fontWeight: 600 }}>
                  {(status.last_hazard * 100).toFixed(1)}%
                </span>
                <span style={{ color: '#9ca3af', fontSize: 11 }}> (ILLUSTRATIVE)</span>
              </div>
            )}
            {status.note && (
              <div style={{ marginTop: 6, color: '#6b7280', fontSize: 11 }}>{status.note}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
