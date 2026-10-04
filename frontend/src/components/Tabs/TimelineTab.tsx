import { Clock, ArrowRight, ShieldAlert, ArrowDownCircle, Network, AlertTriangle } from 'lucide-react';

const explorer = (a?: string) =>
  a && a.startsWith('0x')
    ? `https://etherscan.io/address/${a}`
    : `https://tronscan.org/#/address/${a || ''}`;

function Addr({ a }: { a?: string }) {
  if (!a) return <span className="font-mono text-xs">{a}</span>;
  return (
    <a href={explorer(a)} target="_blank" rel="noopener noreferrer"
       className="font-mono text-xs text-blue-700 hover:underline break-all">{a}</a>
  );
}

export function TimelineTab({ caseData }: { caseData: any }) {
  const ts = caseData?.trace_summary;
  const hops: any[] = ts?.hops || [];
  const exits: any[] = ts?.exits || [];
  const staticTl: Record<string, string> = caseData?.timeline || {};

  // If we have real hop data, build timeline from it
  if (hops.length > 0) {
    // Group hops by hop depth, sorted by first_ts
    const sorted = [...hops].sort((a, b) => (a.first_ts || '').localeCompare(b.first_ts || ''));

    const events: { time: string; type: string; description: string; from: string; to: string; amount: string; txs: string[] }[] = [];

    // Opening event
    events.push({
      time: sorted[0]?.first_ts || '—',
      type: 'report',
      description: `Trace started from seed address. ${caseData?.amount_at_risk ? `${caseData.amount_at_risk} ${caseData.asset} at risk.` : ''}`,
      from: caseData?.seed_address || '',
      to: '',
      amount: '',
      txs: [],
    });

    // Each unique hop level
    const byDepth: Record<number, any[]> = {};
    for (const h of sorted) {
      const d = h.hop ?? 0;
      if (!byDepth[d]) byDepth[d] = [];
      byDepth[d].push(h);
    }

    for (const depth of Object.keys(byDepth).map(Number).sort()) {
      const group = byDepth[depth];
      const isExit = exits.some(e => group.some(h => h.to === e.address));
      const totalAmt = group.reduce((s: number, h: any) => s + (parseFloat(h.amount?.replace(/,/g, '') || '0') || 0), 0);
      const asset = group[0]?.asset || '';
      events.push({
        time: group[0]?.first_ts || '—',
        type: isExit ? 'exit_vasp' : 'transfer',
        description: group.length > 1
          ? `${group.length} parallel transfers at depth ${depth} · ${totalAmt.toLocaleString(undefined, {maximumFractionDigits: 2})} ${asset} total`
          : `Transfer at depth ${depth} · ${group[0]?.amount} ${asset}`,
        from: group[0]?.from || '',
        to: group.length === 1 ? (group[0]?.to || '') : `${group.length} recipients`,
        amount: `${totalAmt.toLocaleString(undefined, {maximumFractionDigits: 2})} ${asset}`,
        txs: group.flatMap((h: any) => h.txs || []).slice(0, 3),
      });
    }

    // Exit events
    for (const ex of exits) {
      events.push({
        time: '—',
        type: ex.type === 'MIXER' ? 'exit_mixer' : ex.type === 'SANCTIONED' ? 'exit_sanctioned' : 'exit_vasp',
        description: `Cash-out destination confirmed: ${ex.entity || 'Unlabelled'} (${ex.type}, ${ex.tier}) · taint ${(ex.taint * 100).toFixed(0)}%`,
        from: ex.deposit_address || '',
        to: ex.address || '',
        amount: ex.received || '',
        txs: [],
      });
    }

    return (
      <div className="h-full flex flex-col p-6 overflow-y-auto">
        <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-500" />
          Forensic Timeline
          <span className="ml-2 text-xs text-slate-400 font-normal">derived from live trace · {hops.length} transfer edges</span>
        </h2>

        <div className="relative border-l-2 border-slate-300 ml-3 space-y-8">
          {events.map((ev, i) => (
            <div key={i} className="relative pl-6">
              <div className={`absolute -left-2.5 top-1 w-5 h-5 rounded-full border-4 border-white ${
                ev.type === 'report' ? 'bg-slate-400' :
                ev.type === 'exit_vasp' ? 'bg-emerald-500' :
                ev.type === 'exit_mixer' ? 'bg-violet-500' :
                ev.type === 'exit_sanctioned' ? 'bg-red-600' : 'bg-blue-500'
              }`} />
              <div className="text-xs font-bold text-slate-500 mb-1">{ev.time}</div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 shadow-sm">
                <div className="flex items-start gap-3">
                  {ev.type === 'report' ? <ShieldAlert className="w-5 h-5 text-slate-400 mt-0.5 shrink-0" /> :
                   ev.type.startsWith('exit') ? <ArrowDownCircle className={`w-5 h-5 mt-0.5 shrink-0 ${ev.type === 'exit_sanctioned' ? 'text-red-600' : ev.type === 'exit_mixer' ? 'text-violet-500' : 'text-emerald-500'}`} /> :
                   <ArrowRight className="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />}
                  <div className="min-w-0 flex-1">
                    <p className="text-slate-900 font-medium text-sm">{ev.description}</p>
                    {(ev.from || ev.to) && (
                      <div className="mt-2 text-xs text-slate-500 space-y-0.5">
                        {ev.from && <div><span className="font-semibold">From:</span> <Addr a={ev.from} /></div>}
                        {ev.to && typeof ev.to === 'string' && ev.to.length > 5 && <div><span className="font-semibold">To:</span> <Addr a={ev.to} /></div>}
                        {ev.to && (ev.to.length <= 5) && <div><span className="font-semibold">To:</span> {ev.to}</div>}
                      </div>
                    )}
                    {ev.txs.length > 0 && (
                      <div className="mt-1 font-mono text-xs text-slate-400 break-all">
                        {ev.txs.map(tx => {
                          const url = tx.startsWith('0x') ? `https://etherscan.io/tx/${tx}` : `https://tronscan.org/#/transaction/${tx}`;
                          return <a key={tx} href={url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline mr-2">{tx.slice(0, 16)}…</a>;
                        })}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Fallback: use static timeline dict from case (demo cases have this)
  if (Object.keys(staticTl).length > 0) {
    const staticEvents = Object.entries(staticTl);
    return (
      <div className="h-full flex flex-col p-6 overflow-y-auto">
        <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-500" />
          Forensic Timeline
          <span className="ml-2 text-xs text-slate-400 font-normal">from case record</span>
        </h2>
        <div className="relative border-l-2 border-slate-300 ml-3 space-y-8">
          {staticEvents.map(([label, detail], i) => (
            <div key={i} className="relative pl-6">
              <div className="absolute -left-2.5 top-1 w-5 h-5 rounded-full border-4 border-white bg-blue-500" />
              <div className="text-xs font-bold text-slate-500 mb-1">{label}</div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 shadow-sm text-sm text-slate-800">{detail}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // No data at all
  return (
    <div className="h-full flex flex-col p-6 overflow-y-auto">
      <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
        <Clock className="w-5 h-5 text-blue-500" />
        Forensic Timeline
      </h2>
      <div className="flex items-center gap-2 text-slate-500 text-sm">
        <AlertTriangle className="w-4 h-4 text-orange-400" />
        No timeline data available. Run a live trace to generate a real forensic timeline.
      </div>
    </div>
  );
}
