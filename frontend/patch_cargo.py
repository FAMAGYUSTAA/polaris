import re

with open('src/components/CargoTracking.jsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# 1. Pass stationId to NewShipmentModal
txt = txt.replace(
    '<NewShipmentModal onClose={() => setShowModal(false)} onCreated={() => { setShowModal(false); init(); }} />',
    '<NewShipmentModal stationId={stationId} onClose={() => setShowModal(false)} onCreated={() => { setShowModal(false); init(); }} />'
)

# 2. Add stationId to NewShipmentModal props
txt = txt.replace(
    'function NewShipmentModal({ onClose, onCreated }) {',
    'function NewShipmentModal({ stationId, onClose, onCreated }) {'
)

# 3. Move payload creation inside try block
# We will match the handleSubmit function inside NewShipmentModal.

old_submit = """
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    // Ensure numbers for quantity
    const processedManifest = manifest.map(m => ({
      ...m,
      quantity: parseFloat(m.quantity) || 0
    })).filter(m => m.sku.trim() !== "");

    const shipmentId = crypto.randomUUID();
    const now = new Date().toISOString();

    const payload = {
      id: shipmentId,
      station_id: stationId,
      carrier_name: formData.carrier_name,
      origin: formData.origin,
      departure_date: new Date(formData.departure_date).toISOString(),
      expected_arrival: new Date(formData.expected_arrival).toISOString(),
      manifest: processedManifest,
      status: "PENDING_APPROVAL",
      hq_approved: false,
      created_at: now
    };

    try {
      // 1. Save to Dexie
      await db.cargoShipments.add({
        ...payload,
        arrived_at: null
      });

      // 2. Queue outbox event
      await db.outboxEvents.add({
        id: shipmentId, // using shipment ID as client_event_id is fine, or new UUID
        event_type: "CARGO_CREATED",
        payload: payload,
        timestamp: now,
        sync_status: "PENDING",
        station_id: stationId
      });

      onCreated();
    } catch (err) {
      console.error("Failed to create shipment locally:", err);
      alert("Failed to create shipment.");
    } finally {
      setSubmitting(false);
    }
  };
"""

new_submit = """
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Ensure numbers for quantity
      const processedManifest = manifest.map(m => ({
        ...m,
        quantity: parseFloat(m.quantity) || 0
      })).filter(m => m.sku.trim() !== "");

      const shipmentId = crypto.randomUUID();
      const now = new Date().toISOString();

      const payload = {
        id: shipmentId,
        station_id: stationId,
        carrier_name: formData.carrier_name,
        origin: formData.origin,
        departure_date: new Date(formData.departure_date).toISOString(),
        expected_arrival: new Date(formData.expected_arrival).toISOString(),
        manifest: processedManifest,
        status: "PENDING_APPROVAL",
        hq_approved: false,
        created_at: now
      };

      // 1. Save to Dexie
      await db.cargoShipments.add({
        ...payload,
        arrived_at: null
      });

      // 2. Queue outbox event
      await db.outboxEvents.add({
        id: crypto.randomUUID(), // outbox event needs its own id
        event_type: "CARGO_CREATED",
        payload: payload,
        timestamp: now,
        sync_status: "PENDING",
        station_id: stationId
      });

      onCreated();
    } catch (err) {
      console.error("Failed to create shipment locally:", err);
      alert("Failed to create shipment.");
    } finally {
      setSubmitting(false);
    }
  };
"""

if old_submit.strip() in txt:
    txt = txt.replace(old_submit.strip(), new_submit.strip())
else:
    print("Could not find old_submit string exactly.")
    
with open('src/components/CargoTracking.jsx', 'w', encoding='utf-8') as f:
    f.write(txt)
    
print("CargoTracking patched.")
