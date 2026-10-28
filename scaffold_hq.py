import os
import json

base_dir = r"c:\Users\acer\OneDrive\Desktop\POLAR 2\polar-hq-dashboard"
os.makedirs(os.path.join(base_dir, "src", "components"), exist_ok=True)

# 1. package.json
pkg = {
  "name": "polar-hq-dashboard",
  "private": True,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.0"
  }
}
with open(os.path.join(base_dir, "package.json"), "w") as f:
    json.dump(pkg, f, indent=2)

# 2. vite.config.js
vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
"""
with open(os.path.join(base_dir, "vite.config.js"), "w") as f:
    f.write(vite_config)

# 3. index.html
html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NCPOR HQ Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
with open(os.path.join(base_dir, "index.html"), "w") as f:
    f.write(html)

# 4. src/main.jsx
main_jsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
with open(os.path.join(base_dir, "src", "main.jsx"), "w") as f:
    f.write(main_jsx)

# 5. src/index.css
css = """
:root {
  --bg-color: #0b192c; /* HQ Deep Blue */
  --text-primary: #e0e6ed;
  --text-muted: #8c9baf;
  --accent-primary: #f6c90e; /* HQ Gold */
  --accent-secondary: #3a506b;
  --panel-bg: #112236;
  --border-color: #1a365d;
  
  --danger-color: #e63946;
  --success-color: #4caf50;
  --warning-color: #ff9800;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-primary);
}

* {
  box-sizing: border-box;
}

.hq-header {
  background-color: #08121f;
  padding: 1rem 2rem;
  border-bottom: 3px solid var(--accent-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hq-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--accent-primary);
  letter-spacing: 1px;
}

.hq-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media(max-width: 900px) {
  .hq-main {
    grid-template-columns: 1fr;
  }
}

.panel {
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.panel h2 {
  margin-top: 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
  color: var(--accent-primary);
  font-size: 1.25rem;
}

button {
  background-color: var(--accent-primary);
  color: #000;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
}

button:hover {
  opacity: 0.9;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

input, textarea, select {
  width: 100%;
  background-color: #0b192c;
  color: #fff;
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 0.25rem;
}

input:focus, textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.form-group {
  margin-bottom: 1rem;
}
"""
with open(os.path.join(base_dir, "src", "index.css"), "w") as f:
    f.write(css)

print("Scaffold created.")
