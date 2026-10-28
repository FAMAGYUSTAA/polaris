/**
 * authService.js — Authentication service for the HQ Dashboard.
 *
 * HQ is online-only: it always requires a valid backend JWT.
 * No offline credential storage is implemented for HQ.
 */

let _currentSession = null;

/**
 * Get the current session. Returns null if not authenticated.
 */
export function getCurrentSession() {
  return _currentSession;
}

/**
 * Get the JWT token for authenticated API requests.
 */
export function getToken() {
  if (_currentSession && _currentSession.token) {
    return _currentSession.token;
  }
  return sessionStorage.getItem("hq_jwt");
}

/**
 * Restore session from sessionStorage on app startup.
 */
export function restoreSession() {
  const saved = sessionStorage.getItem("hq_session");
  if (saved) {
    try {
      _currentSession = JSON.parse(saved);
      return _currentSession;
    } catch (e) {
      sessionStorage.removeItem("hq_session");
      sessionStorage.removeItem("hq_jwt");
    }
  }
  return null;
}

function persistSession(session) {
  _currentSession = session;
  sessionStorage.setItem("hq_session", JSON.stringify(session));
  if (session.token) {
    sessionStorage.setItem("hq_jwt", session.token);
  }
}

/**
 * Online-only login for HQ users.
 */
export async function login(username, password) {
  try {
    const formBody = new URLSearchParams();
    formBody.append("username", username);
    formBody.append("password", password);
    formBody.append("grant_type", "password");

    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formBody.toString(),
    });

    if (res.ok) {
      const data = await res.json();
      const payload = JSON.parse(atob(data.access_token.split(".")[1]));

      if (payload.role !== "HQ") {
        return { success: false, error: "This account does not have HQ access." };
      }

      const session = {
        username: payload.sub,
        role: payload.role,
        station_id: payload.station_id,
        token: data.access_token,
        authenticated_at: new Date().toISOString(),
      };

      persistSession(session);
      return { success: true, session };
    }

    if (res.status === 401 || res.status === 400) {
      return { success: false, error: "Incorrect username or password" };
    }

    return { success: false, error: `Server error (HTTP ${res.status})` };
  } catch (err) {
    return { success: false, error: "Unable to connect to HQ server. Please check connectivity." };
  }
}

/**
 * End the current HQ session.
 */
export function logout() {
  _currentSession = null;
  sessionStorage.removeItem("hq_session");
  sessionStorage.removeItem("hq_jwt");
}

/**
 * Authenticated fetch wrapper for HQ API requests.
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
