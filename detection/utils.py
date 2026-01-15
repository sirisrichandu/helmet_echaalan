import cv2
import os
import easyocr
from ultralytics import YOLO
from django.conf import settings

# ===============================
# LOAD MODELS (ONCE)
# ===============================
person_bike_model = YOLO("yolov8n.pt")  # COCO: person, motorcycle
helmet_model = YOLO(os.path.join(settings.BASE_DIR, "detection/yolo/helmet.pt"))
plate_model = YOLO(os.path.join(settings.BASE_DIR, "detection/yolo/plate.pt"))

reader = easyocr.Reader(['en'], gpu=False)


# ===============================
# DETECT PERSONS & BIKES
# ===============================
def detect_persons_and_bikes(image):
    results = person_bike_model(image, conf=0.35)[0]

    persons = []
    bikes = []

    for box in results.boxes:
        cls = int(box.cls[0])
        label = person_bike_model.names[cls]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "person":
            persons.append((x1, y1, x2, y2))
        elif label == "motorcycle":
            bikes.append((x1, y1, x2, y2))

    return persons, bikes


# ===============================
# BOX OVERLAP CHECK
# ===============================
def overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)


# ===============================
# HEAD EXTRACTION (CRITICAL)
# ===============================
def extract_head(person_box, image):
    x1, y1, x2, y2 = person_box
    h = y2 - y1
    return image[y1:y1 + int(0.30 * h), x1:x2]


# ===============================
# HELMET CHECK (HEAD ONLY)
# ===============================
def no_helmet_on_head(head_crop):
    if head_crop.size == 0:
        return False

    res = helmet_model(head_crop, conf=0.6)[0]

    for box in res.boxes:
        label = helmet_model.names[int(box.cls[0])].lower()
        if label == "nohelmet":
            return True

    return False


# ===============================
# PLATE + OCR (BIKE ONLY)
# ===============================
def detect_plate_and_ocr(bike_crop):
    res = plate_model(bike_crop, conf=0.4)[0]

    for box in res.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        plate_img = bike_crop[y1:y2, x1:x2]

        if plate_img.size == 0:
            continue

        ocr = reader.readtext(
            plate_img,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )

        if ocr:
            return {
                "text": ocr[0][1].replace(" ", ""),
                "confidence": round(ocr[0][2] * 100, 2),
                "img": plate_img
            }

    return None