import { useState } from 'react';
import { FileText, Download, Database, CheckCircle2, ShieldAlert, Loader2 } from 'lucide-react';
import api from '../../lib/api';

export function EvidenceTab({ caseData }: { caseData: any }) {
  const [generating, setGenerating] = useState(false);


  const generateSubpoena = async () => {
    if (!caseData) return;
    try {
      const res = await api.get(`/cases/${caseData.id}/subpoena`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `SUBPOENA_DATA_${caseData.id}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error(err);
      alert('Failed to generate subpoena');
    }
  };

  const generateFreezeRequest = async () => {
    if (!caseData) return;
    try {
      setGenerating(true);
      const res = await api.get(`/cases/${caseData.id}/freeze_request.pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `FREEZE_REQUEST_${caseData.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Failed to generate freeze request PDF');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="h-full flex flex-col p-6 overflow-y-auto">
      <div className="flex justify-between items-end mb-6">
        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <FileText className="w-5 h-5 text-emerald-400" />
          Evidence Locker & Actions
        </h2>
        
        <button 
          onClick={generateFreezeRequest}
          disabled={generating || !caseData}
          className="bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-3 py-1.5 rounded text-sm font-medium transition-colors flex items-center gap-2"
        >
          {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4" />}
          Generate VASP Freeze Request
        </button>
      </div>
      
      <div className="space-y-4">
        {/* Evidence Item 1 */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex items-start justify-between group hover:border-slate-300 transition-colors">
          <div className="flex gap-4">
            <div className="bg-emerald-500/10 p-3 rounded-lg h-fit">
              <Database className="w-6 h-6 text-emerald-500" />
            </div>
            <div>
              <h3 className="text-slate-900 font-semibold mb-1 flex items-center gap-2">
                Deposit Funnel Resolution <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              </h3>
              <p className="text-sm text-slate-600 mb-2">
                Address resolved to {caseData?.exit_entity || 'Exchange Hot Wallet'} via DAR (Deposit Address Reuse) clustering.
              </p>
              <div className="text-xs font-mono text-slate-500">
                Rule ID: DAR_80_TAU_24H | Confidence: 95%
              </div>
            </div>
          </div>
          <button onClick={generateSubpoena} className="text-slate-600 hover:text-blue-400 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Download className="w-5 h-5" />
          </button>
        </div>

        {/* Evidence Item 2 */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex items-start justify-between group hover:border-slate-300 transition-colors">
          <div className="flex gap-4">
            <div className="bg-blue-500/10 p-3 rounded-lg h-fit">
              <FileText className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h3 className="text-slate-900 font-semibold mb-1 flex items-center gap-2">
                Subpoena Data Package
              </h3>
              <p className="text-sm text-slate-600 mb-2">
                Pre-formatted CSV of relevant transaction hashes and exit nodes for law enforcement sharing.
              </p>
              <div className="text-xs font-mono text-slate-500">
                Generated: Today | Format: LEA-STANDARD-V2
              </div>
            </div>
          </div>
          <button onClick={generateSubpoena} className="text-slate-600 hover:text-blue-400 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
