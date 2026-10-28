import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = re.sub(r'\{theme === \'light\' \? \'.*?\' : \'.*?\'\}', '{theme === "light" ? "🌙" : "☀️"}', txt)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(txt)
