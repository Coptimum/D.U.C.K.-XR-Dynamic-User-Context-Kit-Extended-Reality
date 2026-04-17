/*
 * D.U.C.K ESP32 Posture Sensor
 * Reads analog posture sensor (e.g. flex on Z_PIN), supports calibration,
 * outputs POSTURE,... over USB Serial and BLE notify (same line format).
 * Vibe only after 9 s consecutive bad posture; device turns off after 30 s consecutive bad posture.
 *
 * BLE: NimBLE library (NimBLE-Arduino). Host PC uses telemetry/posture-ble/ (bleak); UUIDs below
 * must match that Python code.
 */

#include <NimBLEDevice.h>

#define Z_PIN        35   // Analog input (e.g. flex sensor with voltage divider)
#define VIBE_PIN     25   // Vibration motor
#define BAUD         115200

// ----- BLE (GATT notify; no Wi-Fi) -----
// Human-readable name in scan results (PC can find us by name or by SERVICE UUID below).
#define BLE_DEVICE_NAME       "DUCK Posture"
// UUID = Universally Unique ID: a fixed label for "this app's BLE service" (like a doorplate).
// Advertised so PCs can spot D.U.C.K even if the OS hides BLE_DEVICE_NAME.
#define BLE_SERVICE_UUID      "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
// One GATT characteristic; NOTIFY = ESP32 pushes each POSTURE line to subscribed clients.
#define BLE_POSTURE_CHAR_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// ----- Calibration -----
#define CALIBRATION_MS       3000   // How long (ms) to sample at startup to set "good posture" baseline
#define SAMPLE_INTERVAL_MS   50     // Interval between samples during calibration

// ----- Slouch sensitivity (adjust here) -----
#define SLOUCH_THRESHOLD_RAW_PER_DEGREE  10
#define SLOUCH_THRESHOLD_DEGREES         20
#define SLOUCH_THRESHOLD  (SLOUCH_THRESHOLD_DEGREES * SLOUCH_THRESHOLD_RAW_PER_DEGREE)

#define OUTPUT_INTERVAL_MS  100

#define VIBE_ON_MS   200
#define VIBE_OFF_MS  1800
#define VIBE_AFTER_SLOUCH_MS   9000
#define TURNOFF_AFTER_SLOUCH_MS 30000
#define SMOOTH_SAMPLES  5

// "Good posture" ADC average learned at boot (CALIBRATION_MS).
static float baselineRaw = 0.0f;
static bool calibrated = false;

// Rolling buffer for less noisy readings than single analogRead().
static int smoothBuf[SMOOTH_SAMPLES];
static int smoothIdx = 0;
static int smoothCount = 0;

static NimBLEServer* bleServer = nullptr;
// Where we write UTF-8 lines; host subscribes to this UUID to receive notifies.
static NimBLECharacteristic* postureChar = nullptr;
static bool bleClientConnected = false;

// NimBLE calls these when a laptop/phone connects or drops the BLE link.
class DuckBleServerCallbacks : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer* /*pServer*/, NimBLEConnInfo& /*connInfo*/) override {
    bleClientConnected = true;
  }
  void onDisconnect(NimBLEServer* /*pServer*/, NimBLEConnInfo& /*connInfo*/, int /*reason*/) override {
    bleClientConnected = false;
    NimBLEDevice::startAdvertising();  // Become discoverable again for the next session.
  }
};

// One-time: create BLE service + notify characteristic, then start advertising packets.
static void setupBle() {
  NimBLEDevice::init(BLE_DEVICE_NAME);
  bleServer = NimBLEDevice::createServer();
  bleServer->setCallbacks(new DuckBleServerCallbacks());

  NimBLEService* svc = bleServer->createService(BLE_SERVICE_UUID);
  postureChar = svc->createCharacteristic(
      BLE_POSTURE_CHAR_UUID,
      NIMBLE_PROPERTY::NOTIFY);
  svc->start();

  NimBLEAdvertising* adv = NimBLEDevice::getAdvertising();
  adv->setName(BLE_DEVICE_NAME);
  adv->addServiceUUID(BLE_SERVICE_UUID);  // Lets scanners find us without relying on name only.
  adv->enableScanResponse(true);
  NimBLEDevice::startAdvertising();

  Serial.println("BLE: advertising as \"" BLE_DEVICE_NAME "\" (notify characteristic ready).");
}

// Host-visible line: always USB serial; BLE notify only if a client is connected (saves radio).
static void emitPostureLine(const char* line) {
  Serial.println(line);
  if (postureChar && bleClientConnected) {
    postureChar->setValue((const uint8_t*)line, strlen(line));
    postureChar->notify();
  }
}

