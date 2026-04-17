/*
 * D.U.C.K – Z-axis only accelerometer test (ESP32)
 * Reads Z-axis from analog GPIO 35. No I2C / ADXL345.
 *
 * Wiring: Z-axis sensor or voltage divider on GPIO 35 (0..3.3V → 0..4095).
 */

#define BAUD    115200
#define Z_PIN   35

void setup() {
  Serial.begin(BAUD);
  delay(500);

  analogReadResolution(12);   // 0..4095
  analogSetPinAttenuation(Z_PIN, ADC_11db);
  pinMode(Z_PIN, INPUT);

  Serial.println("\n--- D.U.C.K Z-Axis Test ---");
  Serial.print("[DEBUG] Z-axis from analog pin ");
  Serial.println(Z_PIN);
  Serial.println("[DEBUG] Output: raw Z, volts, g_z, angle_deg\n");
}

void loop() {
  int rawZ = analogRead(Z_PIN);

  float volts = (rawZ / 4095.0f) * 3.3f;
  // Normalized -1..+1 (2048 = 0)
  float g_z = (rawZ - 2048.0f) / 2048.0f;
  // Tilt angle from Z: 0 raw → -90°, 2048 → 0°, 4095 → +90°
  float angle_deg = (rawZ - 2048.0f) / 2048.0f * 90.0f;

  Serial.print("[DEBUG] Raw Z=");
  Serial.println(rawZ);

  Serial.print("[DEBUG] Volts Z=");
  Serial.println(volts, 3);

  Serial.print("[DEBUG] g_z=");
  Serial.println(g_z, 3);

  Serial.print("[DEBUG] Angle (Z)=");
  Serial.print(angle_deg, 2);
  Serial.println(" deg");

  Serial.print("[RESULT] Z raw=");
  Serial.print(rawZ);
  Serial.print(" g_z=");
  Serial.print(g_z, 3);
  Serial.print(" angle_deg=");
  Serial.println(angle_deg, 2);
  Serial.println("---");

  delay(500);
}
