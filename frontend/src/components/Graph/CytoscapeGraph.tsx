import { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { Network, Maximize, ZoomIn, ZoomOut, Download, Filter } from 'lucide-react';

interface CytoscapeGraphProps {
  elements: any[];
  onTraceForward?: (address: string) => Promise<string>;
}

export function CytoscapeGraph({ elements, onTraceForward }: CytoscapeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [tracing, setTracing] = useState(false);
  const [traceMsg, setTraceMsg] = useState('');

  useEffect(() => {
    if (!containerRef.current || !elements || elements.length === 0) return;

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-wrap': 'wrap',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 6,
            'color': '#334155',
            'font-size': '12px',
            'width': (ele: any) => Math.max(30, ele.data('taint') ? ele.data('taint') * 60 : 30),
            'height': (ele: any) => Math.max(30, ele.data('taint') ? ele.data('taint') * 60 : 30),
            'background-color': (ele: any) => {
              const role = ele.data('role') || 'intermediary';
              if (role === 'victim') return '#ef4444'; // red-500
              if (role === 'exchange') return '#eab308'; // yellow-500
              if (role === 'mixer' || role === 'bridge') return '#8b5cf6'; // violet-500
              return '#3b82f6'; // blue-500 (intermediary)
            },
            'border-width': 2,
            'border-color': '#e2e8f0'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(amount)',
            'font-size': '10px',
            'color': '#64748b',
            'text-rotation': 'autorotate',
            'text-margin-y': -8
          }
        },
        {
          selector: ':selected',
          style: {
            'border-width': 4,
            'border-color': '#38bdf8', // sky-400
            'line-color': '#38bdf8',
            'target-arrow-color': '#38bdf8'
          }
        }
      ],
      layout: {
        name: 'breadthfirst',
        directed: true,
        padding: 50,
        spacingFactor: 1.5
      }
    });

    cy.on('tap', 'node', (evt) => {
      setSelectedNode(evt.target.data());
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [elements]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit();

  if (!elements || elements.length === 0) {
    return <div className="flex h-full items-center justify-center text-slate-500">No graph data available.</div>;
  }

  return (
    <div className="flex h-full gap-4 relative">
      {/* Graph Area */}
      <div className="flex-1 bg-slate-50 border border-slate-200 rounded-lg relative overflow-hidden flex flex-col">
        {/* Toolbar */}
        <div className="absolute top-4 left-4 z-10 flex gap-2 bg-white/80 p-1 rounded-md border border-slate-200 backdrop-blur-sm">
          <button onClick={handleZoomIn} className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded" title="Zoom In">
            <ZoomIn className="w-4 h-4" />
          </button>
          <button onClick={handleZoomOut} className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded" title="Zoom Out">
            <ZoomOut className="w-4 h-4" />
          </button>
          <button onClick={handleFit} className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded" title="Fit to Screen">
            <Maximize className="w-4 h-4" />
          </button>
          <div className="w-px bg-slate-300 mx-1"></div>
          <button className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded flex items-center gap-1" title="Filters">
            <Filter className="w-4 h-4" />
            <span className="text-xs font-medium px-1">Filter Hops</span>
          </button>
          <button className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded flex items-center gap-1" title="Export">
            <Download className="w-4 h-4" />
          </button>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-10 bg-white/80 p-3 rounded-md border border-slate-200 backdrop-blur-sm text-xs">
          <div className="font-semibold text-slate-800 mb-2">Node Roles</div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500"></div> <span className="text-slate-600">Victim (Origin)</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500"></div> <span className="text-slate-600">Intermediary</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-yellow-500"></div> <span className="text-slate-600">Exchange Deposit</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-violet-500"></div> <span className="text-slate-600">Mixer / Bridge</span></div>
          </div>
        </div>

        <div ref={containerRef} className="w-full h-full" />
      </div>

      {/* Side Drawer (Node Details) */}
      {selectedNode && (
        <div className="w-80 bg-white border border-slate-200 rounded-lg p-4 flex flex-col overflow-y-auto animate-in slide-in-from-right-4 duration-200">
          <div className="mb-6">
            <div className="text-xs text-slate-500 uppercase font-semibold tracking-wider mb-1">Selected Node</div>
            <h3 className="text-lg font-mono font-bold text-slate-900 break-all">
              {selectedNode.id}
            </h3>
            <div className="mt-2 flex gap-2">
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 text-xs font-medium capitalize border border-slate-300">
                {selectedNode.role || 'Unknown'}
              </span>
              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-xs font-medium border border-blue-500/20">
                Taint: {(selectedNode.taint * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="space-y-6">
            {/* Attribution (real, derived from live data) */}
            <div>
              <h4 className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                <Network className="w-4 h-4 text-blue-400" />
                Attribution
              </h4>
              <div className="bg-slate-50 p-2 rounded border border-slate-200 text-sm space-y-1">
                <div className="text-slate-900 font-medium">{selectedNode.label?.replace('\n', ' ')}</div>
                <div className="text-xs text-slate-600">
                  Tier: <strong>{selectedNode.tier || 'UNATTRIBUTED'}</strong> · Type: {selectedNode.kind || 'UNKNOWN'}
                </div>
                {selectedNode.distinct_peers > 0 && (
                  <div className="text-xs text-slate-600">Distinct inbound senders seen: {selectedNode.distinct_peers}</div>
                )}
                {(selectedNode.evidence || []).map((ev: string, i: number) => (
                  <div key={i} className="text-xs text-slate-500">• {ev}</div>
                ))}
                {!(selectedNode.evidence || []).length && (
                  <div className="text-xs text-slate-500 italic">No label or structural evidence for this address.</div>
                )}
              </div>
            </div>


            {/* Actions */}
            <div className="pt-4 border-t border-slate-200">
              <button
                onClick={() => {
                  const addr = selectedNode.full_address || selectedNode.id;
                  const url = String(addr).startsWith('0x')
                    ? `https://etherscan.io/address/${addr}`
                    : `https://tronscan.org/#/address/${addr}`;
                  window.open(url, '_blank', 'noopener');
                }}
                className="w-full bg-slate-100 hover:bg-slate-200 text-slate-900 px-3 py-2 rounded text-sm font-medium transition-colors border border-slate-300 mb-2"
              >
                View in Explorer
              </button>
              <button
                disabled={tracing || !onTraceForward}
                onClick={async () => {
                  if (!onTraceForward) return;
                  setTracing(true);
                  setTraceMsg('');
                  try {
                    setTraceMsg(await onTraceForward(selectedNode.full_address || selectedNode.id));
                  } catch (e: any) {
                    setTraceMsg(e?.response?.data?.detail || 'Trace failed');
                  } finally {
                    setTracing(false);
                  }
                }}
                className="w-full bg-slate-100 hover:bg-slate-200 disabled:opacity-50 text-slate-900 px-3 py-2 rounded text-sm font-medium transition-colors border border-slate-300"
              >
                {tracing ? 'Tracing… (up to 1 min)' : 'Trace Forward from Here'}
              </button>
              {traceMsg && <div className="text-xs text-slate-600 mt-2">{traceMsg}</div>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
