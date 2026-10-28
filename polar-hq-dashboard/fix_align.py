with open('src/App.jsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    'style={{ display: "flex", flexDirection: "column", justifyContent: "center", textAlign: "right", gap: "0.15rem", lineHeight: 1.2, flex: 1 }}',
    'style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "flex-end", textAlign: "right", gap: "0.15rem", lineHeight: 1.2, flex: 1 }}'
)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(txt)
