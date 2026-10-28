import re
with open("src/App.jsx", "r", encoding="utf-8") as f:
    txt = f.read()

txt = txt.replace('<div className="panel-stagger-2"><DashboardSummary session={session} /></div>', '')
txt = txt.replace('import DashboardSummary from "./components/DashboardSummary.jsx";', '')

with open("src/App.jsx", "w", encoding="utf-8") as f:
    f.write(txt)
print("App.jsx cleaned")
