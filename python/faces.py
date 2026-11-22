"""Base de visages connus et reconnaissance (bibliothèque face_recognition, basée sur dlib).

Organisation de la base :
    known_faces/
        alice/ photo1.jpg photo2.jpg
        bob/   photo1.jpg
Un dossier par personne, plusieurs photos nettes de face par personne.
"""
import os

import face_recognition

IMAGE_EXT = (".jpg", ".jpeg", ".png")
UNKNOWN = "inconnu"


def build_database(folder: str = "known_faces") -> dict:
    """Renvoie {nom: [encodages]} à partir des photos du dossier."""
    db = {}
    if not os.path.isdir(folder):
        return db
    for name in sorted(os.listdir(folder)):
        person_dir = os.path.join(folder, name)
        if not os.path.isdir(person_dir):
            continue
        encodings = []
        for fname in os.listdir(person_dir):
            if fname.lower().endswith(IMAGE_EXT):
                image = face_recognition.load_image_file(os.path.join(person_dir, fname))
                encodings += face_recognition.face_encodings(image)
        if encodings:
            db[name] = encodings
    return db


def identify(crop_bgr, db: dict, tolerance: float = 0.6) -> str:
    """Identifie la personne visible dans l'image (recadrage d'une détection YOLO).

    Renvoie le nom si le visage est dans la base, sinon "inconnu".
    Si aucun visage n'est exploitable (de dos, trop petit, flou), renvoie "inconnu".
    """
    rgb = crop_bgr[:, :, ::-1]
    for encoding in face_recognition.face_encodings(rgb):
        for name, known in db.items():
            if any(face_recognition.compare_faces(known, encoding, tolerance)):
                return name
    return UNKNOWN
