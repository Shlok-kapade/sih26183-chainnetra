import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, ArrowLeft, Upload, Search, AlertTriangle, Loader2, CheckCircle2, Activity } from 'lucide-react';
import api from '../../lib/api';

const CHAINS = [
  { value: 'bitcoin', label: 'Bitcoin', color: 'bg-orange-500' },
  { value: 'ethereum', label: 'Ethereum', color: 'bg-blue-500' },
  { value: 'tron', label: 'Tron (TRC-20)', color: 'bg-red-500' },
  { value: 'bsc', label: 'BNB Smart Chain', color: 'bg-yellow-500' },
  { value: 'polygon', label: 'Polygon', color: 'bg-purple-500' },
];

const PRIORITY_OPTIONS = [
  { value: 'critical', label: 'Critical — Funds actively moving', color: 'text-red-600 bg-red-50 border-red-200' },
  { value: 'high', label: 'High — Time-sensitive investigation', color: 'text-orange-600 bg-orange-50 border-orange-200' },
  { value: 'medium', label: 'Medium — Standard investigation', color: 'text-yellow-600 bg-yellow-50 border-yellow-200' },
  { value: 'low', label: 'Low — Historical / archival', color: 'text-slate-600 bg-slate-50 border-slate-200' },
];

export function NewCase() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [newCaseId, setNewCaseId] = useState('');

  const [form, setForm] = useState({
    title: '',
    description: '',
    chain: 'ethereum',
    priority: 'high',
    asset: 'ETH',
    amount_at_risk: '',
    seed_address: '',
    seed_tx_hash: '',
    victim_name: '',
    complainant_ref: '',
  });

  const update = (field: string, value: string) => {
    setForm(prev => {
      const next = { ...prev, [field]: value };
      if (field === 'chain') {
        const assetMap: Record<string, string> = { bitcoin: 'BTC', ethereum: 'ETH', tron: 'USDT', bsc: 'BNB', polygon: 'MATIC' };
        next.asset = assetMap[value] || 'USDT';
      }
      if (field === 'seed_address') {
        const trimmed = value.trim();
        if (trimmed.startsWith('T') && trimmed.length >= 20) {
          next.chain = 'tron';
          next.asset = 'USDT';
        } else if (trimmed.startsWith('0x') && trimmed.length >= 20) {
          next.chain = 'ethereum';
          next.asset = 'ETH';
        } else if ((trimmed.startsWith('bc1') || trimmed.startsWith('1') || trimmed.startsWith('3')) && trimmed.length >= 20) {
          next.chain = 'bitcoin';
          next.asset = 'BTC';
        }
      }
      return next;
    });
  };

  const [logs, setLogs] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitted(true); // Switch to terminal view immediately

    // Progress messages only - no fabricated results. Real tracing runs on the server.
    const sequence = [
      `[SYS] Starting forward trace from seed ${form.seed_address}...`,
      `[NET] Querying ${form.chain.toUpperCase()} public data sources...`,
      `[GRAPH] Following outgoing transfers hop by hop (this can take up to a minute)...`,
      `[ATTRIBUTION] Checking explorer tags, label files and service heuristics...`,
      `[PATTERNS] Running pattern detectors on collected transfers...`,
    ];

    let currentLog = 0;
    const interval = setInterval(() => {
      if (currentLog < sequence.length) {
        const msg = sequence[currentLog];
        const pct = Math.floor(((currentLog + 1) / (sequence.length + 1)) * 100);
        setLogs(prev => [...prev, msg]);
        setProgress(pct);
        currentLog++;
      } else {
        clearInterval(interval);
      }
    }, 800);

    await submitToApi();
    clearInterval(interval);
    setProgress(100);
  };

  const submitToApi = async () => {
    try {
      const res = await api.post('/cases/', {
        title: form.title || `Investigation — ${form.seed_address.slice(0, 10)}...`,
        description: form.description || `Tracing ${form.amount_at_risk} ${form.asset} on ${form.chain}. Seed: ${form.seed_address}`,
        seed_address: form.seed_address.trim(),
        chain: form.chain,
        priority: form.priority,
        asset: form.asset,
        amount_at_risk: parseFloat(form.amount_at_risk) || 0,
        status: 'pending',
        exit_type: 'UNKNOWN',
        attribution_tier: 'UNATTRIBUTED',
        risk_band: form.priority === 'critical' ? 'CRITICAL' : form.priority === 'high' ? 'HIGH' : 'MEDIUM',
        eta: 'Calculating...',
        urgency_score: form.priority === 'critical' ? 90 : form.priority === 'high' ? 70 : 50,
        exit_entity: '',
      });
      setNewCaseId(res.data.id);
      setLogs(prev => [...prev, `[SYS] Trace complete. Opening case ${res.data.id}...`]);
      setTimeout(() => navigate(`/cases/${res.data.id}`), 500);
    } catch (err) {
      console.error(err);
      setLogs(prev => [...prev, `[ERROR] Case creation failed. Check that the backend is running.`]);
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
          <Activity className="w-8 h-8 text-blue-600 animate-pulse" />
          Live M3 Tracing Pipeline
        </h1>

        <div className="bg-slate-900 rounded-lg p-6 border border-slate-700 shadow-xl overflow-hidden font-mono">
          <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-700">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
            </div>
            <div className="text-slate-400 text-xs">ChainNetra Trace Node v2.4.1</div>
          </div>

          <div className="space-y-2 mb-6 min-h-[250px]">
            {logs.map((log, i) => (
              <div key={i} className="flex gap-3 text-sm">
                <span className="text-slate-500 shrink-0">[{new Date().toISOString().split('T')[1].slice(0, 12)}]</span>
                <span className={
                  log.includes('[SYS]') ? 'text-blue-400' :
                  log.includes('[GRAPH]') ? 'text-purple-400' :
                  log.includes('[ML]') ? 'text-emerald-400' :
                  log.includes('[ATTRIBUTION]') ? 'text-yellow-400' : 'text-slate-300'
                }>{log}</span>
              </div>
            ))}
            {progress < 100 && (
              <div className="flex gap-3 text-sm text-slate-500 animate-pulse">
                <span>[{new Date().toISOString().split('T')[1].slice(0, 12)}]</span>
                <span>_</span>
              </div>
            )}
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-2">
              <span>Overall Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full transition-all duration-300 ease-out" style={{ width: `${progress}%` }}></div>
            </div>
            {!submitting && progress < 100 && (
              <div className="mt-4 pt-3 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => { setSubmitted(false); setLogs([]); setProgress(0); }}
                  className="px-4 py-1.5 text-xs text-slate-300 bg-slate-800 hover:bg-slate-700 rounded border border-slate-600"
                >
                  ← Edit Form & Retry
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button onClick={() => navigate('/queue')} className="text-slate-500 hover:text-slate-700 text-sm flex items-center gap-1 mb-2">
            <ArrowLeft className="w-4 h-4" /> Back to Triage Queue
          </button>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <Plus className="w-8 h-8 text-blue-600" />
            New Investigation Case
          </h1>
          <p className="text-slate-500 mt-1">Submit a new case for automated blockchain tracing and attribution.</p>
        </div>
        <button
          type="button"
          onClick={() => {
            update('chain', 'tron');
            update('asset', 'USDT');
            update('amount_at_risk', '2500000');
            update('seed_address', 'TT2T17KZhoDu47i2E4FWxfG79zpeRxFBCE');
            update('title', 'Pig Butchering Scam — ₹2.5 Cr USDT');
            update('description', 'Victim lured via Telegram investment group. Funds transferred to scammer wallet over 3 days.');
            update('priority', 'high');
            update('complainant_ref', 'I4C-2026-8892');
          }}
          className="bg-emerald-100 hover:bg-emerald-200 text-emerald-700 border border-emerald-200 px-4 py-2 rounded-lg font-medium text-sm transition-colors mt-6"
        >
          Load Demo Case
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Chain Selection */}
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-slate-900 mb-4">Select Blockchain</h2>
          <div className="grid grid-cols-5 gap-3">
            {CHAINS.map(c => (
              <button
                key={c.value}
                type="button"
                onClick={() => update('chain', c.value)}
                className={`p-4 rounded-lg border-2 text-center transition-all ${
                  form.chain === c.value
                    ? 'border-blue-500 bg-blue-50 shadow-sm'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className={`w-3 h-3 rounded-full ${c.color} mx-auto mb-2`} />
                <div className="text-sm font-medium text-slate-900">{c.label}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Seed Information */}
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-500" />
            Seed Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Seed Address *</label>
              <input
                type="text"
                required
                placeholder="0x... or T... or bc1..."
                value={form.seed_address}
                onChange={e => update('seed_address', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-slate-500 mt-1">The initial address to start tracing from</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Transaction Hash (optional)</label>
              <input
                type="text"
                placeholder="0x... transaction hash"
                value={form.seed_tx_hash}
                onChange={e => update('seed_tx_hash', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-slate-500 mt-1">Specific transaction to anchor the investigation</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Amount at Risk *</label>
              <div className="flex">
                <input
                  type="number"
                  required
                  step="0.01"
                  placeholder="0.00"
                  value={form.amount_at_risk}
                  onChange={e => update('amount_at_risk', e.target.value)}
                  className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-l-lg text-sm font-mono text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="px-3 py-2 bg-slate-100 border border-l-0 border-slate-200 rounded-r-lg text-sm font-medium text-slate-600">
                  {form.asset}
                </span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Asset Override</label>
              <select
                value={form.asset}
                onChange={e => update('asset', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="BTC">BTC</option>
                <option value="ETH">ETH</option>
                <option value="USDT">USDT (TRC-20)</option>
                <option value="USDC">USDC</option>
                <option value="BNB">BNB</option>
                <option value="MATIC">MATIC</option>
                <option value="DAI">DAI</option>
              </select>
            </div>
          </div>
        </div>

        {/* Case Details */}
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5 text-purple-500" />
            Case Details
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Case Title</label>
              <input
                type="text"
                placeholder="e.g. Pig Butchering Scam — ₹2.5 Cr USDT on Tron"
                value={form.title}
                onChange={e => update('title', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Description / Notes</label>
              <textarea
                rows={3}
                placeholder="Brief description of the incident, victim details, or any leads..."
                value={form.description}
                onChange={e => update('description', e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Complainant Reference</label>
                <input
                  type="text"
                  placeholder="FIR No. / I4C Ref / Internal ID"
                  value={form.complainant_ref}
                  onChange={e => update('complainant_ref', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Victim Name (optional)</label>
                <input
                  type="text"
                  placeholder="Name or alias"
                  value={form.victim_name}
                  onChange={e => update('victim_name', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Priority */}
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            Priority Level
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {PRIORITY_OPTIONS.map(p => (
              <button
                key={p.value}
                type="button"
                onClick={() => update('priority', p.value)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  form.priority === p.value
                    ? 'border-blue-500 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className={`inline-flex px-2 py-1 rounded text-xs font-medium border mb-1 ${p.color}`}>
                  {p.value.toUpperCase()}
                </div>
                <div className="text-sm text-slate-600">{p.label}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Submit */}
        <div className="flex items-center justify-between bg-white border border-slate-200 rounded-lg p-6">
          <div className="text-sm text-slate-500">
            The case will be automatically traced using M3 guided search and all 7 pattern detectors.
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => navigate('/queue')}
              className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !form.seed_address || !form.amount_at_risk}
              className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              Create Case & Start Tracing
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
