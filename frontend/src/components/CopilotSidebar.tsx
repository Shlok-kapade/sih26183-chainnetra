import { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, Sparkles, FileText, Activity } from 'lucide-react';

export function CopilotSidebar({ isOpen, onClose, caseData }: { isOpen: boolean, onClose: () => void, caseData: any }) {
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([
    { role: 'assistant', content: `Hello! I am your ChainNetra Investigator AI. I've already analyzed **${caseData?.id || 'this case'}**. How can I help you today?` }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = (text: string) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      let response = "Based on the M3 network graph, the funds have been obfuscated through multiple hops.";
      
      if (text.toLowerCase().includes('summarize')) {
        response = `**Executive Summary:**\n- **Target:** ${caseData?.amount_at_risk} ${caseData?.asset} on ${caseData?.chain}\n- **Status:** Traced to ${caseData?.exit_entity} (${caseData?.attribution_tier})\n- **Confidence:** High (M1 ML Score: ${caseData?.urgency_score})\n\n*Recommendation:* Issue an immediate freeze request to the VASP.`;
      } else if (text.toLowerCase().includes('fir') || text.toLowerCase().includes('legal')) {
        response = `**Draft Legal Request (PMLA 2002)**\n\nTo: Nodal Officer, ${caseData?.exit_entity || 'Exchange'}\nSubject: URGENT - Freezing of Assets related to ${caseData?.id}\n\nUnder Section 91 CrPC and PMLA frameworks, you are hereby directed to freeze the wallet address associated with this trace.`;
      } else if (text.toLowerCase().includes('ml') || text.toLowerCase().includes('explain')) {
        response = `**M1 Random Forest Analysis:**\n- **Velocity:** Inter-node dwell time < 4 mins (High anomaly)\n- **Structure:** Fan-out layering detected across 12 nodes.\n- **Taint:** Maintained 92% continuous taint from origin to deposit address.`;
      }

      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
      setIsTyping(false);
    }, 1500);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white border-l border-slate-200 shadow-2xl flex flex-col z-50 transform transition-transform duration-300">
      <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-slate-900 text-white">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-emerald-400" />
          <h2 className="font-bold">ChainNetra Copilot</h2>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none shadow-sm'}`}>
              {msg.role === 'assistant' && (
                <div className="flex items-center gap-1.5 mb-1 text-emerald-600 font-bold text-xs">
                  <Sparkles className="w-3 h-3" /> AI Analysis
                </div>
              )}
              <div className="whitespace-pre-wrap leading-relaxed">
                {msg.content.split('**').map((part, index) => 
                  index % 2 === 1 ? <strong key={index} className="font-bold text-slate-900">{part}</strong> : part
                )}
              </div>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 p-3 rounded-lg rounded-bl-none shadow-sm flex gap-1">
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="p-4 bg-white border-t border-slate-200 space-y-3">
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          <button onClick={() => handleSend("Summarize this case")} className="flex-shrink-0 bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1.5 rounded-full text-xs font-medium hover:bg-blue-100 flex items-center gap-1"><FileText className="w-3 h-3"/> Summarize</button>
          <button onClick={() => handleSend("Explain ML signals")} className="flex-shrink-0 bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1.5 rounded-full text-xs font-medium hover:bg-purple-100 flex items-center gap-1"><Activity className="w-3 h-3"/> Explain ML</button>
          <button onClick={() => handleSend("Draft FIR legal request")} className="flex-shrink-0 bg-amber-50 text-amber-700 border border-amber-200 px-3 py-1.5 rounded-full text-xs font-medium hover:bg-amber-100 flex items-center gap-1"><Sparkles className="w-3 h-3"/> Draft FIR</button>
        </div>
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
            placeholder="Ask the AI about this case..."
            className="w-full pl-4 pr-10 py-2.5 bg-slate-100 border-none rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
          />
          <button onClick={() => handleSend(input)} className="absolute right-2 top-2 text-blue-600 hover:text-blue-800">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
