/**
 * syncService.js — Offline-first sync engine for the Polar Logistics PWA.
 *
 * This module is the bridge between the local Dexie database (the PWA's
 * source of truth while air-gapped) and the FastAPI backend (the station
 * edge-server that persists events to SQLite and eventually relays them to
 * HQ when satellite connectivity is available).
 *
 * Architecture:
 *
 *   ┌─────────────┐   outbox flush    ┌───────────────┐
 *   │  Dexie DB   │ ───────────────→  │  FastAPI /api  │
 *   │ (IndexedDB) │ ←─────────────── │  /sync/delta   │
 *   └─────────────┘   synced_ids      └───────────────┘
 *
 *   The PWA writes every user action as an event into the Dexie outbox.
 *   When connectivity is detected (or the operator manually triggers sync),
 *   this service flushes the outbox to the backend in a single batch POST.
 *   The backend processes each event through its idempotency gate and
 *   responds with which events were accepted vs. rejected.
 *
 * Key design principle: the client never directly mutates backend state
 * via REST calls.  Every mutation goes through the event-sourcing pipeline
 * (Dexie outbox → sync batch → backend process_event → ledger).  This
 * guarantees that weeks-long offline operation doesn't lose data, and that
 * re-syncing the same outbox is always safe (idempotent).
 */

import db, {
  getPendingOutboxEvents,
  markEventSynced,
} from "../db/dexie.js";
import { authFetch } from "./authService.js";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/**
 * API base URL.  Empty string means "same origin" — the Vite dev server's
 * proxy (configured in vite.config.js) forwards /api/* to the FastAPI
 * backend at http://127.0.0.1:8000.  In production, the PWA is served by
 * the same edge-server, so same-origin requests work without a proxy.
 */
const API_BASE = "";

// ---------------------------------------------------------------------------
// Pull Ground Truth (Initialization)
// ---------------------------------------------------------------------------

/**
 * Pull ground truth inventory from the backend and populate local Dexie cache.
 *
 * This is the "pull ground truth on load" counterpart to the outbox's
 * "push changes". It ensures that when the PWA boots (and the station
 * is online), it gets the latest authoritative state from the server.
 * If offline, this fails gracefully and the app relies on the existing
 * local Dexie cache.
 */
