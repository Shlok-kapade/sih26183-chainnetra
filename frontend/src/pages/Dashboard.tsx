import {
  Briefcase,
  Banknote,
  Target,
  Clock,
  Cpu,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Server,
  Network
} from 'lucide-react';

export function Dashboard() {
  const stats = [
    { label: 'Active Cases', value: '2', icon: Briefcase, color: 'text-blue-600', bg: 'bg-blue-100' },
    { label: 'Total Traced', value: '₹47.2 Cr', icon: Banknote, color: 'text-emerald-600', bg: 'bg-emerald-100' },
    { label: 'Attribution Rate', value: '94.7%', icon: Target, color: 'text-indigo-600', bg: 'bg-indigo-100' },
    { label: 'Avg Resolution Time', value: '2.3 hrs', icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
    { label: 'Models Active', value: '3/3', icon: Cpu, color: 'text-purple-600', bg: 'bg-purple-100' },
  ];

  const activities = [
    { time: '10 mins ago', text: 'CASE-7281 escalated to CRITICAL', type: 'alert' },
    { time: '1 hour ago', text: 'M1 model retrained — F1: 0.89 → 0.91', type: 'info' },
    { time: '3 hours ago', text: 'New OFAC SDN labels synced (147 addresses)', type: 'success' },
    { time: '5 hours ago', text: 'CASE-7282 pattern detected: Fan-Out Layering', type: 'warning' },
    { time: '1 day ago', text: 'Freeze request sent to Binance for CASE-7281', type: 'action' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <div className="text-sm text-slate-500 font-medium">
          Last updated: Just now
        </div>
      </div>

      {/* Hero Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <span className="text-slate-500 font-medium text-sm">{stat.label}</span>
                <div className={`p-2 rounded-lg ${stat.bg}`}>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Area - Left 2 Columns */}
        <div className="lg:col-span-2 space-y-6">

          {/* Chain & Risk Distribution */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Chain Distribution */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Network className="w-5 h-5 text-blue-500" />
                Chain Distribution
              </h2>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700">Bitcoin</span>
                    <span className="text-slate-500">45%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div className="bg-orange-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700">Ethereum</span>
                    <span className="text-slate-500">35%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '35%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700">Tron</span>
                    <span className="text-slate-500">20%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: '20%' }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Risk Distribution */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Risk Distribution
              </h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span className="text-sm font-medium text-slate-700">Critical</span>
                  </div>
                  <span className="text-sm font-bold text-slate-900">1</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                    <span className="text-sm font-medium text-slate-700">High</span>
                  </div>
                  <span className="text-sm font-bold text-slate-900">1</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span className="text-sm font-medium text-slate-700">Medium</span>
                  </div>
                  <span className="text-sm font-bold text-slate-900">0</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-sm font-medium text-slate-700">Low</span>
                  </div>
                  <span className="text-sm font-bold text-slate-900">0</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Area - Right Column */}
        <div className="space-y-6">

          {/* Recent Activity Feed */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-500" />
              Recent Activity
            </h2>
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
              {activities.map((activity, idx) => (
                <div key={idx} className="relative flex items-center gap-4">
                  <div className="h-4 w-4 rounded-full bg-slate-200 border-2 border-white z-10 shrink-0">
                    <div className={`h-full w-full rounded-full ${
                      activity.type === 'alert' ? 'bg-red-500' :
                      activity.type === 'success' ? 'bg-emerald-500' :
                      activity.type === 'warning' ? 'bg-amber-500' :
                      activity.type === 'action' ? 'bg-blue-500' : 'bg-slate-400'
                    }`}></div>
                  </div>
                  <div className="flex-1 pb-1">
                    <p className="text-sm text-slate-800 font-medium">{activity.text}</p>
                    <span className="text-xs text-slate-500">{activity.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* System Health */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Server className="w-5 h-5 text-slate-500" />
              System Health
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-sm font-medium text-slate-700">Backend</span>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span className="text-sm font-bold text-emerald-600">OK</span>
                </div>
              </div>
              <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-sm font-medium text-slate-700">ML Pipeline</span>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span className="text-sm font-bold text-emerald-600">OK</span>
                </div>
              </div>
              <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-sm font-medium text-slate-700">Label Store</span>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span className="text-sm font-bold text-emerald-600">OK</span>
                </div>
              </div>
              <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                <span className="text-sm font-medium text-slate-700">API Quota</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-slate-200 rounded-full h-1.5">
                    <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: '12%' }}></div>
                  </div>
                  <span className="text-xs font-bold text-slate-600">12/100</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
