"""Détection de personnes avec YOLOv5 (modèle pré-entraîné COCO, classe 0 = personne)."""
import cv2


class PersonDetector:
    def __init__(self, weights: str = "yolov5s", conf: float = 0.4):
        import torch  # import tardif : lourd

        self.model = torch.hub.load("ultralytics/yolov5", weights)
        self.model.conf = conf
        self.model.classes = [0]          # ne garder que les personnes

    def detect(self, frame_bgr):
        """Renvoie une liste de (x1, y1, x2, y2, confiance) pour chaque personne détectée."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rows = self.model(rgb).xyxy[0].cpu().numpy()
        return [(int(x1), int(y1), int(x2), int(y2), float(conf))
                for x1, y1, x2, y2, conf, _cls in rows]


def draw_boxes(frame, boxes, labels=None, color=(0, 255, 0)):
    """Dessine les cadres (et un libellé par cadre) sur l'image."""
    for i, (x1, y1, x2, y2, conf) in enumerate(boxes):
        label = labels[i] if labels else f"Personne {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, max(y1 - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
