import re

with open("frontend/src/components/Tabs/EvidenceTab.tsx", "r") as f:
    content = f.read()

# Add download function
download_func = """
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
"""

content = content.replace("  const generateFreezeRequest = async () => {", download_func + "\n  const generateFreezeRequest = async () => {")

# Update button
old_btn = """<button className="text-slate-600 hover:text-blue-400 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Download className="w-5 h-5" />
          </button>"""
          
new_btn = """<button onClick={generateSubpoena} className="text-slate-600 hover:text-blue-400 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Download className="w-5 h-5" />
          </button>"""

content = content.replace(old_btn, new_btn)

with open("frontend/src/components/Tabs/EvidenceTab.tsx", "w") as f:
    f.write(content)
