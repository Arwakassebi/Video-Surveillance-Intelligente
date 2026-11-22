/*
 * Capture JPEG avec ArduCAM (OV5642) et envoi au PC par USB (port série).
 *
 * - Chaque image JPEG est envoyée telle quelle (octets bruts) ; le script Python
 *   retrouve les images grâce aux marqueurs JPEG FFD8 (début) / FFD9 (fin).
 * - Ne rien afficher avec Serial.print() : cela polluerait le flux binaire.
 *
 * Prérequis : bibliothèque ArduCAM installée, et dans son fichier memorysaver.h
 * la ligne correspondant à votre module décommentée (ex. OV5642_MINI_5MP_PLUS).
 */
#include <Wire.h>
#include <SPI.h>
#include <ArduCAM.h>
#include "memorysaver.h"

#define CS_PIN 10
ArduCAM myCAM(OV5642, CS_PIN);

void errorBlink() {            // erreur matérielle : la LED clignote vite
  pinMode(LED_BUILTIN, OUTPUT);
  while (true) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    delay(150);
  }
}

void setup() {
  Serial.begin(115200);        // doit être identique à --baud côté Python
  Wire.begin();

  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);
  SPI.begin();

  // Réinitialisation du CPLD de la caméra
  myCAM.write_reg(0x07, 0x80);
  delay(100);
  myCAM.write_reg(0x07, 0x00);
  delay(100);

  // Test de la liaison SPI
  myCAM.write_reg(ARDUCHIP_TEST1, 0x55);
  if (myCAM.read_reg(ARDUCHIP_TEST1) != 0x55) {
    errorBlink();
  }

  myCAM.set_format(JPEG);
  myCAM.InitCAM();
  // Résolutions possibles : OV5642_320x240, OV5642_640x480, OV5642_1024x768...
  // Plus la résolution est haute, plus la reconnaissance faciale est fiable,
  // mais plus le transfert série est lent.
  myCAM.OV5642_set_JPEG_size(OV5642_320x240);
  delay(1000);
  myCAM.clear_fifo_flag();
}

void loop() {
  myCAM.flush_fifo();
  myCAM.clear_fifo_flag();
  myCAM.start_capture();

  while (!myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK)) { }  // attendre la fin de capture

  uint32_t length = myCAM.read_fifo_length();
  if (length > 0 && length < 0x7FFFF) {                     // taille valide du FIFO
    myCAM.CS_LOW();
    myCAM.set_fifo_burst();
    for (uint32_t i = 0; i < length; i++) {
      Serial.write(SPI.transfer(0x00));
    }
    myCAM.CS_HIGH();
  }
  myCAM.clear_fifo_flag();

  delay(1000);                 // une image par seconde
}
