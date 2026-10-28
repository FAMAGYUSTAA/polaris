import fs from 'fs';
const filepath = 'frontend/src/services/syncService.js';
let content = fs.readFileSync(filepath, 'utf8');
content += `

export async function syncCargoFromServer(stationId = "BHARATI") {
  const resp = await fetch(\`/api/cargo?station_id=\${stationId}\`);
  if (!resp.ok) {
    throw new Error(\`Failed to fetch cargo: HTTP \${resp.status}\`);
  }
  const items = await resp.json();
  await db.cargoShipments.bulkPut(items);
}
`;
fs.writeFileSync(filepath, content);
console.log("Added syncCargoFromServer");
