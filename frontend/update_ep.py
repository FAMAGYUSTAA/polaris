with open("src/components/ExpeditionPlanning.jsx", "r", encoding="utf-8") as f:
    txt = f.read()
txt = txt.replace('className="btn-confirm"', 'className="btn-primary"')
txt = txt.replace('className="btn-cancel"', 'className="btn-secondary"')
txt = txt.replace('style={{ gridColumn: "1 / -1" }}', 'style={{ gridColumn: "1 / -1", marginTop: "1rem" }}')
with open("src/components/ExpeditionPlanning.jsx", "w", encoding="utf-8") as f:
    f.write(txt)
print("ExpeditionPlanning buttons fixed.")
