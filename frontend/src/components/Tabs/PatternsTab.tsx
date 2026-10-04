import { Share2, GitBranch, GitMerge, FastForward, Shuffle, AlertCircle, Activity } from 'lucide-react';

const PATTERN_ICONS: Record<string, any> = {
  'Peel Chain': GitBranch,
  'Fan-Out': GitMerge,
  'Fan-In': GitMerge,
  'Rapid Forward': FastForward,
  'High-Velocity Hopping': FastForward,
  'Mixer Interaction': Shuffle,
};

const CONFIDENCE_STYLE: Record<string, { badge: string; bar: string; border: string }> = {
  CRITICAL:     { badge: 'bg-red-100 text-red-700 border-red-200',    bar: 'bg-red-500',    border: 'border-l-red-500' },
  HIGH:         { badge: 'bg-orange-100 text-orange-700 border-orange-200', bar: 'bg-orange-500', border: 'border-l-orange-500' },
  MEDIUM:       { badge: 'bg-yellow-100 text-yellow-700 border-yellow-200', bar: 'bg-yellow-500', border: 'border-l-yellow-500' },
  LOW:          { badge: 'bg-slate-100 text-slate-600 border-slate-200',    bar: 'bg-slate-400',  border: 'border-l-slate-400' },
  CONFIRMED:    { badge: 'bg-blue-100 text-blue-700 border-blue-200',   bar: 'bg-blue-500',   border: 'border-l-blue-500' },
  UNATTRIBUTED: { badge: 'bg-slate-100 text-slate-500 border-slate-200',    bar: 'bg-slate-300',  border: 'border-l-slate-300' },
};

function scoreToLabel(score: number): string {
  if (score >= 0.9) return 'CRITICAL';
  if (score >= 0.75) return 'HIGH';
  if (score >= 0.5)  return 'MEDIUM';
  return 'LOW';
}

