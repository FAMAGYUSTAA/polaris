import glob

replacements = {
    '&#128230;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>inventory_2</span>',
    '&#128666;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>directions_boat</span>',
    '&#9873;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>flag</span>',
    '&#128101;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>groups</span>',
    '&#9888;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>warning</span>',
    '&#128197;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>calendar_today</span>',
    '&#128196;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>description</span>',
    '&#128737;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>security</span>',
    '&#127968;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>home</span>',
    '&#128205;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>pin_drop</span>',
    '&#9976;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>flag</span>',
    '&#128110;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>security</span>',
    '&#128202;': '<span className="material-symbols-outlined" style={{fontSize: "inherit"}}>bar_chart</span>',
}

files = glob.glob('src/components/*.jsx') + ['src/App.jsx']
for file in files:
    with open(file, encoding='utf-8') as f:
        txt = f.read()
    for old, new in replacements.items():
        txt = txt.replace(old, new)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(txt)
