"""Vidéosurveillance intelligente : détection de personnes (+ reconnaissance de visages) et alertes e-mail.

Exemples :
    python main.py --port COM3                      # flux en direct depuis l'Arduino (Windows)
    python main.py --port /dev/ttyACM0 --faces      # + reconnaissance : alerte seulement si inconnu
    python main.py --video chemin/video.mp4         # analyse d'une vidéo
"""
import argparse
import os
import time
from datetime import datetime

import cv2

from alerts import send_email_alert
from detector import PersonDetector, draw_boxes


def video_frames(path: str, every: int):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise SystemExit(f"Impossible d'ouvrir la vidéo : {path}")
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % every == 0:
            yield frame
        i += 1
    cap.release()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--port", help="port série de l'Arduino (ex. COM3 ou /dev/ttyACM0)")
    src.add_argument("--video", help="chemin d'un fichier vidéo à analyser")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--faces", action="store_true", help="activer la reconnaissance (alerte si visage inconnu)")
    p.add_argument("--faces-dir", default="known_faces")
    p.add_argument("--every", type=int, default=10, help="vidéo : analyser 1 image sur N")
    p.add_argument("--conf", type=float, default=0.4, help="seuil de confiance YOLO")
    p.add_argument("--cooldown", type=int, default=60, help="secondes minimum entre deux e-mails")
    p.add_argument("--save-dir", default="captures", help="dossier des images enregistrées")
    p.add_argument("--save-all", action="store_true", help="enregistrer toutes les images reçues")
    p.add_argument("--no-display", action="store_true", help="ne pas ouvrir de fenêtre")
    args = p.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    alerts_dir = os.path.join(args.save_dir, "alertes")
    os.makedirs(alerts_dir, exist_ok=True)

    detector = PersonDetector(conf=args.conf)
    db = {}
    if args.faces:
        import faces
        db = faces.build_database(args.faces_dir)
        print(f"Base de visages : {len(db)} personne(s) -> {', '.join(db) or 'aucune'}")

    if args.port:
        from serial_receiver import frames_from_serial
        frames = frames_from_serial(args.port, args.baud)
    else:
        frames = video_frames(args.video, args.every)

    last_alert = 0.0
    for frame in frames:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        if args.save_all:
            cv2.imwrite(os.path.join(args.save_dir, f"{stamp}.jpg"), frame)

        boxes = detector.detect(frame)
        labels, intruders = [], 0
        for (x1, y1, x2, y2, conf) in boxes:
            if args.faces:
                import faces
                name = faces.identify(frame[max(y1, 0):y2, max(x1, 0):x2], db)
                labels.append(f"{name} {conf:.2f}")
                intruders += name == faces.UNKNOWN
            else:
                labels.append(f"Personne {conf:.2f}")
                intruders += 1
        draw_boxes(frame, boxes, labels)

        if intruders and time.time() - last_alert > args.cooldown:
            path = os.path.join(alerts_dir, f"intrusion_{stamp}.jpg")
            cv2.imwrite(path, frame)
            print(f"[{stamp}] Intrusion : {intruders} personne(s) non autorisée(s)")
            send_email_alert("Alerte : intrusion détectée",
                             f"{intruders} personne(s) non autorisée(s) détectée(s). Image jointe.", path)
            last_alert = time.time()

        if not args.no_display:
            cv2.imshow("Videosurveillance (q pour quitter)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
