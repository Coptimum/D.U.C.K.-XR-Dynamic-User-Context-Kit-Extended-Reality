import 'dotenv/config';
import PulsoidSocket from '@pulsoid/socket';
import { WebSocket, WebSocketServer } from 'ws';

const token = process.env.PULSOID_TOKEN?.trim();
if (!token) {
  console.error('Missing PULSOID_TOKEN. Copy .env.example to .env and set your token.');
  process.exit(1);
}

const postureWsUrl = process.env.POSTURE_WS_URL?.trim() || 'ws://127.0.0.1:8765';
const fusionHost = process.env.FUSION_WS_HOST?.trim() || '127.0.0.1';
const fusionPort = Number.parseInt(process.env.FUSION_WS_PORT || '9090', 10);
const emitOnPosture = ['1', 'true', 'yes', 'on'].includes(
  String(process.env.FUSION_EMIT_ON_POSTURE || '1').toLowerCase(),
);

const wss = new WebSocketServer({ host: fusionHost, port: fusionPort });
let stopping = false;

let lastPosture = null;
let lastHr = {
  heartRate: null,
  heartMeasuredAt: null,
};

function makeMerged(type) {
  return {
    type,
    ts: new Date().toISOString(),
    heartRate: lastHr.heartRate,
    heartMeasuredAt: lastHr.heartMeasuredAt,
    posture: lastPosture,
  };
}

function broadcast(obj) {
  const blob = JSON.stringify(obj);
  for (const client of wss.clients) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(blob);
    }
  }
}

wss.on('listening', () => {
  console.log(`Fusion WS server listening on ws://${fusionHost}:${fusionPort}/`);
  console.log(`Posture input URL: ${postureWsUrl}`);
});

wss.on('connection', (client) => {
  // Give new clients immediate context so they do not wait for the next upstream tick.
  client.send(JSON.stringify(makeMerged('snapshot')));
});

let postureWs = null;
let postureRetryMs = 1000;
let postureRetryTimer = null;

function schedulePostureReconnect() {
  if (stopping) return;
  if (postureRetryTimer) return;

  postureRetryTimer = setTimeout(() => {
    postureRetryTimer = null;
    connectPostureWs();
  }, postureRetryMs);

  postureRetryMs = Math.min(postureRetryMs * 2, 15000);
}

function connectPostureWs() {
  if (stopping) return;

  try {
    postureWs = new WebSocket(postureWsUrl);
  } catch (err) {
    console.error('Posture WS create error:', err?.message ?? err);
    schedulePostureReconnect();
    return;
  }

  postureWs.on('open', () => {
    postureRetryMs = 1000;
    console.log('Connected to posture bridge WebSocket.');
  });

  postureWs.on('message', (raw) => {
    let parsed;
    try {
      parsed = JSON.parse(raw.toString('utf-8'));
    } catch {
      return;
    }

    lastPosture = parsed;
    if (emitOnPosture) {
      broadcast(makeMerged('posture'));
    }
  });

  postureWs.on('error', (err) => {
    console.error('Posture WS error:', err?.message ?? err);
  });

  postureWs.on('close', () => {
    if (!stopping) {
      console.log(`Posture WS disconnected. Reconnecting in ${postureRetryMs} ms...`);
      schedulePostureReconnect();
    }
  });
}

const pulsoidSocket = new PulsoidSocket(token);

pulsoidSocket.on('open', () => {
  console.log('Pulsoid WebSocket connected.');
});

pulsoidSocket.on('online', () => {
  console.log('Pulsoid monitor is online.');
});

pulsoidSocket.on('offline', () => {
  console.log('Pulsoid monitor is offline (~30s without data).');
});

pulsoidSocket.on('heart-rate', (data) => {
  const measuredAt = data?.measuredAt != null ? new Date(data.measuredAt).toISOString() : null;
  const heartRate = Number.isFinite(data?.heartRate) ? data.heartRate : null;

  lastHr = {
    heartRate,
    heartMeasuredAt: measuredAt,
  };

  broadcast(makeMerged('hr'));
});

pulsoidSocket.on('error', (err) => {
  console.error('Pulsoid socket error:', err?.message ?? err);
});

function shutdown() {
  if (stopping) return;
  stopping = true;

  if (postureRetryTimer) {
    clearTimeout(postureRetryTimer);
    postureRetryTimer = null;
  }

  try {
    postureWs?.close();
  } catch {
    // noop
  }

  try {
    pulsoidSocket.disconnect();
  } catch {
    // noop
  }

  wss.close(() => {
    process.exit(0);
  });

  setTimeout(() => process.exit(0), 500).unref();
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

connectPostureWs();
pulsoidSocket.connect();
console.log('Fusion service started. Press Ctrl+C to stop.');
