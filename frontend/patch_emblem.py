import re

with open('src/components/StationLogin.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(r'<div className="moes-emblem-placeholder">.*?</div>', '<img src="/moes-emblem.png" alt="Government of India Emblem" className="moes-emblem" onError={(e) => e.target.style.display=\'none\'} />', c, flags=re.DOTALL)

with open('src/components/StationLogin.jsx', 'w', encoding='utf-8') as f:
    f.write(c)
