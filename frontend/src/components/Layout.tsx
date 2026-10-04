import { Outlet, Link, useLocation } from 'react-router-dom';
import { Shield, List, Activity, Settings, Database, BarChart3 } from 'lucide-react';

export function Layout() {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: BarChart3 },
    { name: 'Triage Queue', path: '/queue', icon: List, badge: '2' },
    { name: 'Model Center', path: '/models', icon: Activity },
    { name: 'Label Explorer', path: '/labels', icon: Database },
    { name: 'Admin', path: '/admin', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <div className="w-64 border-r border-slate-200 bg-white flex flex-col">
        <div className="p-4 border-b border-slate-200 flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <Shield className="text-blue-600 w-6 h-6" />
            <span className="font-bold text-xl text-slate-900 tracking-tight">ChainNetra</span>
          </div>
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider ml-8">Blockchain Forensics Platform</span>
        </div>

        <div className="flex-1 overflow-y-auto py-6">
          <nav className="space-y-1.5 px-3">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border-l-4 border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                    {item.name}
                  </div>
                  {item.badge && (
                    <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-slate-200 bg-slate-50/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
              IN
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-slate-900">Investigator</span>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                <span className="text-xs text-slate-500 font-medium">LIVE MODE</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
