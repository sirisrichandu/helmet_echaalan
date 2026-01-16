import os
import cv2
import easyocr
from ultralytics import YOLO
from django.conf import settings

# =======================
# MODELS
# =======================
person_bike_model = YOLO("yolov8n.pt")  # COCO
helmet_model = YOLO(os.path.join(settings.BASE_DIR, "detection/yolo/helmet.pt"))
plate_model = YOLO(os.path.join(settings.BASE_DIR, "detection/yolo/plate.pt"))

reader = easyocr.Reader(['en'], gpu=False)


# =======================
# HELPER
# =======================
def overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)


# =======================
# DETECT PERSONS & BIKES
# =======================
def detect_persons_and_bikes(image):
    res = person_bike_model(image, conf=0.35)[0]
    persons, bikes = [], []

    for box in res.boxes:
        label = person_bike_model.names[int(box.cls[0])]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "person":
            persons.append((x1, y1, x2, y2))
        elif label == "motorcycle":
            bikes.append((x1, y1, x2, y2))

    return persons, bikes


# =======================
# NO HELMET DETECTION (FULL IMAGE)
# =======================
def detect_nohelmet_boxes(image):
    res = helmet_model(image, conf=0.35)[0]
    nohelmets = []

    for box in res.boxes:
        label = helmet_model.names[int(box.cls[0])].lower()
        if "nohelmet" in label:
            nohelmets.append(tuple(map(int, box.xyxy[0])))

    return nohelmets


# =======================
# PLATE + OCR (IMPROVED)
# =======================
def detect_plate_and_ocr(bike_crop):
    res = plate_model(bike_crop, conf=0.4)[0]

    best = None
    best_conf = 0

    for box in res.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        plate = bike_crop[y1:y2, x1:x2]

        if plate.size == 0:
            continue

        ocr = reader.readtext(
            plate,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            detail=1
        )

        for txt in ocr:
            text = txt[1].replace(" ", "")
            conf = round(txt[2] * 100, 2)

            if conf > best_conf and len(text) >= 6:
                best_conf = conf
                best = {
                    "text": text,
                    "confidence": conf,
                    "img": plate
                }

    return best