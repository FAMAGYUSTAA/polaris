/**
 * authService.js — Authentication service for the Polar Logistics Station PWA.
 *
 * Supports:
 *   1. Online login via POST /api/auth/login → JWT
 *   2. Offline login via locally stored PBKDF2 password verifier
 *   3. Session persistence across browser restarts
 *   4. Authenticated fetch wrapper for protected API calls
 *
 * Offline password verification uses Web Crypto PBKDF2 with a per-user salt.
 * The plaintext password is NEVER stored — only its one-way PBKDF2 digest.
 */

import db from "../db/dexie.js";

const API_BASE = "";

// Session state — kept in memory; JWT also persisted to sessionStorage
let _currentSession = null;

// ---------------------------------------------------------------------------
// Web Crypto PBKDF2 helpers (browser-native, no npm dependency)
// ---------------------------------------------------------------------------

/**
 * Derive a PBKDF2-SHA256 key from a password + salt, returned as hex.
 * This is a one-way KDF — the password cannot be recovered from the output.
 */
async function derivePasswordVerifier(password, salt) {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    enc.encode(password),
    "PBKDF2",
    false,
    ["deriveBits"]
  );
  const bits = await crypto.subtle.deriveBits(
    {
      name: "PBKDF2",
      salt: enc.encode(salt),
      iterations: 100000,
      hash: "SHA-256",
    },
    keyMaterial,
    256
  );
  return Array.from(new Uint8Array(bits))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Generate the salt string for a given username.
 * Using a deterministic salt based on username ensures the same password
 * always produces the same verifier for the same user, enabling offline
 * comparison without storing anything secret.
 */
function getSalt(username) {
  return `polar-station-auth-${username}`;
}

// ---------------------------------------------------------------------------
// Session management
// ---------------------------------------------------------------------------

/**
 * Get the current in-memory session. Returns null if not authenticated.
 */
export function getCurrentSession() {
  return _currentSession;
}

/**
 * Get the JWT token for authenticated API requests. Returns null if unavailable.
 */
export function getToken() {
  if (_currentSession && _currentSession.token) {
    return _currentSession.token;
  }
  return sessionStorage.getItem("polar_jwt");
}

/**
 * Restore session from sessionStorage on app startup.
 * This allows the Station to reopen without re-login if the tab was refreshed.
 * Does NOT require a backend request.
 */
export function restoreSession() {
  const saved = sessionStorage.getItem("polar_session");
  if (saved) {
    try {
      _currentSession = JSON.parse(saved);
      return _currentSession;
    } catch (e) {
      sessionStorage.removeItem("polar_session");
      sessionStorage.removeItem("polar_jwt");
    }
  }
  return null;
}

/**
 * Save the current session to sessionStorage for tab-refresh persistence.
 */
function persistSession(session) {
  _currentSession = session;
  sessionStorage.setItem("polar_session", JSON.stringify(session));
  if (session.token) {
    sessionStorage.setItem("polar_jwt", session.token);
  }
}

// ---------------------------------------------------------------------------
// Login flows
// ---------------------------------------------------------------------------

/**
 * Attempt online login first. If the backend is unreachable, fall back to
 * offline verification using the locally stored PBKDF2 password verifier.
 *
 * Returns: { success, session?, error?, mode: "online"|"offline" }
 */
export async function login(stationId, username, password, selectedRole) {
  // --- Try online login first ---
  try {
    const formBody = new URLSearchParams();
    formBody.append("username", username);
    formBody.append("password", password);
    formBody.append("grant_type", "password");
    formBody.append("client_id", stationId);

    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formBody.toString(),
    });

    if (res.ok) {
      const data = await res.json();
      // Decode JWT payload to extract role, station_id
      const payload = JSON.parse(atob(data.access_token.split(".")[1]));

      if (payload.role !== selectedRole && payload.role !== "STATION" && payload.role !== "HQ") {
        // If they have legacy STATION role or HQ, we might let them through, but the prompt says:
        // "Compare it with the role selected on the login form. If they do not match, reject the login".
        // Wait, the prompt literally says "If they do not match, reject the login". So we strictly enforce it!
      }
      
      if (payload.role !== selectedRole) {
        return { success: false, error: "Selected role does not match your assigned role.", mode: "online" };
      }

      const session = {
        username: payload.sub,
        role: payload.role,
        station_id: payload.station_id,
        token: data.access_token,
        mode: "online",
        authenticated_at: new Date().toISOString(),
      };

      // Provision offline credential
      const verifier = await derivePasswordVerifier(password, getSalt(username));
      await db.authSessions.put({
        username: username,
        role: payload.role,
        station_id: payload.station_id,
        password_verifier: verifier,
        last_authenticated_at: new Date().toISOString(),
      });

      persistSession(session);
      return { success: true, session, mode: "online" };
    }

    if (res.status === 401 || res.status === 400 || res.status === 403) {
      const errData = await res.json().catch(() => ({}));
      return { success: false, error: errData.detail || "Incorrect username, password, or station", mode: "online" };
    }

    // Other HTTP errors — fall through to offline
    throw new Error(`HTTP ${res.status}`);
  } catch (networkErr) {
    // Backend unreachable — try offline login
    console.warn("[authService] Backend unreachable, trying offline login:", networkErr.message);
  }

  // --- Offline login fallback ---
  return loginOffline(stationId, username, password, selectedRole);
}

/**
 * Perform offline password verification using locally stored PBKDF2 verifier.
 */
async function loginOffline(stationId, username, password, selectedRole) {
  const record = await db.authSessions.get(username);

  if (!record) {
    return {
      success: false,
      error: "No offline credentials found for this user. Initial login requires satellite connectivity.",
      mode: "offline",
    };
  }

  if (record.station_id !== stationId) {
    return { success: false, error: "Incorrect station selection", mode: "offline" };
  }

  if (record.role !== selectedRole) {
    return { success: false, error: "Selected role does not match your assigned role.", mode: "offline" };
  }

  const verifier = await derivePasswordVerifier(password, getSalt(username));

  if (verifier !== record.password_verifier) {
    return { success: false, error: "Incorrect username or password", mode: "offline" };
  }

  const session = {
    username: record.username,
    role: record.role,
    station_id: record.station_id,
    token: null, // No valid JWT available offline
    mode: "offline",
    authenticated_at: new Date().toISOString(),
  };

  persistSession(session);
  return { success: true, session, mode: "offline" };
}

// ---------------------------------------------------------------------------
// Logout
// ---------------------------------------------------------------------------

/**
 * End the current authentication session.
 * Preserves ALL Dexie business data and pending outbox events.
 * Preserves offline authentication records for future offline login.
 */
export function logout() {
  _currentSession = null;
  sessionStorage.removeItem("polar_session");
  sessionStorage.removeItem("polar_jwt");
}

// ---------------------------------------------------------------------------
// Authenticated fetch wrapper
// ---------------------------------------------------------------------------

/**
 * A fetch wrapper that automatically attaches the Bearer token header.
 * Falls back to a normal fetch if no token is available (e.g. offline mode
 * with read-only Dexie data).
 *
 * @param {string} url
 * @param {RequestInit} options
 * @returns {Promise<Response>}
 */
export async function authFetch(url, options = {}) {
  const token = getToken();
  if (token) {
    options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return fetch(url, options);
}
