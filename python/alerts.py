"""Envoi d'alertes par e-mail. Les identifiants sont lus dans les variables d'environnement (.env)."""
import mimetypes
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def send_email_alert(subject: str, body: str, image_path: str | None = None) -> bool:
    """Envoie un e-mail (avec image en pièce jointe). Renvoie True si l'envoi a réussi."""
    sender = os.getenv("EMAIL_FROM")
    password = os.getenv("EMAIL_PASSWORD")      # mot de passe d'application Gmail
    recipient = os.getenv("EMAIL_TO")
    if not (sender and password and recipient):
        print("[alerte] EMAIL_FROM / EMAIL_PASSWORD / EMAIL_TO non définis : e-mail non envoyé.")
        return False

    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = sender, recipient, subject
    msg.set_content(body)

    if image_path:
        ctype, _ = mimetypes.guess_type(image_path)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        with open(image_path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype,
                               filename=os.path.basename(image_path))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("[alerte] E-mail envoyé.")
        return True
    except Exception as exc:
        print(f"[alerte] Échec de l'envoi : {exc}")
        return False
