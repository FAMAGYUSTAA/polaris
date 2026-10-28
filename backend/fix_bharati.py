import os
import glob

def fix_component(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Generic replaces
    content = content.replace("station_id: \"BHARATI\"", "station_id: stationId")
    content = content.replace("export default function CargoTracking() {", "export default function CargoTracking({ stationId }) {")
    content = content.replace("export default function DirectivesPanel() {", "export default function DirectivesPanel({ stationId }) {")
    content = content.replace("export default function EmergencyMuster() {", "export default function EmergencyMuster({ stationId }) {")
    content = content.replace("export default function ExpeditionPlanning() {", "export default function ExpeditionPlanning({ stationId }) {")
    content = content.replace("export default function PersonnelTracker() {", "export default function PersonnelTracker({ stationId }) {")
    content = content.replace("export default function AssetInventory() {", "export default function AssetInventory({ stationId }) {")
    content = content.replace("export default function SneakernetExport() {", "export default function SneakernetExport({ stationId }) {")

    # Sync calls
    content = content.replace("syncCargoFromServer()", "syncCargoFromServer(stationId)")
    content = content.replace("syncDirectivesFromServer()", "syncDirectivesFromServer(stationId)")
    content = content.replace("syncExpeditionsFromServer()", "syncExpeditionsFromServer(stationId)")
    content = content.replace("syncInventoryFromServer()", "syncInventoryFromServer(stationId)")
    content = content.replace("syncPersonnelFromServer()", "syncPersonnelFromServer(stationId)")
    content = content.replace("exportSneakernetSnapshot(\"BHARATI\")", "exportSneakernetSnapshot(stationId)")
    content = content.replace("sneakernet-export-BHARATI", "sneakernet-export-${stationId}")

    # Dexie local filters. Replace `db.<table_name>.toArray()` with `db.<table_name>.where('station_id').equals(stationId).toArray()` ?
    # Wait, in Dexie, unless we add an index on `station_id`, `where` won't work easily if it's not indexed.
    # Alternatively we can just filter it in JS: `const all = await db.X.toArray(); all.filter(...)`
    # Let's do JS filtering.
    content = content.replace("allItems.sort(", "allItems.filter(i => i.station_id === stationId).sort(")
    content = content.replace("db.cargoShipments.toArray()", "db.cargoShipments.filter(i => i.station_id === stationId).toArray()")
    content = content.replace("db.directives.toArray()", "db.directives.filter(i => i.station_id === stationId).toArray()")
    content = content.replace("db.plannedExpeditions.toArray()", "db.plannedExpeditions.filter(i => i.station_id === stationId).toArray()")
    content = content.replace("db.personnel.toArray()", "db.personnel.filter(i => i.station_id === stationId).toArray()")
    content = content.replace("db.fieldMissions.toArray()", "db.fieldMissions.filter(i => i.station_id === stationId).toArray()")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

for f in glob.glob("frontend/src/components/*.jsx"):
    fix_component(f)
