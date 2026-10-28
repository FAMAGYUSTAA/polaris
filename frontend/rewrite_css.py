import os

css_content = """/* CSS Variables as requested */
:root {
  --navy-dark: #0F2D5B;
  --blue-primary: #2563EB;
  --blue-primary-hover: #1d4ed8;
  --blue-secondary: #E8F0F8;
  --page-bg: #F4F7FB;
  --card-bg: #FFFFFF;
  --card-border: #DCE6F0;
  
  --text-heading: #0F2D5B;
  --text-main: #334155;
  --text-secondary: #64748B;
  --text-muted: #7B8CA3;
  --white: #FFFFFF;
  
  --status-healthy: #16A34A;
  --status-warning: #D97706;
  --status-critical: #DC2626;
  
  --danger-bg: #FEF2F2;
  --danger-border: #FECACA;
  
  --divider: #E2E8F0;
  
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 70px;
}

/* Reset and Base */
*, *::before, *::after {
  box-sizing: border-box;
}

body, html {
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: var(--page-bg);
  color: var(--text-main);
  overflow-x: hidden;
}

/* Layout */
.app-root {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--navy-dark);
  color: var(--white);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.app-root.sidebar-collapsed .sidebar {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 64px;
}

.sidebar-title {
  font-weight: 600;
  font-size: 1.1rem;
  white-space: nowrap;
}

.btn-sidebar-toggle {
  background: transparent;
  border: none;
  color: var(--white);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
  border-left: 3px solid transparent;
}

.nav-item:hover, .nav-item.active {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--white);
}

.nav-item.active {
  border-left-color: var(--blue-primary);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-right: 1rem;
}

.app-root.sidebar-collapsed .nav-item {
  padding: 0.75rem;
  justify-content: center;
}

.app-root.sidebar-collapsed .nav-icon {
  margin-right: 0;
}

.app-root.sidebar-collapsed .nav-item span {
  display: none;
}

/* Main Content Wrapper */
.app-main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.app-header {
  background-color: var(--navy-dark);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  min-height: 64px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 10;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-logo {
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.header-titles {
  display: flex;
  flex-direction: column;
}

.header-titles h1 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.header-titles h2 {
  font-size: 0.75rem;
  font-weight: 400;
  margin: 0;
  opacity: 0.8;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.sync-status-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online { background-color: var(--status-healthy); }
.status-dot.offline { background-color: var(--status-critical); }

.user-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-left: 1px solid rgba(255,255,255,0.2);
  padding-left: 1.5rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  text-align: right;
}

.username {
  font-weight: 600;
  font-size: 0.9rem;
}

.user-role {
  font-size: 0.75rem;
  opacity: 0.8;
}

/* Main Area */
.app-main {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 3rem;
}

/* Hero Banner */
.hero-banner {
  position: relative;
  height: 180px;
  background-image: url('/bg-station.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  padding: 0 3rem;
  margin-bottom: 2rem;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, rgba(15, 45, 91, 0.8) 0%, rgba(15, 45, 91, 0.2) 100%);
}

.hero-content {
  position: relative;
  z-index: 1;
  color: var(--white);
}

.hero-title {
  font-size: 2.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.hero-subtitle {
  font-size: 1.25rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Dashboard Grid (Single Column as requested) */
.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0 3rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Cards / Panels */
.tracker-panel, .panel-container {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.tracker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--divider);
  padding-bottom: 1rem;
}

.tracker-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-heading);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
}

.icon-box {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--blue-secondary);
  color: var(--blue-primary);
}

.icon-box.danger {
  background-color: var(--danger-bg);
  color: var(--status-critical);
}

/* Buttons */
button {
  font-family: inherit;
  transition: all 0.2s ease;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  border-radius: 4px;
}

.btn-primary {
  background-color: var(--blue-primary);
  color: var(--white);
  border: none;
  padding: 0.5rem 1rem;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--blue-primary-hover);
}

.btn-secondary {
  background-color: var(--blue-secondary);
  color: var(--text-heading);
  border: 1px solid var(--card-border);
  padding: 0.5rem 1rem;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #d8e5f3;
}

.btn-danger {
  background-color: var(--status-critical);
  color: var(--white);
  border: none;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  font-size: 1.1rem;
}

.btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-logout {
  background: rgba(255, 255, 255, 0.1);
  color: var(--white);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.4rem 0.8rem;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Emergency Protocol */
.emergency-panel {
  background-color: var(--danger-bg);
  border-color: var(--danger-border);
}

.emergency-panel .tracker-header {
  border-bottom-color: var(--danger-border);
}

.emergency-panel h2 {
  color: var(--text-heading);
}

.emergency-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: rgba(220, 38, 38, 0.05);
  border-radius: 8px;
  border: 1px dashed var(--danger-border);
}

/* Personnel Grid */
.personnel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.personnel-col {
  background: var(--page-bg);
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid var(--card-border);
}

.personnel-col h3 {
  font-size: 1rem;
  color: var(--text-heading);
  margin-top: 0;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.personnel-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.personnel-card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.p-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.p-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--blue-secondary);
  color: var(--blue-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.p-details {
  display: flex;
  flex-direction: column;
}

.p-name {
  font-weight: 600;
  color: var(--text-heading);
  margin-bottom: 0.2rem;
}

.p-role {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.blood-type {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--status-critical);
  background: var(--danger-bg);
  border: 1px solid var(--danger-border);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

/* Cargo Rows */
.cargo-section h3 {
  font-size: 1rem;
  color: var(--text-heading);
  margin: 1.5rem 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cargo-row {
  background: var(--page-bg);
  border: 1px solid var(--card-border);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cargo-row-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cargo-title {
  font-weight: 600;
  color: var(--text-heading);
  font-size: 1.1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--white);
}

/* Animations */
.fade-in-up {
  animation: fadeInUp 0.4s ease-out forwards;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .fade-in-up {
    animation: none;
  }
  .sidebar {
    transition: none;
  }
}

.panel-stagger-1 { animation-delay: 0.05s; }
.panel-stagger-2 { animation-delay: 0.1s; }
.panel-stagger-3 { animation-delay: 0.15s; }
.panel-stagger-4 { animation-delay: 0.2s; }
.panel-stagger-5 { animation-delay: 0.25s; }
.panel-stagger-6 { animation-delay: 0.3s; }
.panel-stagger-7 { animation-delay: 0.35s; }
.panel-stagger-8 { animation-delay: 0.4s; }
.panel-stagger-9 { animation-delay: 0.45s; }

/* Dashboard Summary removal */
.dashboard-summary { display: none; }
"""

with open("src/index.css", "w", encoding="utf-8") as f:
    f.write(css_content)

print("index.css updated.")
