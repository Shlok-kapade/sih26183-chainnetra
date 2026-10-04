import React, { useState, useEffect } from 'react';
import { ShieldAlert, FileUp, Filter, ChevronDown, ChevronRight, Clock, Activity, Coins, Loader2, TrendingUp, AlertOctagon, Network } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getCases } from '../lib/api';

const MOCK_CASES = [
  {
    id: 'CASE-7281',
    chain: 'bitcoin',
    amount: 45.5,
    asset: 'BTC',
    exit_type: 'VASP',
    tier: 'CONFIRMED',
    risk_band: 'CRITICAL',
    eta: '2.5 hrs',
    freshness: '15 mins',
    status: 'pending',
    urgency_score: 95,
    urgency_factors: ["High value transfer (+40 pts)", "Rapid peel chain pattern (+25 pts)", "Time since incident < 24h (+20 pts)"],
    timeline: {"Reported": "Today, 10:45 AM", "First Hop": "Today, 11:02 AM", "Last Seen": "Today, 12:15 PM"},
    ml_signals: {"exchange": 0.94, "mixer": 0.02, "service": 0.04}
  },
  {
    id: 'CASE-7282',
    chain: 'ethereum',
    amount: 1200.0,
    asset: 'ETH',
    exit_type: 'MIXER',
    tier: 'PROBABLE',
    risk_band: 'HIGH',
    eta: 'Unknown',
    freshness: '4 hrs',
    status: 'running',
    urgency_score: 88,
    urgency_factors: ["High value transfer (+40 pts)", "Known mixer interaction (+25 pts)"],
    timeline: {"Reported": "Today, 14:20 PM", "First Hop": "Today, 14:35 PM", "Last Seen": "Ongoing"},
    ml_signals: {"exchange": 0.12, "mixer": 0.85, "service": 0.03}
  }
];

