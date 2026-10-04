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

export function TraceDetailsTab({ caseData }: { caseData: any }) {
  const ts = caseData?.trace_summary;
  if (!ts || !ts.stats) {
    return <div className="p-6 text-sm text-slate-500">No live trace data for this case (demo case or trace not run).</div>;
  }
  const exits: any[] = ts.exits || [];
  const fanOuts: any[] = ts.fan_outs || [];
  const fanIns: any[] = ts.fan_ins || [];
  const patterns: any[] = ts.patterns || [];
  const hops: any[] = ts.hops || [];

  return (
    <div className="p-6 overflow-y-auto h-full space-y-8">
      <div className="text-xs text-slate-500">
        Seed: <Addr a={caseData.seed_address} /> · {ts.stats.nodes} addresses, {ts.stats.edges} edges,
        {' '}{ts.stats.transfers} transfers analysed · {ts.stats.expanded} addresses expanded · {ts.stats.elapsed_s}s
        {(ts.notes || []).map((n: string, i: number) => <div key={i} className="text-orange-600">⚠ {n}</div>)}
      </div>

      <section>
        <h3 className="font-semibold text-slate-900 mb-2">Hop-by-hop transfers ({hops.length})</h3>
        {hops.length === 0 && <div className="text-sm text-slate-500">No transfers recorded.</div>}
        {hops.length > 0 && (
          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            <table className="w-full text-xs">
              <thead className="bg-slate-100 text-slate-600">
                <tr>
                  <th className="p-2 text-left">#</th><th className="p-2 text-left">Hop</th>
                  <th className="p-2 text-left">From</th><th className="p-2 text-left">To</th>
                  <th className="p-2 text-right">Amount</th><th className="p-2 text-right">Tx</th>
                  <th className="p-2 text-left">Time (UTC)</th><th className="p-2 text-left">Transaction hash</th>
                </tr>
              </thead>
              <tbody>
                {hops.map((h, i) => (
                  <tr key={i} className="border-t border-slate-100 align-top">
                    <td className="p-2">{i + 1}</td>
                    <td className="p-2">{h.hop}</td>
                    <td className="p-2"><Addr a={h.from} /><Tag info={h.from_info} /></td>
                    <td className="p-2"><Addr a={h.to} /><Tag info={h.to_info} /></td>
                    <td className="p-2 text-right whitespace-nowrap font-medium">{h.amount} {h.asset}</td>
                    <td className="p-2 text-right">{h.tx_count}</td>
                    <td className="p-2 whitespace-nowrap">{h.first_ts}{h.last_ts && h.last_ts !== h.first_ts ? <><br />→ {h.last_ts}</> : null}</td>
                    <td className="p-2">{(h.txs || []).map((t: string) => <Tx key={t} h={t} />)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h3 className="font-semibold text-slate-900 mb-2">Cash-out candidates ({exits.length})</h3>
        {exits.length === 0 && <div className="text-sm text-slate-500">No exit found within the trace depth. Use “Trace Forward from Here” on the last nodes.</div>}
        {exits.map((e, i) => (
          <div key={i} className="border border-slate-200 rounded-lg p-3 mb-3">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${tierColor[e.tier] || ''}`}>{e.tier}</span>
              <span className="text-sm font-medium text-slate-900">{e.entity || 'Unlabelled'} · {e.type}</span>
              <span className="text-xs text-slate-500 ml-auto">{e.received} · {e.hops} hop(s) · taint {(e.taint * 100).toFixed(1)}%</span>
            </div>
            <div className="text-xs text-slate-500">Address: <Addr a={e.address} /></div>
            {e.deposit_address && <div className="text-xs text-slate-500">Deposit / last-hop address: <Addr a={e.deposit_address} /></div>}
            {e.evidence?.map((ev: string, j: number) => <div key={j} className="text-xs text-slate-600">• {ev}</div>)}
            <div className="mt-2 text-xs text-slate-500">Path:</div>
            <div className="flex flex-col gap-0.5 ml-2">
              {e.path.map((p: string, j: number) => (
                <div key={j} className="flex items-center gap-1"><Link2 className="w-3 h-3 text-slate-400" /><Addr a={p} /></div>
              ))}
            </div>
          </div>
        ))}
      </section>

      <section>
        <h3 className="font-semibold text-slate-900 mb-2">Fan-out points ({fanOuts.length})</h3>
        {fanOuts.length === 0 && <div className="text-sm text-slate-500">None detected.</div>}
        {fanOuts.map((f, i) => (
          <div key={i} className="border border-slate-200 rounded-lg p-3 mb-3">
            <div className="text-sm text-slate-900">Splits to <strong>{f.split_count}</strong> addresses from <Addr a={f.address} /></div>
            <table className="w-full text-xs mt-2"><tbody>
              {f.targets.map((t: any, j: number) => (
                <tr key={j} className="border-t border-slate-100"><td className="py-1"><Addr a={t.address} /></td>
                  <td className="text-right whitespace-nowrap pl-2">{t.amount} ({t.tx_count} tx)</td></tr>))}
            </tbody></table>
          </div>
        ))}
      </section>

      <section>
        <h3 className="font-semibold text-slate-900 mb-2">Fan-in (consolidation) points ({fanIns.length})</h3>
        {fanIns.length === 0 && <div className="text-sm text-slate-500">None detected.</div>}
        {fanIns.map((f, i) => (
          <div key={i} className="border border-slate-200 rounded-lg p-3 mb-3">
            <div className="text-sm text-slate-900"><strong>{f.merge_count}</strong> addresses consolidate into <Addr a={f.address} /></div>
            <table className="w-full text-xs mt-2"><tbody>
              {f.sources.map((t: any, j: number) => (
                <tr key={j} className="border-t border-slate-100"><td className="py-1"><Addr a={t.address} /></td>
                  <td className="text-right whitespace-nowrap pl-2">{t.amount} ({t.tx_count} tx)</td></tr>))}
            </tbody></table>
          </div>
        ))}
      </section>

      <section>
        <h3 className="font-semibold text-slate-900 mb-2">Other pattern detections ({patterns.length})</h3>
        {patterns.length === 0 && <div className="text-sm text-slate-500">None.</div>}
        {patterns.map((p, i) => (
          <div key={i} className="border border-slate-200 rounded-lg p-3 mb-2 text-xs">
            <div className="text-sm font-medium text-slate-900">{p.pattern} · {p.instances ?? 1} instance(s) · best score {Number(p.score).toFixed(2)}</div>
            <div className="text-slate-500">{p.false_positive_note}</div>
            <div className="font-mono break-all text-slate-600 mt-1">tx: {(p.evidence_tx_refs || []).slice(0, 3).join(', ')}</div>
          </div>
        ))}
      </section>
    </div>
  );
}
