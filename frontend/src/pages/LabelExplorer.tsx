import { Database, Search, Filter, ShieldAlert, Upload, Download } from 'lucide-react';

export function LabelExplorer() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2 text-slate-900">
            <Database className="text-blue-500 w-8 h-8" />
            Label Explorer
          </h1>
          <p className="text-slate-600 mt-1">
            Browse and manage known entities, OFAC SDN lists, and exchange hot wallets.
          </p>
        </div>
        
        <div className="flex gap-3">
          <button className="bg-slate-100 hover:bg-slate-200 text-slate-900 px-4 py-2 rounded-md font-medium border border-slate-300 transition-colors flex items-center gap-2">
            <Upload className="w-4 h-4" /> Import CSV
          </button>
          <button className="bg-slate-100 hover:bg-slate-200 text-slate-900 px-4 py-2 rounded-md font-medium border border-slate-300 transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" /> Export All
          </button>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg p-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search by address, entity name, or tags..." 
              className="w-full bg-slate-50 border border-slate-200 rounded-md pl-10 pr-4 py-2 text-slate-900 outline-none focus:border-blue-500"
            />
          </div>
          <button className="bg-slate-100 border border-slate-300 px-4 py-2 rounded-md text-slate-800 flex items-center gap-2 hover:bg-slate-200">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <table className="w-full text-left text-sm text-slate-800">
          <thead className="bg-slate-50 text-slate-600 uppercase text-xs font-semibold border-b border-slate-200">
            <tr>
              <th className="px-4 py-3">Address</th>
              <th className="px-4 py-3">Entity</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Last Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            <tr className="hover:bg-slate-100/50">
              <td className="px-4 py-3 font-mono text-blue-400">TNVaKWQzau4pirzvwSH17CPvMk4p7yPAn6</td>
              <td className="px-4 py-3 font-medium text-slate-900 flex items-center gap-2">
                Lazarus Group <ShieldAlert className="w-3 h-3 text-red-500" />
              </td>
              <td className="px-4 py-3">
                <span className="px-2 py-1 bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-medium rounded">
                  Sanctioned
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">OFAC SDN</td>
              <td className="px-4 py-3 text-slate-500">2026-01-01</td>
            </tr>
            <tr className="hover:bg-slate-100/50">
              <td className="px-4 py-3 font-mono text-blue-400">TKnABDqoTfRms2BNQDUahFqXiR32vufQi8</td>
              <td className="px-4 py-3 font-medium text-slate-900">Binance</td>
              <td className="px-4 py-3">
                <span className="px-2 py-1 bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 text-xs font-medium rounded">
                  Exchange Hot Wallet
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">Proof of Reserves</td>
              <td className="px-4 py-3 text-slate-500">2026-01-01</td>
            </tr>
            <tr className="hover:bg-slate-100/50">
              <td className="px-4 py-3 font-mono text-blue-400">0x098B716B8Aaf21512996dC57EB0615e2383E2f96</td>
              <td className="px-4 py-3 font-medium text-slate-900 flex items-center gap-2">
                Tornado Cash <ShieldAlert className="w-3 h-3 text-red-500" />
              </td>
              <td className="px-4 py-3">
                <span className="px-2 py-1 bg-violet-500/10 text-violet-400 border border-violet-500/20 text-xs font-medium rounded">
                  Mixer
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">OFAC SDN</td>
              <td className="px-4 py-3 text-slate-500">2026-01-01</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
