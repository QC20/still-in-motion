#include <EEPROM.h>

void setup() {
  // Start serial communication for debugging
  Serial.begin(9600);
  Serial.println("Starting EEPROM erase...");

  // Write a 0 to every address in the EEPROM
  for (int i = 0; i < EEPROM.length(); i++) {
    EEPROM.write(i, 0);
  }

  Serial.println("EEPROM erased! The image counter will start from 0 on next boot.");

  // Optional: Verify the erasure
  Serial.println("Verifying erasure...");
  bool erasureSuccess = true;
  for (int i = 0; i < EEPROM.length(); i++) {
    if (EEPROM.read(i) != 0) {
      Serial.print("Verification failed at address ");
      Serial.println(i);
      erasureSuccess = false;
    }
  }

  if (erasureSuccess) {
    Serial.println("Verification successful - all memory is cleared");
  }
}

void loop() {
  // Nothing to do here
}