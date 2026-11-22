/* Test de base : faire clignoter une LED (question 4 du cahier des charges). */
const int LED_PIN = 13;        // LED intégrée de l'Arduino Uno

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
