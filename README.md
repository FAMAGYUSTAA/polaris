# POLARIS: Integrated Polar Expedition Logistics & Asset Management System

An offline-first, mission-critical logistics, personnel tracking, and expedition asset management platform designed for Antarctic and Arctic research stations (Bharati, Maitri, Himadri) and NCPOR Headquarters (Goa).

---

## 1. Project Directory Structure

```text
POLARIS/
├── backend/
│   ├── main.py                     # FastAPI application entrypoint & API routes
│   ├── models.py                   # SQLAlchemy ORM models (SQLite)
│   ├── schemas.py                  # Pydantic validation schemas
│   ├── crud.py                     # Database CRUD operations
│   ├── auth.py                     # Password hashing & JWT token management
│   ├── dependencies.py             # FastAPI authentication & role dependencies
│   ├── permissions.py              # Role-based access control & sync authorization
│   ├── sync_engine.py              # Delta sync processing & event ingestion
│   ├── database.py                 # SQLite engine & session management
│   ├── stations.py                 # Station registries & metadata
│   ├── requirements.txt            # Python dependencies
│   ├── polar_station.db            # Local SQLite database
│   └── tests & utilities           # Backend test suites & diagnostic scripts
│
├── frontend/
│   ├── src/                        # Station Dashboard React source code
│   │   ├── components/             # Operational panels (Cargo, Inventory, Personnel, etc.)
│   │   ├── db/                     # Dexie.js offline IndexedDB layer
│   │   ├── services/               # Sync engine, outbox handlers, auth service
│   │   ├── App.jsx                 # Main application component
│   │   └── permissions.js          # Client-side permission matrices
│   ├── public/                     # Static assets, logos & branding
│   ├── package.json                # Station frontend npm configuration
│   ├── package-lock.json           # Locked npm dependencies
│   ├── vite.config.js              # Vite server & PWA service worker configuration (Port 5173)
│   └── index.html                  # Station Dashboard HTML entrypoint
│
├── polar-hq-dashboard/
│   ├── src/                        # HQ Dashboard React source code
│   │   ├── components/             # Command center panels (Cargo Approval, Directives, etc.)
│   │   ├── services/               # Online HQ authentication & API client
│   │   └── App.jsx                 # HQ Dashboard root component
│   ├── public/                     # HQ static assets
│   ├── package.json                # HQ frontend npm configuration
│   ├── package-lock.json           # Locked npm dependencies
│   ├── vite.config.js              # Vite configuration (Port 5174)
│   └── index.html                  # HQ Dashboard HTML entrypoint
│
├── .gitignore                      # Git exclusion rules
└── README.md                       # System documentation & startup guide
```

---

## 2. Port Allocation & Architecture

| Component | Technology | Default Port | Description |
| :--- | :--- | :--- | :--- |
| **Backend API** | FastAPI / SQLAlchemy / SQLite | `8000` | REST API, Delta Sync Engine, JWT Auth, Station Isolation |
| **Station Dashboard** | React / Vite / Dexie.js | `5173` | Offline-first Station PWA with local IndexedDB & Outbox |
| **HQ Dashboard** | React / Vite | `5174` | Online Command Center for NCPOR Headquarters |

---

## 3. Quickstart & Launch Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

---

### Step 1: Start the Backend Server

Open a terminal at the project root:

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Verify backend health at: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)  
Interactive API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Step 2: Start the Station Dashboard (PWA)

Open a second terminal at the project root:

```bash
cd frontend
npm install
npm run dev
```

Access the Station Dashboard at: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

### Step 3: Start the HQ Command Center Dashboard

Open a third terminal at the project root:

```bash
cd polar-hq-dashboard
npm install
npm run dev
```

Access the HQ Dashboard at: [http://127.0.0.1:5174](http://127.0.0.1:5174)

---

## 4. Test Accounts & Default Credentials

### Headquarters (HQ)
- **Role:** HQ Operator / Command Center
- **Username:** `hq_operator`
- **Password:** `hq_password`

### Station: Bharati
- **Station Leader:** `bharati_leader` / `bharati_password`
- **Logistics & Engineering Officer:** `bharati_logistics` / `bharati_password`
- **Chief Scientist:** `bharati_scientist` / `bharati_password`
- **Medical Officer:** `bharati_medical` / `bharati_password`
- **Field Team Member:** `bharati_field` / `bharati_password`

### Station: Maitri
- **Station Leader:** `maitri_leader` / `maitri_password`
- **Logistics Officer:** `maitri_logistics` / `maitri_password`
- *(Use station suffix `_leader`, `_logistics`, `_scientist`, `_medical`, `_field` with password `<station>_password`)*

### Station: Himadri
- **Station Leader:** `himadri_leader` / `himadri_password`
- **Logistics Officer:** `himadri_logistics` / `himadri_password`

---

## 5. Offline-First Architecture & Synchronization

1. **Local-First Writes:** All operational actions on the Station Dashboard write immediately to client IndexedDB via Dexie.js. The station functions seamlessly even when completely air-gapped from the internet.
2. **Outbox Event Sourcing:** When mutations occur offline, events are stored in the local `outboxEvents` table with `sync_status: "PENDING"`.
3. **Satellite Synchronization:** When connectivity is established, clicking **"Force Sync via Satellite"** flushes pending outbox events to `/api/sync/delta`. The backend processes events through idempotent ledger validation (`SyncLedger`).
4. **Sneakernet Fallback:** For prolonged blackouts, the Station Dashboard allows exporting encrypted/hashed sync payloads to physical storage (USB) and importing at HQ or another station.

---

## 6. Running Tests

### Backend Unit & Integration Tests
```bash
cd backend
python test_sync.py
python test_multi_station.py
python test_sync_auth.py
python test_browser_scenarios.py
```

### Station Frontend Tests
```bash
cd frontend
node test_permissions.js
```
