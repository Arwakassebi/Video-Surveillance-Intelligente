"""Réception des images JPEG envoyées par l'Arduino (ArduCAM) via le port série."""
import cv2
import numpy as np

SOI = b"\xff\xd8"   # Start Of Image
EOI = b"\xff\xd9"   # End Of Image
MAX_BUFFER = 2_000_000


class JpegStreamParser:
    """Reconstitue des images JPEG complètes à partir d'un flux d'octets découpé n'importe comment."""

    def __init__(self):
        self.buf = bytearray()

    def feed(self, data: bytes):
        """Ajoute des octets et renvoie la liste des JPEG complets (bytes) désormais disponibles."""
        self.buf.extend(data)
        images = []
        while True:
            start = self.buf.find(SOI)
            if start == -1:
                del self.buf[:-1]          # garder 1 octet (un SOI peut être coupé en deux)
                break
            end = self.buf.find(EOI, start + 2)
            if end == -1:
                del self.buf[:start]       # jeter ce qui précède le début de l'image
                break
            images.append(bytes(self.buf[start:end + 2]))
            del self.buf[:end + 2]
        if len(self.buf) > MAX_BUFFER:     # flux corrompu : on repart de zéro
            self.buf.clear()
        return images


def decode_jpeg(jpeg: bytes):
    """Décode un JPEG en image BGR (OpenCV). Renvoie None si l'image est corrompue."""
    arr = np.frombuffer(jpeg, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def frames_from_serial(port: str, baud: int = 115200):
    """Générateur d'images BGR lues en continu depuis le port série."""
    import serial  # pyserial, importé ici pour pouvoir tester le parseur sans matériel

    parser = JpegStreamParser()
    with serial.Serial(port, baud, timeout=1) as ser:
        ser.reset_input_buffer()
        while True:
            data = ser.read(ser.in_waiting or 1)
            for jpeg in parser.feed(data):
                frame = decode_jpeg(jpeg)
                if frame is not None:
                    yield frame
