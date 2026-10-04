import { Beaker, Brain, Cpu, ShieldAlert } from 'lucide-react';

export function ModelCenter() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Brain className="text-purple-500 w-8 h-8" />
          Model Center
        </h1>
        <p className="text-slate-600 mt-1">
          Performance metrics, reliability diagrams, and feature importance for active ML models.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* M1 Model Card */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-blue-400" />
                M1 — Address Role Classifier
              </h2>
              <p className="text-sm text-slate-600">LightGBM (OVR) • v1.4.2</p>
            </div>
            <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium rounded uppercase">
              Active
            </span>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-xs text-slate-500 uppercase font-medium">Macro F1</div>
              <div className="text-xl font-mono text-slate-900 mt-1">0.89</div>
            </div>
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-xs text-slate-500 uppercase font-medium">Precision</div>
              <div className="text-xl font-mono text-slate-900 mt-1">0.92</div>
            </div>
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-xs text-slate-500 uppercase font-medium">Brier Score</div>
              <div className="text-xl font-mono text-slate-900 mt-1">0.08</div>
            </div>
          </div>
          
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-slate-800">Top Features (SHAP)</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">indegree_7d</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 w-[85%]"></div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">balance_mean</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 w-[65%]"></div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">active_days</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 w-[40%]"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* M3 Model Card */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Beaker className="w-5 h-5 text-orange-400" />
                M3 — Guided Tracing Policy
              </h2>
              <p className="text-sm text-slate-600">RandomForestRegressor • v2.1.0</p>
            </div>
            <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium rounded uppercase">
              Active
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-xs text-slate-500 uppercase font-medium">Recall@100</div>
              <div className="text-xl font-mono text-slate-900 mt-1">0.76</div>
            </div>
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-xs text-slate-500 uppercase font-medium">API Saving vs BFS</div>
              <div className="text-xl font-mono text-emerald-400 mt-1">68%</div>
            </div>
          </div>
          
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-slate-800">Top Features (SHAP)</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">amount_share</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-orange-500 w-[90%]"></div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">time_diff</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-orange-500 w-[55%]"></div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">is_contract</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-orange-500 w-[30%]"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* M4 Model Card */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-400" />
                M4 — Anomaly Detector
              </h2>
              <p className="text-sm text-slate-600">IsolationForest • v1.0.0</p>
            </div>
            <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium rounded uppercase">
              Active
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-xs text-slate-500 uppercase font-medium">Contamination Rate</div>
              <div className="text-xl font-mono text-slate-900 mt-1">10%</div>
            </div>
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-xs text-slate-500 uppercase font-medium">Detection AUC-ROC</div>
              <div className="text-xl font-mono text-slate-900 mt-1">0.93</div>
            </div>
          </div>
          
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-slate-800">Top Trace Features (Importance)</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">split_ratio</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 w-[82%]"></div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">revisit_rate</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 w-[70%]"></div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-600 w-32 font-mono">timing_regularity</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 w-[60%]"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
