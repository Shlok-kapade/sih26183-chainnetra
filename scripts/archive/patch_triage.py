import re

with open("frontend/src/pages/TriageQueue.tsx", "r") as f:
    content = f.read()

# Replace imports
import_replacement = "import { ShieldAlert, FileUp, Filter, ChevronDown, ChevronRight, Clock, Activity, Coins, Loader2, TrendingUp, AlertOctagon, Network } from 'lucide-react';"
content = re.sub(r"import { ShieldAlert.* } from 'lucide-react';", import_replacement, content)

# Add threat radar
threat_radar = """
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
"""

content = content.replace("      {/* Filters Bar */}", threat_radar + "\n      {/* Filters Bar */}")

with open("frontend/src/pages/TriageQueue.tsx", "w") as f:
    f.write(content)