const TierBadge = ({ tier }: { tier: string }) => {
  const colors: Record<string, string> = {
    CONFIRMED: 'bg-red-500/10 text-red-500 border-red-500/20',
    PROBABLE: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
    POSSIBLE: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    UNATTRIBUTED: 'bg-slate-500/10 text-slate-600 border-slate-500/20'
  };
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium border ${colors[tier] || colors.UNATTRIBUTED}`}>
      {tier}
    </span>
  );
};

const RiskBadge = ({ band }: { band: string }) => {
  const colors: Record<string, string> = {
    CRITICAL: 'text-red-500',
    HIGH: 'text-orange-500',
    MEDIUM: 'text-yellow-500',
    LOW: 'text-emerald-500'
  };
  return (
    <span className={`font-bold text-sm ${colors[band] || 'text-slate-600'}`}>
      {band}
    </span>
  );
};

export function TriageQueue() {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await getCases();
      if (data && data.length > 0) {
        // Map backend case structure if needed, or just use directly
        // For now, if we get real data, use it. If not, use mock.
        setCases(data.map((c: any) => ({
          id: c.id,
          chain: c.chain || 'unknown',
          amount: c.amount_at_risk || 0,
          asset: c.asset || 'USD',
          exit_type: c.exit_type || 'UNKNOWN',
          tier: c.attribution_tier || 'UNATTRIBUTED',
          risk_band: c.risk_band || 'MEDIUM',
          eta: c.eta || 'Unknown',
          freshness: 'Just now',
          status: c.status || 'pending',
          urgency_score: c.urgency_score || 0,
          urgency_factors: c.urgency_factors || [],
          timeline: c.timeline || {},
          ml_signals: c.ml_signals || {}
        })));
      } else {
        setCases(MOCK_CASES);
      }
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ShieldAlert className="text-red-500 w-8 h-8" />
            Triage Queue
          </h1>
          <p className="text-slate-600 mt-1">
            Cases prioritized by time-to-cashout, amount at risk, and heuristic evidence.
          </p>
        </div>

        <div className="flex gap-3">
          <Link to="/cases/new" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors">
            + New Case
          </Link>
          <button className="bg-slate-100 hover:bg-slate-200 text-slate-900 px-4 py-2 rounded-md font-medium flex items-center gap-2 border border-slate-300 transition-colors">
            <FileUp className="w-4 h-4" />
            Bulk Import CSV
          </button>
        </div>
      </div>


      {/* Global Threat Radar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-5 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-red-500/10 rounded-full blur-xl group-hover:bg-red-500/20 transition-all"></div>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-slate-400 font-medium flex items-center gap-2"><AlertOctagon className="w-4 h-4" /> Active Threats</h3>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20">LIVE</span>
          </div>
          <div className="text-3xl font-bold text-white">24</div>
          <div className="text-sm text-slate-500 mt-2">↑ 3 new in last hour</div>
        </div>

        <div className="bg-slate-900 border border-slate-700 rounded-lg p-5 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 rounded-full blur-xl group-hover:bg-blue-500/20 transition-all"></div>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-slate-400 font-medium flex items-center gap-2"><Coins className="w-4 h-4" /> Value at Risk (24h)</h3>
          </div>
          <div className="text-3xl font-bold text-white">$14.2M</div>
          <div className="text-sm text-slate-500 mt-2 flex items-center gap-1"><TrendingUp className="w-3 h-3 text-red-400" /> <span className="text-red-400">+12%</span> vs yesterday</div>
        </div>

        <div className="bg-slate-900 border border-slate-700 rounded-lg p-5 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-purple-500/10 rounded-full blur-xl group-hover:bg-purple-500/20 transition-all"></div>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-slate-400 font-medium flex items-center gap-2"><Network className="w-4 h-4" /> Top Exit Nodes</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-300">Binance Hot Wallet</span>
              <span className="text-white font-mono">45%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5">
              <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: '45%' }}></div>
            </div>
            <div className="flex justify-between text-sm mt-1">
              <span className="text-slate-300">Tornado Cash</span>
              <span className="text-white font-mono">22%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5">
              <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: '22%' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white border border-slate-200 p-3 rounded-lg flex items-center gap-4">
        <Filter className="w-4 h-4 text-slate-600 ml-2" />
        <select className="bg-slate-50 border border-slate-200 text-sm rounded px-3 py-1.5 text-slate-800 outline-none focus:border-blue-500">
          <option>All Chains</option>
          <option>Tron</option>
          <option>Ethereum</option>
          <option>Bitcoin</option>
        </select>
        <select className="bg-slate-50 border border-slate-200 text-sm rounded px-3 py-1.5 text-slate-800 outline-none focus:border-blue-500">
          <option>All Risk Bands</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
        </select>
        <select className="bg-slate-50 border border-slate-200 text-sm rounded px-3 py-1.5 text-slate-800 outline-none focus:border-blue-500">
          <option>All Statuses</option>
          <option>Pending</option>
          <option>Running</option>
          <option>Completed</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden relative min-h-[300px]">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-white/50 z-10 backdrop-blur-sm">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : null}
        <table className="w-full text-left text-sm text-slate-800">
          <thead className="bg-slate-50 text-slate-600 uppercase text-xs font-semibold">
            <tr>
              <th className="px-4 py-3"></th>
              <th className="px-4 py-3">Reference</th>
              <th className="px-4 py-3">Amount at Risk</th>
              <th className="px-4 py-3">Exit / Tier</th>
              <th className="px-4 py-3">Risk Band</th>
              <th className="px-4 py-3">ETA to Cashout</th>
              <th className="px-4 py-3">Freshness</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {cases.map(c => (
              <React.Fragment key={c.id}>
                <tr className="hover:bg-slate-100/50 transition-colors group">
                  <td className="px-4 py-3 w-10">
                    <button
                      onClick={() => setExpandedRow(expandedRow === c.id ? null : c.id)}
                      className="text-slate-500 hover:text-slate-800"
                    >
                      {expandedRow === c.id ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>
                  </td>
                  <td className="px-4 py-3 font-medium">
                    <Link to={`/cases/${c.id}`} className="text-blue-400 hover:underline">
                      {c.id}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-mono text-slate-900">{Number(c.amount).toLocaleString()} {c.asset}</div>
                    <div className="text-xs text-slate-500 capitalize">{c.chain}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-900 mb-1">{c.exit_type}</div>
                    <TierBadge tier={c.tier} />
                  </td>
                  <td className="px-4 py-3"><RiskBadge band={c.risk_band} /></td>
                  <td className="px-4 py-3 text-red-400 font-medium">{c.eta}</td>
                  <td className="px-4 py-3">{c.freshness}</td>
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${c.status === 'completed' ? 'bg-emerald-500' : c.status === 'running' ? 'bg-blue-500 animate-pulse' : 'bg-slate-500'}`}></span>
                      <span className="capitalize">{c.status}</span>
                    </span>
                  </td>
                </tr>
                {expandedRow === c.id && (
                  <tr className="bg-slate-50/50">
                    <td colSpan={8} className="px-12 py-4 border-l-2 border-l-red-500">
                      <div className="grid grid-cols-3 gap-6 text-sm">
                        <div>
                          <div className="text-slate-600 font-medium mb-2 flex items-center gap-2"><Activity className="w-4 h-4"/> Urgency Factors</div>
                          <ul className="space-y-1 text-slate-800">
                            {c.urgency_factors && c.urgency_factors.length > 0 ? (
                              c.urgency_factors.map((factor: string, idx: number) => (
                                <li key={idx}>• {factor}</li>
                              ))
                            ) : (
                              <li className="text-slate-400 italic">No urgency factors identified.</li>
                            )}
                          </ul>
                        </div>
                        <div>
                          <div className="text-slate-600 font-medium mb-2 flex items-center gap-2"><Clock className="w-4 h-4"/> Timeline</div>
                          <ul className="space-y-1 text-slate-800">
                            {c.timeline && Object.keys(c.timeline).length > 0 ? (
                              Object.entries(c.timeline).map(([key, value]) => (
                                <li key={key}>{key}: {value as React.ReactNode}</li>
                              ))
                            ) : (
                              <li className="text-slate-400 italic">Timeline unavailable.</li>
                            )}
                          </ul>
                        </div>
                        <div>
                           <div className="text-slate-600 font-medium mb-2 flex items-center gap-2"><Coins className="w-4 h-4"/> M1 ML Signals</div>
                           <div className="bg-white rounded p-2 text-xs border border-slate-200">
                              {c.ml_signals && Object.keys(c.ml_signals).length > 0 ? (
                                Object.entries(c.ml_signals).map(([key, value]) => (
                                  <div key={key}>p({key}) = {Number(value).toFixed(2)}</div>
                                ))
                              ) : (
                                <div className="text-slate-400 italic">No signals generated yet.</div>
                              )}
                           </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
import { Link2 } from 'lucide-react';

const explorer = (a?: string) =>
  a && a.startsWith('0x') ? `https://etherscan.io/address/${a}` : `https://tronscan.org/#/address/${a || ''}`;

function Addr({ a }: { a?: string }) {
  if (!a) return <span className="font-mono text-xs text-slate-400">N/A</span>;
  return (
    <a href={explorer(a)} target="_blank" rel="noopener noreferrer"
       className="font-mono text-xs text-blue-700 hover:underline break-all">{a}</a>
  );
}

function Tag({ info }: { info?: any }) {
  if (!info || (!info.label && (!info.tier || info.tier === 'UNATTRIBUTED'))) return null;
  return (
    <div className="mt-0.5">
      <span className="px-1.5 py-0.5 rounded bg-red-100 text-red-700 font-semibold">
        {info.label || info.kind} · {info.tier}
      </span>
    </div>
  );
}

function Tx({ h }: { h: string }) {
  const url = h.startsWith('0x') ? `https://etherscan.io/tx/${h}` : `https://tronscan.org/#/transaction/${h}`;
  return (
    <div><a href={url} target="_blank" rel="noopener noreferrer"
            className="font-mono text-blue-700 hover:underline break-all">{h}</a></div>
  );
}

const tierColor: Record<string, string> = {
  CONFIRMED: 'bg-red-100 text-red-700', PROBABLE: 'bg-orange-100 text-orange-700',
  POSSIBLE: 'bg-yellow-100 text-yellow-800', UNATTRIBUTED: 'bg-slate-100 text-slate-600',
};

