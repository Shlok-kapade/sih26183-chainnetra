import { Settings, Key, Users, Database, Activity, CheckCircle2, AlertCircle } from 'lucide-react';

export function AdminDashboard() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto p-2">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2 text-slate-900">
          <Settings className="text-slate-600 w-8 h-8" />
          Admin Dashboard
        </h1>
        <p className="text-slate-600 mt-1">
          System health, API integrations, and organization settings.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health Column */}
        <div className="space-y-6 lg:col-span-2">
          
          {/* Status Panel */}
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-blue-400" />
              System Status
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-50 p-4 rounded border border-slate-200">
                <div className="text-sm text-slate-500 mb-1">Celery Workers</div>
                <div className="text-2xl font-mono text-emerald-400 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5" /> 4/4
                </div>
              </div>
              <div className="bg-slate-50 p-4 rounded border border-slate-200">
                <div className="text-sm text-slate-500 mb-1">Redis Queue</div>
                <div className="text-2xl font-mono text-slate-900">12</div>
              </div>
              <div className="bg-slate-50 p-4 rounded border border-slate-200">
                <div className="text-sm text-slate-500 mb-1">Database Load</div>
                <div className="text-2xl font-mono text-slate-900">14%</div>
              </div>
              <div className="bg-slate-50 p-4 rounded border border-slate-200">
                <div className="text-sm text-slate-500 mb-1">API Latency</div>
                <div className="text-2xl font-mono text-slate-900">42ms</div>
              </div>
            </div>
          </div>

          {/* API Integrations */}
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
              <Key className="w-5 h-5 text-yellow-400" />
              API Integrations
            </h2>
            <div className="space-y-3">
              {/* TronGrid */}
              <div className="flex items-center justify-between bg-slate-50 p-3 rounded border border-slate-200">
                <div>
                  <div className="font-medium text-slate-900">TronGrid API</div>
                  <div className="text-xs text-slate-500">Node sync status and RPC health</div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-slate-600 font-mono">18c5f8a5-...</span>
                  <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium rounded uppercase flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Connected
                  </span>
                  <button className="text-blue-400 text-sm hover:underline">Edit</button>
                </div>
              </div>
              {/* Etherscan */}
              <div className="flex items-center justify-between bg-slate-50 p-3 rounded border border-slate-200">
                <div>
                  <div className="font-medium text-slate-900">Etherscan API</div>
                  <div className="text-xs text-slate-500">Ethereum tracing provider</div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-slate-600 font-mono">Not configured</span>
                  <span className="px-2 py-1 bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-medium rounded uppercase flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> Missing
                  </span>
                  <button className="text-blue-400 text-sm hover:underline">Setup</button>
                </div>
              </div>
              {/* Binance CEX API */}
              <div className="flex items-center justify-between bg-slate-50 p-3 rounded border border-slate-200">
                <div>
                  <div className="font-medium text-slate-900">Binance Law Enforcement Portal</div>
                  <div className="text-xs text-slate-500">Subpoena automation endpoint</div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="px-2 py-1 bg-slate-500/10 text-slate-600 border border-slate-500/20 text-xs font-medium rounded uppercase">
                    Disabled
                  </span>
                  <button className="text-blue-400 text-sm hover:underline">Setup</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Storage & Users Column */}
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-purple-400" />
              Storage
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">PostgreSQL (Graph Data)</span>
                  <span className="text-slate-900">4.2 GB / 100 GB</span>
                </div>
                <div className="w-full bg-slate-50 rounded-full h-2 border border-slate-200">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '4.2%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">Label Storage</span>
                  <span className="text-slate-900">128 MB</span>
                </div>
                <div className="w-full bg-slate-50 rounded-full h-2 border border-slate-200">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '2%' }}></div>
                </div>
              </div>
              <button className="w-full mt-2 bg-slate-100 hover:bg-slate-200 text-slate-900 px-3 py-2 rounded text-sm font-medium transition-colors border border-slate-300">
                Run Vacuum / Cleanup
              </button>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
              <Users className="w-5 h-5 text-emerald-400" />
              Access Control
            </h2>
            <div className="space-y-3">
              <div className="bg-slate-50 p-3 rounded border border-slate-200 flex justify-between items-center">
                <div className="text-sm text-slate-800">Active Investigators</div>
                <div className="font-mono text-slate-900">12</div>
              </div>
              <div className="bg-slate-50 p-3 rounded border border-slate-200 flex justify-between items-center">
                <div className="text-sm text-slate-800">Pending Invites</div>
                <div className="font-mono text-slate-900">2</div>
              </div>
              <button className="w-full mt-2 bg-slate-100 hover:bg-slate-200 text-slate-900 px-3 py-2 rounded text-sm font-medium transition-colors border border-slate-300">
                Manage Users
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
