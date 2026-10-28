import re

with open('frontend/src/components/StationLogin.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add import for ROLE_LABELS
code = code.replace(
    'import { login } from "../services/authService.js";',
    'import { login } from "../services/authService.js";\nimport { ROLE_LABELS, ROLES } from "../permissions.js";'
)

# Add selectedRole to state
code = code.replace(
    '  const [password, setPassword] = useState("");',
    '  const [password, setPassword] = useState("");\n  const [selectedRole, setSelectedRole] = useState("STATION_LEADER");'
)

# Pass selectedRole to login
code = code.replace(
    'const result = await login(stationId, username.trim(), password);',
    'const result = await login(stationId, username.trim(), password, selectedRole);'
)

# Add Role dropdown field in UI right after Station select
role_field = """
          <div style={{ marginBottom: "1.25rem" }}>
            <label style={{ display: "block", marginBottom: "0.4rem", color: "#94a3b8", fontSize: "0.9rem" }}>
              Role
            </label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              style={{
                width: "100%",
                padding: "0.6rem 0.8rem",
                backgroundColor: "#0f172a",
                color: "#e2e8f0",
                border: "1px solid #475569",
                borderRadius: "6px",
                fontSize: "1rem",
                appearance: "none",
              }}
            >
              {Object.entries(ROLE_LABELS).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </div>
"""

code = code.replace(
    '</select>\n          </div>\n\n          <div style={{ marginBottom: "1.25rem" }}>\n            <label',
    '</select>\n          </div>\n' + role_field + '\n          <div style={{ marginBottom: "1.25rem" }}>\n            <label'
)

with open('frontend/src/components/StationLogin.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
