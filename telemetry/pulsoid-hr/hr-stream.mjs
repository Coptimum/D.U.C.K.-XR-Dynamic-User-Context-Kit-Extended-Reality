/**
 * Connects to Pulsoid real-time HR WebSocket and prints each update.
 * Requires: Pulsoid app showing live BPM (same account as the token).
 */
import 'dotenv/config';
import PulsoidSocket from '@pulsoid/socket';

const token = process.env.PULSOID_TOKEN?.trim();

if (!token) {
  console.error('Missing PULSOID_TOKEN. Copy .env.example to .env and set your token, or export the variable.');
  process.exit(1);
}

// @pulsoid/socket v1.3+ exports the class directly (no static .create()).
const socket = new PulsoidSocket(token);

socket.on('open', () => {
  console.log('WebSocket connected.');
});

socket.on('online', () => {
  console.log('Heart rate monitor is sending data.');
});

socket.on('offline', () => {
  console.log('No data from monitor for ~30s (check band / app).');
});

socket.on('heart-rate', (data) => {
  const t = data.measuredAt != null ? new Date(data.measuredAt).toISOString() : '';
  console.log(`[${t}] ${data.heartRate} BPM`);
});

socket.on('error', (err) => {
  console.error('Pulsoid socket error:', err?.message ?? err);
});

process.on('SIGINT', () => {
  socket.disconnect();
  process.exit(0);
});

socket.connect();
console.log('Pulsoid session started — wear band and keep the app on live HR. Ctrl+C to exit.');
