import os
import cv2
import easyocr
from ultralytics import YOLO
from django.conf import settings

BASE_DIR = settings.BASE_DIR

helmet_model = YOLO(os.path.join(BASE_DIR, "detection/yolo/helmet.pt"))
plate_model = YOLO(os.path.join(BASE_DIR, "detection/yolo/plate.pt"))

reader = easyocr.Reader(['en'], gpu=False)


def detect_helmet_violation(source):
    """
    Returns:
    True  → NO HELMET detected (violation)
    False → Helmet worn (safe)
    """
    results = helmet_model(source, conf=0.5)[0]

    for box in results.boxes:
        cls = int(box.cls[0])
        label = helmet_model.names[cls].lower()

        if label == "nohelmet":
            return True   # 🚨 violation

    return False  # ✅ helmet worn


def detect_plates_and_ocr(image_path):
    img = cv2.imread(image_path)
    results = plate_model(image_path, conf=0.4)

    detections = []

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            plate_img = img[y1:y2, x1:x2]

            if plate_img.size == 0:
                continue

            ocr = reader.readtext(
                plate_img,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            )

            text, conf = None, 0
            if ocr:
                text = ocr[0][1].replace(" ", "")
                conf = round(ocr[0][2] * 100, 2)

            detections.append({
                "text": text,
                "confidence": conf,
                "img": plate_img
            })

    return detections, None
