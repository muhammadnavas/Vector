const fs = require('fs');

let content = fs.readFileSync('src/style/HomePage.jsx', 'utf8');

const replacements = [
  ['<GlowButton primary>🚀 Run Your First Test</GlowButton>', '<GlowButton primary><span style={{display: \'inline-flex\', alignItems: \'center\', gap: \'8px\'}}><Rocket size={18} /> Run Your First Test</span></GlowButton>'],
  ['<span style={{ color: \'#a78bfa\' }}>✓</span>', '<span style={{ color: \'#a78bfa\' }}><Check size={16} /></span>'],
  ['<span style={{ color: \'#f87171\' }}>✗</span>', '<span style={{ color: \'#f87171\' }}><X size={16} /></span>'],
  ['<span style={{ color: \'#a78bfa\' }}>💡 Fix:</span>', '<span style={{ color: \'#a78bfa\', display: \'inline-flex\', alignItems: \'center\', gap: \'4px\' }}><Lightbulb size={16} /> Fix:</span>']
];

for (let [oldStr, newStr] of replacements) {
    let replaced = false;
    content = content.replace(new RegExp(oldStr.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), () => { replaced = true; return newStr; });
    if (!replaced) console.log("Missed:", oldStr);
}

const importsToAdd = "import { Rocket, Check, X, Lightbulb } from 'lucide-react';\n";
if (!content.includes('Rocket')) {
    content = importsToAdd + content;
}

fs.writeFileSync('src/style/HomePage.jsx', content);
