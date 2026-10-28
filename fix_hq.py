import glob
import re

for filepath in glob.glob("polar-hq-dashboard/src/components/*.jsx"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip HQLogin and other non-data panels if they don't have BHARATI
    if "station_id=BHARATI" not in content and "\"BHARATI\"" not in content and "'BHARATI'" not in content:
        continue

    # 1. Update signature to receive stationId
    content = re.sub(r'export default function (\w+)\(\)\s*\{', r'export default function \1({ stationId }) {', content)

    # 2. Update API URLs from strings to template literals or concatenation
    # e.g., "/api/personnel?station_id=BHARATI" -> `/api/personnel?station_id=${stationId}`
    # using simple concatenation: "/api/personnel?station_id=" + stationId
    content = content.replace('"/api/personnel?station_id=BHARATI"', '`/api/personnel?station_id=${stationId}`')
    content = content.replace('"/api/cargo?station_id=BHARATI"', '`/api/cargo?station_id=${stationId}`')
    content = content.replace('"/api/directives?station_id=BHARATI"', '`/api/directives?station_id=${stationId}`')
    content = content.replace('"/api/expeditions?station_id=BHARATI"', '`/api/expeditions?station_id=${stationId}`')
    content = content.replace('"/api/health?station_id=BHARATI"', '`/api/health?station_id=${stationId}`')

    # Also catch any other endpoints
    content = re.sub(r'"(/api/[^?]+\?station_id=)BHARATI"', r'`\1${stationId}`', content)

    # 3. Update body objects
    content = content.replace('station_id: "BHARATI"', 'station_id: stationId')

    # 4. Update useEffect dependency array from [] to [stationId]
    # We must be careful not to match random arrays, just the useEffect ones at the end
    # `}, []);` -> `}, [stationId]);`
    content = content.replace('}, []);', '}, [stationId]);')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
