# Vidéosurveillance intelligente — Arduino + ArduCAM + YOLOv5

> Projet de la **Semaine Système** (3–10 mars 2025) — ENIT, 1ʳᵉ année Télécom
> Réalisé par Arwa Kassebi et son groupe

Un système de vidéosurveillance low-cost : une caméra **ArduCAM** pilotée par un **Arduino** envoie des images au **PC** par USB ; un script **Python** détecte les personnes avec **YOLOv5**, peut vérifier si elles figurent dans une **base de visages connus**, enregistre les images et **envoie une alerte e-mail** en cas d'intrusion.

```
ArduCAM (OV5642) ──SPI──► Arduino ──USB (série, JPEG)──► PC
                                                         │
                          réception JPEG → YOLOv5 (personnes) → [reconnaissance faciale]
                                                         │
                                  images enregistrées  +  e-mail d'alerte avec photo
```

## Fonctionnalités

- Capture JPEG par l'ArduCAM (1 image/s, résolution réglable) et transmission série
- Reconstitution des images côté PC (marqueurs JPEG, robuste aux octets perdus)
- Détection de personnes en temps réel (YOLOv5s, classe « personne »)
- Reconnaissance faciale optionnelle (`--faces`) : alerte uniquement pour les visages **inconnus**
- Alerte e-mail avec image jointe, avec délai anti-spam (`--cooldown`)
- Analyse d'une vidéo existante (`--video`) pour tester sans matériel

## Structure

```
├── arduino/
│   ├── arducam_capture/arducam_capture.ino   # capture + envoi série
│   └── led_blink/led_blink.ino               # test de base (LED)
├── python/
│   ├── main.py             # programme principal (CLI)
│   ├── serial_receiver.py  # lecture série → images
│   ├── detector.py         # YOLOv5 : détection de personnes
│   ├── faces.py            # base de visages + identification
│   └── alerts.py           # envoi d'e-mails
├── tests/                  # test du parseur JPEG (sans matériel)
├── known_faces/            # photos des personnes autorisées (non versionnées)
├── .env.example            # modèle de configuration e-mail
└── requirements.txt
```

## Matériel

Arduino Uno, module ArduCAM (OV5642 5 MP), câbles de connexion, câble USB, PC.

Câblage (Arduino Uno) :

| ArduCAM | Arduino Uno |
|---|---|
| CS | D10 |
| MOSI | D11 |
| MISO | D12 |
| SCK | D13 |
| SDA | A4 |
| SCL | A5 |
| VCC / GND | 5 V / GND |

## Installation

### 1. Arduino
1. Installer l'IDE Arduino et la bibliothèque **ArduCAM**.
2. Dans le fichier `memorysaver.h` de la bibliothèque, décommenter la ligne de **votre** module (ex. `OV5642_MINI_5MP_PLUS`).
3. Ouvrir `arduino/arducam_capture/arducam_capture.ino`, téléverser sur la carte, puis **fermer le moniteur série** (il bloquerait le port pour Python).

> Si la LED intégrée clignote rapidement, la liaison SPI avec la caméra a échoué : vérifier le câblage.

### 2. Python (3.10 ou plus)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```
La reconnaissance faciale demande en plus `pip install face_recognition` (nécessite CMake et dlib).

### 3. Alertes e-mail
Copier `.env.example` en `.env` et renseigner l'adresse d'envoi, un **mot de passe d'application Gmail** et le destinataire. Sans ces variables, la détection fonctionne mais aucun e-mail n'est envoyé.

## Utilisation

```bash
cd python

# Flux en direct depuis l'Arduino (Windows : COM3 ; Linux : /dev/ttyACM0 ; macOS : /dev/cu.usbmodem*)
python main.py --port COM3

# Avec reconnaissance faciale : alerte seulement pour les visages absents de known_faces/
python main.py --port COM3 --faces

# Tester sur une vidéo, sans matériel
python main.py --video ma_video.mp4 --every 10
```

Options utiles : `--save-all` (enregistrer toutes les images), `--conf 0.5` (seuil YOLO), `--cooldown 120`, `--no-display`. Les images d'alerte sont dans `captures/alertes/`. Touche **q** pour quitter.

Test du parseur (sans matériel) : `python -m unittest discover -s tests`

## Limites

- À 320×240, les visages sont petits : la reconnaissance faciale est plus fiable en 640×480 (voir le commentaire dans le `.ino`), au prix d'un transfert plus lent (115200 bauds).
- Une personne de dos ou au visage non visible est considérée comme « inconnue » avec `--faces`.

## Sécurité et vie privée

- Ne jamais publier `.env` (mot de passe e-mail) ni les photos de `known_faces/` : ils sont dans `.gitignore`.
- Les images et vidéos capturées peuvent contenir des personnes identifiables : ne pas les versionner.

## Licence

MIT — voir [LICENSE](LICENSE).
