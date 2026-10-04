const fs = require('fs');
const path = require('path');

function walkDir(dir, callback) {
  fs.readdirSync(dir).forEach(f => {
    let dirPath = path.join(dir, f);
    let isDirectory = fs.statSync(dirPath).isDirectory();
    isDirectory ? 
      walkDir(dirPath, callback) : callback(path.join(dir, f));
  });
}

walkDir('/home/finex/Desktop/projects/uncompleted/chainnetra-sih26138/frontend/src', function(filePath) {
  if (filePath.endsWith('.tsx') || filePath.endsWith('.ts')) {
    let content = fs.readFileSync(filePath, 'utf8');
    let original = content;
    
    // text-slate-100 on headings should be text-slate-900
    content = content.replace(/text-slate-100/g, 'text-slate-900');
    
    // hover:bg-slate-700 on light buttons should be hover:bg-slate-200
    content = content.replace(/hover:bg-slate-700/g, 'hover:bg-slate-200');
    
    // bg-slate-800/50 dividers should be bg-slate-200 (if any)
    content = content.replace(/bg-slate-800\/50/g, 'bg-slate-200');
    
    // Timeline dots with border-slate-900 should be border-white
    content = content.replace(/border-slate-900/g, 'border-white');

    if (content !== original) {
      console.log(`Updated ${filePath}`);
      fs.writeFileSync(filePath, content, 'utf8');
    }
  }
});
