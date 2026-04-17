# accelTest – Z-axis only test sketch

Tests the **Z-axis** from analog GPIO 35 and prints every reading to the Serial Monitor.

- **Input:** Analog pin **GPIO 35** (0..3.3V → 0..4095).
- **Serial:** 115200 baud. Open **Tools → Serial Monitor** after upload.

**Output per reading:**
- `[DEBUG] Raw Z=` – raw ADC value (0..4095)
- `[DEBUG] Volts Z=` – voltage (0..3.3 V)
- `[DEBUG] g_z=` – normalized -1..+1 (2048 = 0)
- `[DEBUG] Angle (Z)=` – tilt from Z in degrees (-90°..+90°)
- `[RESULT] Z raw= ... g_z= ... angle_deg= ...` – one-line summary

No I2C or ADXL345; only the Z-axis on pin 35 is read.
