import re

def add_session_prop(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        txt = f.read()
    
    # Replace export default function XXX({ stationId }) with export default function XXX({ stationId, session })
    txt = re.sub(r'export default function (\w+)\(\{\s*stationId\s*\}\)', r'export default function \1({ stationId, session })', txt)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt)

add_session_prop('src/components/AssetInventory.jsx')
add_session_prop('src/components/CargoTracking.jsx')
add_session_prop('src/components/DirectivesPanel.jsx')

print("Added session prop to components.")
