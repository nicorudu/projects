// M4 bench step 1: confirm the dock board is an ESP32-S3 N16R8.
// Pass: 16 MB flash and 8 MB PSRAM reported.
//
// Board: ESP32S3 Dev Module, Flash Size = 16MB, PSRAM = OPI PSRAM.
// Build: arduino-cli compile -b esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi
// Serial: 115200 baud on the UART/COM port (USB CDC On Boot disabled).
//
// No GPIO is touched. GPIO35-37 belong to the octal PSRAM; never use them.

void report() {
  Serial.println();
  Serial.println("=== dock_hello ===");
  Serial.printf("chip:        %s rev %d, %d cores, %lu MHz\n",
                ESP.getChipModel(), ESP.getChipRevision(), ESP.getChipCores(),
                (unsigned long)ESP.getCpuFreqMHz());
  Serial.printf("mac:         %012llX\n", ESP.getEfuseMac());
  Serial.printf("sdk:         %s\n", ESP.getSdkVersion());
  Serial.printf("flash size:  %lu bytes (%lu MB), %lu MHz\n",
                (unsigned long)ESP.getFlashChipSize(),
                (unsigned long)(ESP.getFlashChipSize() / (1024UL * 1024UL)),
                (unsigned long)(ESP.getFlashChipSpeed() / 1000000UL));
  Serial.printf("psram found: %s\n", psramFound() ? "yes" : "no");
  Serial.printf("psram size:  %lu bytes (%.2f MB), free %lu\n",
                (unsigned long)ESP.getPsramSize(),
                ESP.getPsramSize() / (1024.0 * 1024.0),
                (unsigned long)ESP.getFreePsram());
  Serial.printf("heap:        %lu bytes, free %lu\n",
                (unsigned long)ESP.getHeapSize(), (unsigned long)ESP.getFreeHeap());

  // Prove the PSRAM is usable, not just detected: fill and check 4 MB.
  const size_t n = 4UL * 1024UL * 1024UL;
  uint8_t *p = (uint8_t *)ps_malloc(n);
  bool ok = p != nullptr;
  if (ok) {
    for (size_t i = 0; i < n; i++) p[i] = (uint8_t)(i * 31u + 7u);
    for (size_t i = 0; i < n && ok; i++) ok = p[i] == (uint8_t)(i * 31u + 7u);
    free(p);
  }
  Serial.printf("psram 4 MB write/read: %s\n", ok ? "ok" : "FAILED");

  bool flash16 = ESP.getFlashChipSize() == 16UL * 1024UL * 1024UL;
  bool psram8 = ESP.getPsramSize() >= 7UL * 1024UL * 1024UL;  // a little is reserved
  Serial.printf("RESULT: %s\n", (flash16 && psram8 && ok) ? "PASS" : "FAIL");
}

void setup() {
  Serial.begin(115200);
  delay(500);
}

void loop() {
  report();
  delay(3000);
}