function PatternCard({ p }: { p: any }) {
  const name: string = p.pattern || 'Unknown';
  const score: number = parseFloat(p.score ?? 0);
  const label = scoreToLabel(score);
  const style = CONFIDENCE_STYLE[label] || CONFIDENCE_STYLE.LOW;
  const Icon = PATTERN_ICONS[name] || AlertCircle;
  const txRefs: string[] = (p.evidence_tx_refs || []).slice(0, 5);
  const chain = txRefs[0]?.startsWith('0x') ? 'eth' : 'tron';

  return (
    <div className={`bg-slate-50 border border-slate-200 rounded-lg p-5 border-l-4 ${style.border} hover:shadow-md transition-shadow`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Icon className="w-4 h-4" />
          {name}
        </h3>
        <span className={`px-2 py-0.5 border rounded text-xs font-bold ${style.badge}`}>
          {label}
        </span>
      </div>

      {p.false_positive_note && (
        <p className="text-sm text-slate-600 mb-3">{p.false_positive_note}</p>
      )}

      <div className="bg-white border border-slate-200 rounded p-3 text-xs font-mono text-slate-800 space-y-1 mb-3">
        <div>Instances: {p.instances ?? 1}</div>
        <div>Score: {score.toFixed(3)}</div>
        {/* Score bar */}
        <div className="flex items-center gap-2 mt-1">
          <div className="flex-1 bg-slate-100 rounded-full h-1.5">
            <div className={`h-1.5 rounded-full ${style.bar}`} style={{ width: `${Math.min(score * 100, 100)}%` }} />
          </div>
          <span className="text-slate-500 w-8 text-right">{(score * 100).toFixed(0)}%</span>
        </div>
      </div>

      {txRefs.length > 0 && (
        <div className="text-xs text-slate-500 space-y-0.5">
          <div className="font-semibold text-slate-600 mb-1">Evidence tx refs:</div>
          {txRefs.map(tx => {
            const url = chain === 'eth'
              ? `https://etherscan.io/tx/${tx}`
              : `https://tronscan.org/#/transaction/${tx}`;
            return (
              <a key={tx} href={url} target="_blank" rel="noopener noreferrer"
                 className="block font-mono text-blue-600 hover:underline break-all">
                {tx.length > 20 ? `${tx.slice(0, 20)}…${tx.slice(-8)}` : tx}
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function PatternsTab({ caseData }: { caseData: any }) {
  const ts = caseData?.trace_summary;
  const patterns: any[] = ts?.patterns || [];
  const fanOuts: any[] = ts?.fan_outs || [];
  const fanIns: any[] = ts?.fan_ins || [];

  const hasRealData = ts && ts.stats;

  // If we have a live trace but zero patterns, show explicit "none detected"
  if (hasRealData && patterns.length === 0 && fanOuts.length === 0 && fanIns.length === 0) {
    return (
      <div className="h-full flex flex-col p-6 overflow-y-auto">
        <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
          <Share2 className="w-5 h-5 text-purple-600" />
          Detected Patterns &amp; M3 Heuristics
        </h2>
        <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 rounded-lg p-5 text-sm text-slate-600">
          <AlertCircle className="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-slate-900 mb-1">No patterns detected in this trace.</p>
            <p>The trace has {ts.stats?.edges ?? 0} edge(s) and {ts.stats?.transfers ?? 0} transfer(s). Pattern detectors require more hops to fire (peel chain needs ≥3 hops, fan-out needs ≥3 recipients, etc.).</p>
            {(ts.notes || []).map((n: string, i: number) => (
              <div key={i} className="mt-1 text-orange-600">⚠ {n}</div>
            ))}
          </div>
        </div>

        <div className="mt-6 bg-slate-100 border border-slate-200 rounded-lg p-4 flex items-start gap-3">
          <Activity className="w-5 h-5 text-indigo-500 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-slate-900">M3 Pipeline Result</h4>
            <p className="text-sm text-slate-600 mt-1">
              ChainNetra's M3 pipeline found no pattern matches. Urgency Score: <strong className="text-indigo-600">{caseData?.urgency_score ?? '—'}</strong>.
              {caseData?.exit_type === 'SANCTIONED' || caseData?.attribution_tier === 'CONFIRMED'
                ? ' Note: OFAC-sanctioned destination was confirmed — this is itself a critical indicator regardless of pattern count.'
                : ''}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6 overflow-y-auto">
      <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
        <Share2 className="w-5 h-5 text-purple-600" />
        Detected Patterns &amp; M3 Heuristics
        {hasRealData && (
          <span className="ml-2 text-xs text-slate-400 font-normal">
            from live trace · {patterns.length} pattern(s)
          </span>
        )}
      </h2>

      {patterns.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {patterns.map((p, i) => <PatternCard key={i} p={p} />)}
        </div>
      ) : (
        <div className="text-sm text-slate-500 mb-6">No pattern engine results available for this case.</div>
      )}

      {/* Fan-out summary if patterns array is empty but fan_outs exist */}
      {fanOuts.length > 0 && !patterns.some(p => p.pattern === 'Fan-Out') && (
        <div className="mt-4">
          <PatternCard p={{
            pattern: 'Fan-Out',
            score: 0.8,
            instances: fanOuts.length,
            false_positive_note: `${fanOuts.length} address(es) sent to ≥3 recipients. Largest: ${fanOuts[0]?.split_count} recipients from ${fanOuts[0]?.address?.slice(0, 10)}…`,
            evidence_tx_refs: fanOuts[0]?.targets?.slice(0, 3).map((t: any) => t.first_tx).filter(Boolean) || [],
          }} />
        </div>
      )}

      {fanIns.length > 0 && !patterns.some(p => p.pattern === 'Fan-In') && (
        <div className="mt-4">
          <PatternCard p={{
            pattern: 'Fan-In',
            score: 0.75,
            instances: fanIns.length,
            false_positive_note: `${fanIns.length} consolidation point(s). Largest: ${fanIns[0]?.merge_count} senders into ${fanIns[0]?.address?.slice(0, 10)}…`,
            evidence_tx_refs: fanIns[0]?.sources?.slice(0, 3).map((t: any) => t.first_tx).filter(Boolean) || [],
          }} />
        </div>
      )}

      <div className="mt-8 bg-slate-100 border border-slate-200 rounded-lg p-4 flex items-start gap-3">
        <Activity className="w-5 h-5 text-indigo-500 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-bold text-slate-900">M3 Pipeline Evaluation</h4>
          <p className="text-sm text-slate-600 mt-1">
            ChainNetra's M3 pipeline applies pattern detectors and heuristics against extracted topological features.
            Urgency Score: <strong className="text-indigo-600">{caseData?.urgency_score ?? '—'}</strong>.
            {hasRealData && ts.stats && (
              <> Analysed {ts.stats.nodes} address(es), {ts.stats.edges} edge(s), {ts.stats.transfers} transfer(s) in {ts.stats.elapsed_s}s.</>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
