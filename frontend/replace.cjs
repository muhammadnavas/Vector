const fs = require('fs');

let content = fs.readFileSync('src/style/TestRunner.jsx', 'utf8');

const replacements = [
  ['🚀 Trigger Test Run', '<span style={{display: \'flex\', alignItems: \'center\', gap: \'12px\'}}><Rocket size={24} /> Trigger Test Run</span>'],
  ['❌ {error}', '<span style={{display: \'flex\', alignItems: \'center\', gap: \'8px\'}}><XCircle size={18} /> {error}</span>'],
  ["{loading ? '⏳ Running Tests...' : '▶️ Run Tests'}", "{loading ? <span style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'}}><Loader2 className=\"animate-spin\" size={18} /> Running Tests...</span> : <span style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'}}><Play size={18} /> Run Tests</span>}"],
  ["{loading ? '⏳ Discovering Endpoints...' : '🔎 Discover Endpoints from Repo URL'}", "{loading ? <span style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'}}><Loader2 className=\"animate-spin\" size={18} /> Discovering Endpoints...</span> : <span style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'}}><Search size={18} /> Discover Endpoints from Repo URL</span>}"],
  ['📊 Execution Results', '<span style={{display: \'flex\', alignItems: \'center\', gap: \'12px\'}}><BarChart2 size={24} /> Execution Results</span>'],
  ["{currentExecution.status === 'pending' && '⏳ Pending'}", "{currentExecution.status === 'pending' && <span style={{display: 'flex', alignItems: 'center', gap: '8px'}}><Hourglass size={18} /> Pending</span>}"],
  ["{currentExecution.status === 'processing' && '⚙️ Processing'}", "{currentExecution.status === 'processing' && <span style={{display: 'flex', alignItems: 'center', gap: '8px'}}><Cog className=\"animate-spin\" size={18} /> Processing</span>}"],
  ["{currentExecution.status === 'completed' && '✅ Completed'}", "{currentExecution.status === 'completed' && <span style={{display: 'flex', alignItems: 'center', gap: '8px'}}><CheckCircle size={18} /> Completed</span>}"],
  ["{(currentExecution.status === 'failed' || currentExecution.success === false) && '❌ Failed'}", "{(currentExecution.status === 'failed' || currentExecution.success === false) && <span style={{display: 'flex', alignItems: 'center', gap: '8px'}}><XCircle size={18} /> Failed</span>}"],
  ['🔗 Tested Endpoints', '<span style={{display: \'flex\', alignItems: \'center\', gap: \'12px\'}}><Link2 size={20} /> Tested Endpoints</span>'],
  ["{endpoint.auth_required ? '🔐 Auth Required' : '🔓 Public'}", "{endpoint.auth_required ? <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}><Lock size={14} /> Auth Required</span> : <span style={{display: 'flex', alignItems: 'center', gap: '4px'}}><Unlock size={14} /> Public</span>}"],
  ['⚠️ Failures & Fixes', '<span style={{display: \'flex\', alignItems: \'center\', gap: \'12px\'}}><AlertTriangle size={20} /> Failures & Fixes'],
  ['<strong>💡 Suggested Fix:</strong>', '<strong><span style={{display: \'inline-flex\', alignItems: \'center\', gap: \'4px\'}}><Lightbulb size={16} /> Suggested Fix:</span></strong>'],
  ['📄 Full Report', '<span style={{display: \'flex\', alignItems: \'center\', gap: \'12px\'}}><FileText size={20} /> Full Report</span>']
];

for (let [oldStr, newStr] of replacements) {
    let replaced = false;
    content = content.replace(oldStr, () => { replaced = true; return newStr; });
    if (!replaced) console.log("Missed:", oldStr);
}

// Add imports
const importsToAdd = "import { Rocket, XCircle, Loader2, Play, BarChart2, Hourglass, Link2, Lock, Unlock, AlertTriangle, Lightbulb, FileText } from 'lucide-react';\n";
if (!content.includes('Rocket')) {
    content = content.replace("import { Satellite", importsToAdd + "import { Satellite");
}

fs.writeFileSync('src/style/TestRunner.jsx', content);