void setup() {
  Serial.begin(BAUD);
  delay(200);

  pinMode(VIBE_PIN, OUTPUT);
  digitalWrite(VIBE_PIN, LOW);

  analogReadResolution(12);              // 0..4095 typical for ESP32 ADC
  analogSetPinAttenuation(Z_PIN, ADC_11db);  // Full-scale ~3.3 V on GPIO35
  delay(200);

  Serial.println("\n--- D.U.C.K Posture Sensor ---");
  Serial.print("Reset reason: ");
  Serial.println(esp_reset_reason());

  // User must hold neutral posture here; baseline is the reference for "slouched" later.
  Serial.println("Calibrating: hold good posture...");
  unsigned long t0 = millis();
  unsigned long sum = 0;
  int n = 0;
  while (millis() - t0 < CALIBRATION_MS) {
    int raw = analogRead(Z_PIN);
    sum += raw;
    n++;
    delay(SAMPLE_INTERVAL_MS);
  }
  baselineRaw = (n > 0) ? (sum / (float)n) : 2048.0f;
  calibrated = true;
  Serial.print("Baseline (raw): ");
  Serial.println(baselineRaw, 1);
  Serial.print("Slouch threshold: ");
  Serial.print(SLOUCH_THRESHOLD_DEGREES);
  Serial.println(" deg (vibe after 9s bad, off after 30s bad).");
  Serial.println("Output: POSTURE,<state>[,<value>][,<deviation_deg>]");

  setupBle();  // After calibration so we do not advertise mid-calibration.
}

// Simple moving average over the last SMOOTH_SAMPLES ADC readings.
int readSmoothedRaw() {
  int raw = analogRead(Z_PIN);
  smoothBuf[smoothIdx] = raw;
  smoothIdx = (smoothIdx + 1) % SMOOTH_SAMPLES;
  if (smoothCount < SMOOTH_SAMPLES) smoothCount++;
  long s = 0;
  for (int i = 0; i < smoothCount; i++) s += smoothBuf[i];
  return (int)(s / smoothCount);
}

void loop() {
  static unsigned long lastPrint = 0;
  static unsigned long vibeOffAt = 0;
  static unsigned long nextVibeAllowedAt = 0;
  static bool vibeOn = false;
  static unsigned long slouchStartedAt = 0;  // Start time of current continuous slouch streak
  static bool deviceOff = false;            // Latched after TURNOFF_AFTER_SLOUCH_MS
  static char lineBuf[56];

  if (deviceOff) {
    delay(1000);
    return;
  }

  unsigned long now = millis();
  int raw = readSmoothedRaw();

  // Magnitude of tilt vs calibrated baseline (firmware "degrees" are scaled from raw ADC).
  int deviationRaw = (int)(raw - baselineRaw);
  if (deviationRaw < 0) deviationRaw = -deviationRaw;
  int deviationDeg = deviationRaw / SLOUCH_THRESHOLD_RAW_PER_DEGREE;
  bool slouched = calibrated && (deviationRaw >= SLOUCH_THRESHOLD);

  if (slouched) {
    if (slouchStartedAt == 0) slouchStartedAt = now;
    unsigned long slouchDurationMs = now - slouchStartedAt;

    if (slouchDurationMs >= TURNOFF_AFTER_SLOUCH_MS) {
      digitalWrite(VIBE_PIN, LOW);
      deviceOff = true;
      emitPostureLine("POSTURE,off,30s_bad");  // Then loop idles in deviceOff state.
      return;
    }

    // Haptics only after sustained bad posture (not on every brief dip).
    if (slouchDurationMs >= VIBE_AFTER_SLOUCH_MS) {
      if (!vibeOn && now >= nextVibeAllowedAt) {
        digitalWrite(VIBE_PIN, HIGH);
        vibeOn = true;
        vibeOffAt = now + VIBE_ON_MS;
      } else if (vibeOn && now >= vibeOffAt) {
        digitalWrite(VIBE_PIN, LOW);
        vibeOn = false;
        nextVibeAllowedAt = now + VIBE_OFF_MS;
      }
    }
  } else {
    slouchStartedAt = 0;  // Good posture resets the consecutive-slouch timer.
    digitalWrite(VIBE_PIN, LOW);
    vibeOn = false;
  }

  // Rate-limit serial/BLE so the host is not flooded faster than ~10 Hz.
  if (now - lastPrint >= OUTPUT_INTERVAL_MS) {
    lastPrint = now;
    if (slouched) {
      snprintf(lineBuf, sizeof(lineBuf), "POSTURE,slouched,%d,%d", raw, deviationDeg);
    } else {
      snprintf(lineBuf, sizeof(lineBuf), "POSTURE,good,%d", deviationDeg);
    }
    emitPostureLine(lineBuf);
  }

  delay(10);
}
