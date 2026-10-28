import React, { useState, useEffect } from "react";
import StationLogin from "./components/StationLogin.jsx";
import HeaderStatus from "./components/HeaderStatus.jsx";
import Sidebar from "./components/Sidebar.jsx";
import HeroBanner from "./components/HeroBanner.jsx";


import DirectivesPanel from "./components/DirectivesPanel.jsx";
import CargoTracking from "./components/CargoTracking.jsx";
import AssetInventory from "./components/AssetInventory.jsx";
import PersonnelTracker from "./components/PersonnelTracker.jsx";
import ExpeditionPlanning from "./components/ExpeditionPlanning.jsx";
import EmergencyMuster from "./components/EmergencyMuster.jsx";
import SneakernetExport from "./components/SneakernetExport.jsx";
import { isOnline as getIsOnline, initNetworkListeners, forceSyncNow } from "./services/syncService.js";
import { getOutboxPendingCount } from "./db/dexie.js";
import { liveQuery } from "dexie";
import { restoreSession, logout as authLogout } from "./services/authService.js";
import { hasPermission, hasAnyPermission, PERMISSIONS } from "./permissions.js";
import "./index.css";

export default function App() {
  const [session, setSession] = useState(null);
  const [isOnline, setIsOnline] = useState(getIsOnline());
  const [pendingCount, setPendingCount] = useState(0);
  const [lastSyncResult, setLastSyncResult] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    const restored = restoreSession();
    if (restored) {
      setSession(restored);
    }
  }, []);

  const refreshPendingCount = async () => {
    if (!session || !session.station_id) return;
    try {
      const count = await getOutboxPendingCount(session.station_id);
      setPendingCount(count);
    } catch (err) {
      console.error("[App] Failed to get pending count", err);
    }
  };

  useEffect(() => {
    if (!session || !session.station_id) return;

    const cleanupNetwork = initNetworkListeners(setIsOnline, session.station_id);
    
    const subscription = liveQuery(() => getOutboxPendingCount(session.station_id)).subscribe({
      next: (count) => setPendingCount(count),
      error: (err) => console.error("[App] liveQuery error:", err)
    });

    return () => {
      cleanupNetwork();
      subscription.unsubscribe();
    };
  }, [session]);

  const handleForceSync = async () => {
    if (!session || !session.station_id) return;
    const result = await forceSyncNow(session.station_id);
    setLastSyncResult(result);
    await refreshPendingCount();
  };

  const handleLogin = (newSession) => {
    setSession(newSession);
  };

  const handleLogout = () => {
    authLogout();
    setSession(null);
  };

  if (!session) {
    return <StationLogin onLogin={handleLogin} />;
  }

  // Determine visibility based on specific permission or overarching STATION_OVERVIEW
  const canSeeCargo = hasAnyPermission(session.role, [PERMISSIONS.CARGO_TRACKING, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeDirectives = hasAnyPermission(session.role, [PERMISSIONS.HQ_DIRECTIVES, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeInventory = hasAnyPermission(session.role, [PERMISSIONS.INVENTORY_MANAGEMENT, PERMISSIONS.STATION_OVERVIEW]);
  const canSeePersonnel = hasAnyPermission(session.role, [PERMISSIONS.PERSONNEL_MANAGEMENT, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN, PERMISSIONS.EMERGENCY_STATUS_REPORTING, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeExpeditions = hasAnyPermission(session.role, [PERMISSIONS.PLANNED_EXPEDITIONS, PERMISSIONS.FIELD_MISSION_MANAGEMENT, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeEmergency = hasAnyPermission(session.role, [PERMISSIONS.EMERGENCY_MUSTER, PERMISSIONS.EMERGENCY_MUSTER_MEDICAL, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeSync = hasAnyPermission(session.role, [PERMISSIONS.SNEAKERNET, PERMISSIONS.STATION_OVERVIEW, PERMISSIONS.DATA_SYNC]);

  return (
    <div className={`app-root ${sidebarCollapsed ? 'sidebar-collapsed' : ''} fade-in-up`}>
      <Sidebar session={session} collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      <div className="app-main-wrapper">
        <HeaderStatus
          isOnline={isOnline}
          pendingCount={pendingCount}
          lastSyncResult={lastSyncResult}
          onForceSync={handleForceSync}
          session={session}
          onLogout={handleLogout}
        />
        <main className="app-main">
          <div className="panel-stagger-1"><HeroBanner stationId={session.station_id} /></div>
          
          
          <div className="dashboard-grid">
            {canSeeDirectives && (
              <div id="directives" className="panel-container panel-stagger-3">
                <DirectivesPanel stationId={session.station_id} session={session} />
              </div>
            )}
            
            {canSeeCargo && (
              <div id="cargo" className="panel-container panel-stagger-4">
                <CargoTracking stationId={session.station_id} session={session} />
              </div>
            )}

            {canSeeInventory && (
              <div id="inventory" className="panel-container panel-stagger-5">
                <AssetInventory stationId={session.station_id} session={session} />
              </div>
            )}

            {canSeePersonnel && (
              <div id="personnel" className="panel-container panel-stagger-6">
                <PersonnelTracker stationId={session.station_id} session={session} />
              </div>
            )}

            {canSeeExpeditions && (
              <div id="expeditions" className="panel-container panel-stagger-7">
                <ExpeditionPlanning stationId={session.station_id} session={session} />
              </div>
            )}

            {canSeeEmergency && (
              <div id="emergency" className="panel-container panel-stagger-8">
                <EmergencyMuster stationId={session.station_id} session={session} />
              </div>
            )}

            {canSeeSync && (
              <div id="sync" className="panel-container panel-stagger-9">
                <SneakernetExport stationId={session.station_id} session={session} />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
