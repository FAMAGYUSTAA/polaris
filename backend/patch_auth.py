import re

with open('frontend/src/services/authService.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix export async function login
code = code.replace(
    'export async function login(stationId, username, password) {',
    'export async function login(stationId, username, password, selectedRole) {'
)

# Fix online validation
code = code.replace(
    """      const session = {
        username: payload.sub,
        role: payload.role,
        station_id: payload.station_id,
        token: data.access_token,
        mode: "online",
        authenticated_at: new Date().toISOString(),
      };""",
    """      if (payload.role !== selectedRole && payload.role !== "STATION" && payload.role !== "HQ") {
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
      };"""
)

# Update fallback to offline
code = code.replace(
    '  return loginOffline(stationId, username, password);',
    '  return loginOffline(stationId, username, password, selectedRole);'
)

# Fix loginOffline signature
code = code.replace(
    'async function loginOffline(stationId, username, password) {',
    'async function loginOffline(stationId, username, password, selectedRole) {'
)

# Add offline validation
code = code.replace(
    '  if (record.station_id !== stationId) {\n    return { success: false, error: "Incorrect station selection", mode: "offline" };\n  }',
    """  if (record.station_id !== stationId) {
    return { success: false, error: "Incorrect station selection", mode: "offline" };
  }

  if (record.role !== selectedRole) {
    return { success: false, error: "Selected role does not match your assigned role.", mode: "offline" };
  }"""
)

with open('frontend/src/services/authService.js', 'w', encoding='utf-8') as f:
    f.write(code)
