# =======================
# LAZY GLOBALS
# =======================

_helmet_model = None
_plate_model = None
_vehicle_model = None
_reader = None


# =======================
# MODEL LOADERS
# =======================

def get_vehicle_model():
    global _vehicle_model
    if _vehicle_model is None:
        from ultralytics import YOLO
        _vehicle_model = YOLO("yolov8n.pt")
    return _vehicle_model


def get_helmet_model():
    global _helmet_model
    if _helmet_model is None:
        from ultralytics import YOLO
        _helmet_model = YOLO("helmet.pt")
    return _helmet_model


def get_plate_model():
    global _plate_model
    if _plate_model is None:
        from ultralytics import YOLO
        _plate_model = YOLO("plate.pt")
    return _plate_model


def get_ocr_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader


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
    model = get_vehicle_model()
    res = model(image, conf=0.35)[0]

    persons, bikes = [], []

    for box in res.boxes:
        label = model.names[int(box.cls[0])]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "person":
            persons.append((x1, y1, x2, y2))
        elif label == "motorcycle":
            bikes.append((x1, y1, x2, y2))

    return persons, bikes


# =======================
# NO HELMET DETECTION
# =======================
def detect_nohelmet_boxes(image):
    model = get_helmet_model()
    res = model(image, conf=0.35)[0]

    nohelmets = []

    for box in res.boxes:
        label = model.names[int(box.cls[0])].lower()
        if "nohelmet" in label:
            nohelmets.append(tuple(map(int, box.xyxy[0])))

    return nohelmets


# =======================
# PLATE + OCR
# =======================
def detect_plate_and_ocr(bike_crop):
    model = get_plate_model()
    reader = get_ocr_reader()

    res = model(bike_crop, conf=0.4)[0]

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