export async function syncInventoryFromServer(stationId) {
  const resp = await fetch(`${API_BASE}/api/inventory?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch inventory: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  
  // Upsert into Dexie. bulkPut replaces existing items with the same primary key.
  await db.inventory.bulkPut(items);
}

export async function syncPersonnelFromServer(stationId) {
  const resp = await fetch(`${API_BASE}/api/personnel?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch personnel: HTTP ${resp.status}`);
  }
  const data = await resp.json();
  
  // The backend endpoint returns { personnel: [...], active_missions: [...] }
  if (data.personnel && Array.isArray(data.personnel)) {
    await db.personnel.bulkPut(data.personnel);
  }
  if (data.active_missions && Array.isArray(data.active_missions)) {
    await db.fieldMissions.bulkPut(data.active_missions);
  }
}

// ---------------------------------------------------------------------------
// Core sync: flush the Dexie outbox to the backend
// ---------------------------------------------------------------------------

/**
 * Flush all pending outbox events to the backend via POST /api/sync/delta.
 *
 * This is the primary synchronisation pathway.  It is called:
 *   • Automatically when the browser fires the `online` event (satellite
 *     link restored).
 *   • Manually when the operator clicks "Force Sync via Satellite".
 *   • Periodically by a polling interval (to be wired in a later task).
 *
 * Returns a summary object:
 *   { attempted, synced, rejected, failed, error? }
 *
 * On network failure, no events are modified — they stay PENDING for the
 * next attempt.  On a successful HTTP response, each event whose
 * client_event_id appears in `synced_ids` is marked SYNCED in Dexie.
 *
 * @returns {Promise<{attempted: number, synced: number, rejected: number, failed: boolean, error?: string}>}
 */
export async function flushOutbox(stationId) {
  // ---- 1. Read the local outbox ------------------------------------------
  const pendingEvents = await getPendingOutboxEvents(stationId);

  if (pendingEvents.length === 0) {
    return { attempted: 0, synced: 0, rejected: 0, failed: false };
  }

  // ---- 2. Map Dexie records → SyncDeltaRequest shape ---------------------
  //
  // IMPORTANT: the Dexie record's `id` field IS the client_event_id that
  // the backend checks for idempotency.  We must pass it through as-is —
  // NEVER regenerate a new UUID here, or the backend's duplicate detection
  // breaks and we get double-applied events.
  //
  // The Dexie record shape:
  //   { local_id, id, event_type, station_id, payload, timestamp, sync_status }
  //
  // The backend's SyncEventIn expects:
  //   { id, event_type, station_id, timestamp, payload }

  const eventsPayload = pendingEvents.map((evt) => ({
    id: evt.id,               // client_event_id — the idempotency key
    event_type: evt.event_type,
    station_id: evt.station_id,
    timestamp: evt.timestamp,
    payload: evt.payload,
  }));

  // Build a lookup from client_event_id → local_id so we can mark the
  // correct Dexie rows as synced when the backend responds.
  // Multiple Dexie rows CAN share the same `id` if the user retried an
  // action, but in practice the UI should prevent that.  We handle it
  // by mapping id → array of local_ids and marking all of them.
  const idToLocalIds = new Map();
  for (const evt of pendingEvents) {
    if (!idToLocalIds.has(evt.id)) {
      idToLocalIds.set(evt.id, []);
    }
    idToLocalIds.get(evt.id).push(evt.local_id);
  }

  // ---- 3. POST to the backend --------------------------------------------
  let responseData;
  try {
    const resp = await authFetch(`${API_BASE}/api/sync/delta`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ events: eventsPayload }),
    });

    if (!resp.ok) {
      const errText = await resp.text().catch(() => "(no body)");
      console.error(
        `[syncService] POST /api/sync/delta failed: HTTP ${resp.status} — ${errText}`
      );
      return {
        attempted: pendingEvents.length,
        synced: 0,
        rejected: 0,
        failed: true,
        error: `HTTP ${resp.status}`,
      };
    }

    responseData = await resp.json();
  } catch (err) {
    console.warn(`[syncService] POST /api/sync/delta failed (network):`, err.message);
    return {
      attempted: pendingEvents.length,
      synced: 0,
      rejected: 0,
      failed: true,
      error: err.message,
    };
  }

  // ---- 4. Handle synced_ids ---------------------------------------------
  //
  // The backend returns the list of client_event_ids it successfully
  // applied (or successfully skipped as known duplicates).
  // We mark the corresponding Dexie rows as SYNCED so they are excluded
  // from future flushes.
  let syncedCount = 0;
  const syncedIds = responseData.synced_ids || [];

  for (const clientEventId of syncedIds) {
    const localIds = idToLocalIds.get(clientEventId);
    if (localIds) {
      for (const localId of localIds) {
        await markEventSynced(localId);
        syncedCount++;
      }
      // Remove from the map so we don't double-process if the same
      // client_event_id appears multiple times in synced_ids (which
      // happens for duplicates — the backend returns the id once for
      // the original APPLIED and once for the DUPLICATE_SKIPPED).
      idToLocalIds.delete(clientEventId);
    }
  }

  // ---- 5. Handle rejected_ids -------------------------------------------
  //
  // DESIGN DECISION: rejected events are LEFT as PENDING in the outbox
  // rather than being deleted or marked with an error state.
  //
  // Tradeoff:
  //   Pro: No silent data loss — a human or dev can inspect and fix them.
  //   Con: A permanently bad event will be resent on every sync attempt,
  //        generating repeated backend warnings.
  //
  // A production system would want a dedicated DEAD_LETTER or ERROR state
  // (distinct from both PENDING and SYNCED) plus a UI for reviewing and
  // discarding bad events.  For this prototype, the console warning is
  // sufficient to surface the issue during development and testing.
  //
  const rejectedIds = responseData.rejected_ids || [];
  if (rejectedIds.length > 0) {
    console.warn(
      `[syncService] ${rejectedIds.length} event(s) REJECTED by backend:`,
      rejectedIds,
      "These events remain PENDING in the outbox and will be resent on the " +
        "next sync attempt.  Inspect and fix them manually if the rejection " +
        "is due to a bad payload."
    );
  }

  return {
    attempted: pendingEvents.length,
    synced: syncedCount,
    rejected: rejectedIds.length,
    failed: false,
  };
}


// ---------------------------------------------------------------------------
// Connectivity state
// ---------------------------------------------------------------------------

/**
 * Return whether the browser currently considers itself online.
 * Note: this is a weak check. `navigator.onLine === true` just means
 * connected to a local router; the actual satellite uplink may still be down.
 */
export function isOnline() {
  return navigator.onLine;
}

/**
 * Attach listeners to the browser's native 'online'/'offline' events.
 *
 * @param {function} onStatusChange — Callback invoked with the boolean online status
 * @param {string} stationId - The station identifier
 * @returns {function} Cleanup function to remove the listeners
 */
export function initNetworkListeners(onStatusChange, stationId) {
  const handleOnline = () => {
    console.info(
      "[syncService] Network online — satellite connection restored. Triggering auto-sync..."
    );
    onStatusChange(true);

    // Fire-and-forget the flush. We don't await it because the event
    // handler is synchronous.  flushOutbox logs its own errors internally.
    flushOutbox(stationId).catch((err) => {
      console.error("[syncService] Auto-sync after reconnect failed:", err);
    });
  };

  const handleOffline = () => {
    console.info("[syncService] Network offline — entering air-gapped mode.");
    onStatusChange(false);
  };

  window.addEventListener("online", handleOnline);
  window.addEventListener("offline", handleOffline);

  // Return cleanup function for React useEffect teardown.
  return () => {
    window.removeEventListener("online", handleOnline);
    window.removeEventListener("offline", handleOffline);
  };
}


// ---------------------------------------------------------------------------
// Manual trigger functions (for UI buttons)
// ---------------------------------------------------------------------------

/**
 * Manually trigger an outbox flush.
 *
 * Backs the "Force Sync via Satellite" button in the dashboard header.
 * This is identical to the auto-sync triggered by the `online` event,
 * but initiated explicitly by the station operator when they know the
 * satellite window is open and want to push immediately.
 *
 * @returns {Promise<{attempted: number, synced: number, rejected: number, failed: boolean, error?: string}>}
 */
export async function forceSyncNow(stationId) {
  return flushOutbox(stationId);
}

/**
 * Export all pending outbox events as a sneakernet JSON bundle and trigger
 * a browser file download.
 *
 * DESIGN DECISION — export PENDING events only, not ALL events:
 *
 *   The sneakernet bundle's purpose is to fill the gap between what the
 *   backend already knows and what this client has queued locally.  Events
 *   already marked SYNCED have been accepted by the backend — re-exporting
 *   them would be redundant (the backend's idempotency gate would skip
 *   them anyway, but it wastes bandwidth and USB space for no reason).
 *
 *   Exporting only PENDING events means the USB file contains exactly the
 *   data the backend is missing — which is the entire point of physically
 *   carrying a file between stations when the satellite has been down for
 *   weeks.
 *
 * The hash is computed to match the backend's verify_snapshot_hash():
 *   SHA-256 of canonical JSON (sorted keys, compact separators) of the
 *   bundle object EXCLUDING the `hash` field itself.
 *
 * @param {string} [stationId="BHARATI"] — the station identifier
 * @returns {Promise<object>} the complete bundle object (with hash)
 */
export async function exportSneakernetSnapshot(stationId) {
  const pendingEvents = await getPendingOutboxEvents();

  // Build the bundle without the hash field first.
  const bundle = {
    station_id: stationId,
    exported_at: new Date().toISOString(),
    events: pendingEvents.map((evt) => ({
      id: evt.id,
      event_type: evt.event_type,
      station_id: evt.station_id,
      timestamp: evt.timestamp,
      payload: evt.payload,
    })),
  };

  // ---- Compute SHA-256 hash ----------------------------------------------
  // Must match backend's verify_snapshot_hash() exactly:
  //   canonical JSON = sorted keys, compact separators (",", ":"),
  //   str() fallback for non-JSON types.
  //
  // JSON.stringify with a replacer and sorted keys produces the same
  // output as Python's json.dumps(sort_keys=True, separators=(',', ':')).
  // We use a custom replacer to handle key sorting at all nesting levels.

  const canonicalJson = jsonCanonical(bundle);
  const hashHex = await sha256Hex(canonicalJson);

  // Add hash to the bundle.
  bundle.hash = hashHex;

  // ---- Trigger browser file download -------------------------------------
  const filename = `sneakernet-export-${stationId}-${bundle.exported_at.replace(/[:.]/g, "-")}.json`;
  const blob = new Blob([JSON.stringify(bundle, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();

  // Cleanup: remove the temporary anchor and revoke the object URL to
  // free memory.  The setTimeout ensures the download starts before
  // we revoke.
  setTimeout(() => {
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  }, 100);

  console.info(
    `[syncService] Sneakernet bundle exported: ${filename} ` +
      `(${pendingEvents.length} events, hash=${hashHex.slice(0, 12)}...)`
  );

  return bundle;
}


// ---------------------------------------------------------------------------
// Internal utilities
// ---------------------------------------------------------------------------

/**
 * Produce canonical JSON with sorted keys and compact separators at all
 * nesting levels.  This matches Python's:
 *   json.dumps(obj, sort_keys=True, separators=(',', ':'), default=str)
 *
 * @param {any} obj
 * @returns {string}
 */
function jsonCanonical(obj) {
  // JSON.stringify's replacer doesn't sort keys.  We recursively rebuild
  // objects with sorted keys before serialising.
  return JSON.stringify(sortKeysDeep(obj));
}

/**
 * Recursively sort object keys at every level of nesting.
 * Arrays are traversed but their order is preserved (only object keys sort).
 */
function sortKeysDeep(val) {
  if (val === null || val === undefined) return val;
  if (Array.isArray(val)) return val.map(sortKeysDeep);
  if (typeof val === "object" && !(val instanceof Date)) {
    const sorted = {};
    for (const key of Object.keys(val).sort()) {
      sorted[key] = sortKeysDeep(val[key]);
    }
    return sorted;
  }
  return val;
}

/**
 * Compute SHA-256 of a UTF-8 string using the Web Crypto API.
 *
 * @param {string} text
 * @returns {Promise<string>} lowercase hex digest
 */
async function sha256Hex(text) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function syncExpeditionsFromServer(stationId) {
  const resp = await fetch(`${API_BASE}/api/expeditions?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch expeditions: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  
  // Re-apply local PENDING cancellations so server data doesn't overwrite un-synced offline actions
  const pendingEvents = await getPendingOutboxEvents(stationId);
  const canceledIds = new Set(
    pendingEvents
      .filter(e => e.event_type === "EXPEDITION_CANCELLED")
      .map(e => e.payload.expedition_id)
  );
  
  for (const item of items) {
    if (canceledIds.has(item.id)) {
      item.status = "CANCELLED";
    }
  }

  await db.plannedExpeditions.bulkPut(items);
}

export async function syncDirectivesFromServer(stationId) {
  const resp = await fetch(`${API_BASE}/api/directives?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch directives: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  await db.directives.bulkPut(items);
}


export async function syncCargoFromServer(stationId) {
  const resp = await fetch(`${API_BASE}/api/cargo?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch cargo: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  await db.cargoShipments.bulkPut(items);
}
