import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    '<HeaderStatus\n        isOnline={isOnline}\n        pendingCount={pendingCount}\n        lastSyncResult={lastSyncResult}\n        onForceSync={handleForceSync}\n      />',
    '<HeaderStatus\n        isOnline={isOnline}\n        pendingCount={pendingCount}\n        lastSyncResult={lastSyncResult}\n        onForceSync={handleForceSync}\n        session={session}\n      />'
)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

with open('frontend/src/components/HeaderStatus.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'import React from "react";',
    'import React from "react";\nimport { hasPermission, PERMISSIONS } from "../permissions.js";'
)

code = code.replace(
    'export default function HeaderStatus({ isOnline, pendingCount, lastSyncResult, onForceSync }) {',
    'export default function HeaderStatus({ isOnline, pendingCount, lastSyncResult, onForceSync, session }) {'
)

# Hide Force Sync via Satellite button for users without DATA_SYNC
sync_btn_orig = """        <div className="sync-actions">
          <button 
            className="btn-sync" 
            onClick={onForceSync} 
            disabled={!isOnline}
            title={!isOnline ? "Reconnect to satellite link to sync" : "Force sync now"}
          >
            Force Sync via Satellite
          </button>
          {!isOnline && (
            <div className="sync-note">Reconnect to satellite link to sync</div>
          )}
        </div>"""

sync_btn_new = """        {hasPermission(session.role, PERMISSIONS.DATA_SYNC) && (
          <div className="sync-actions">
            <button 
              className="btn-sync" 
              onClick={onForceSync} 
              disabled={!isOnline}
              title={!isOnline ? "Reconnect to satellite link to sync" : "Force sync now"}
            >
              Force Sync via Satellite
            </button>
            {!isOnline && (
              <div className="sync-note">Reconnect to satellite link to sync</div>
            )}
          </div>
        )}"""

code = code.replace(sync_btn_orig, sync_btn_new)

with open('frontend/src/components/HeaderStatus.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
