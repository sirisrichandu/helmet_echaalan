""" import os
import cv2

from django.shortcuts import render
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import StreamingHttpResponse

from .models import Violation
from .utils import detect_helmet_violation, detect_plates_and_ocr, detect_bikes
from vehicles.models import Vehicle


DEFAULT_LOCATION = {
    "name": "Bhimavaram",
    "lat": 16.5449,
    "lng": 81.5212
}


def upload_image(request):
    if request.method == "POST":
        image = request.FILES.get("media")

        if not image:
            return render(request, "detection/upload.html", {
                "error": "Please upload an image"
            })

        return handle_image(request, image)

    return render(request, "detection/upload.html")


def handle_image(request, image_file):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp_upload.jpg")

    with open(temp_path, "wb+") as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    img = cv2.imread(temp_path)

    # 🔍 Detect all bikes
    bikes = detect_bikes(img)

    violations = []

    # 🚲 Loop through each detected bike
    for (x1, y1, x2, y2) in bikes:
        bike_crop = img[y1:y2, x1:x2]
        if bike_crop.size == 0:
            continue

        # 🚨 True = NO HELMET
        violation_detected = detect_helmet_violation(bike_crop)

        if not violation_detected:
            continue  # Helmet worn → skip

        # ❌ NO HELMET → CREATE VIOLATION
        violation = Violation.objects.create(
            helmet_detected=False,
            location=DEFAULT_LOCATION["name"],
            latitude=DEFAULT_LOCATION["lat"],
            longitude=DEFAULT_LOCATION["lng"]
        )

        # Save original image
        violation.image.save(
            f"violation_{violation.id}.jpg",
            ContentFile(open(temp_path, "rb").read())
        )

        # 🔢 Plate detection + OCR (per bike)
        plates, _ = detect_plates_and_ocr(bike_crop)

        if plates:
            best = plates[0]
            violation.vehicle_number = best.get("text")
            violation.confidence = best.get("confidence")

            if best.get("img") is not None:
                plate_dir = os.path.join(settings.MEDIA_ROOT, "plates")
                os.makedirs(plate_dir, exist_ok=True)

                plate_path = os.path.join(plate_dir, f"{violation.id}.jpg")
                cv2.imwrite(plate_path, best["img"])
                violation.plate_image = f"plates/{violation.id}.jpg"

            # 🔗 Link vehicle owner if exists
            try:
                vehicle = Vehicle.objects.get(vehicle_number=violation.vehicle_number)
                violation.vehicle = vehicle
            except Vehicle.DoesNotExist:
                pass

        violation.save()
        violations.append(violation)

    # ✅ If no violations at all
    if not violations:
        return render(request, "detection/result.html", {
            "violations": [],
            "uploaded_image": "/media/temp_upload.jpg",
            "location": DEFAULT_LOCATION
        })

    # 🚘 Show all violations
    return render(request, "detection/result.html", {
        "violations": violations,
        "uploaded_image": "/media/temp_upload.jpg",
        "location": DEFAULT_LOCATION
    })


# ===============================
# Webcam placeholders (SAFE)
# ===============================
"""

import os
import cv2
from django.shortcuts import render
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import StreamingHttpResponse
from .models import Violation
from .utils import (
    detect_persons_and_bikes,
    overlap,
    extract_head,
    no_helmet_on_head,
    detect_plate_and_ocr
)
from vehicles.models import Vehicle


DEFAULT_LOCATION = {
    "name": "Bhimavaram",
    "lat": 16.5449,
    "lng": 81.5212
}


def upload_image(request):
    if request.method == "POST":
        image = request.FILES.get("media")
        if not image:
            return render(request, "detection/upload.html", {"error": "Upload image"})
        return handle_image(request, image)

    return render(request, "detection/upload.html")


def handle_image(request, image_file):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    temp_path = os.path.join(settings.MEDIA_ROOT, "temp.jpg")
    with open(temp_path, "wb+") as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    img = cv2.imread(temp_path)

    persons, bikes = detect_persons_and_bikes(img)

    # ===============================
    # ASSIGN PERSONS TO BIKES
    # ===============================
    bike_persons = {}
    for bike in bikes:
        bike_persons[bike] = []
        for person in persons:
            if overlap(person, bike):
                bike_persons[bike].append(person)

    violations = []

    # ===============================
    # CHECK EACH PERSON
    # ===============================
    for bike_box, persons_on_bike in bike_persons.items():
        bx1, by1, bx2, by2 = bike_box
        bike_crop = img[by1:by2, bx1:bx2]

        plate_data = detect_plate_and_ocr(bike_crop)

        for person in persons_on_bike:
            head = extract_head(person, img)

            if no_helmet_on_head(head):
                violation = Violation.objects.create(
                    helmet_detected=False,
                    location=DEFAULT_LOCATION["name"],
                    latitude=DEFAULT_LOCATION["lat"],
                    longitude=DEFAULT_LOCATION["lng"]
                )

                violation.image.save(
                    f"violation_{violation.id}.jpg",
                    ContentFile(open(temp_path, "rb").read())
                )

                if plate_data:
                    violation.vehicle_number = plate_data["text"]
                    violation.confidence = plate_data["confidence"]

                    plate_dir = os.path.join(settings.MEDIA_ROOT, "plates")
                    os.makedirs(plate_dir, exist_ok=True)
                    plate_path = os.path.join(plate_dir, f"{violation.id}.jpg")
                    cv2.imwrite(plate_path, plate_data["img"])
                    violation.plate_image = f"plates/{violation.id}.jpg"

                    try:
                        violation.vehicle = Vehicle.objects.get(
                            vehicle_number=plate_data["text"]
                        )
                    except Vehicle.DoesNotExist:
                        pass

                violation.save()
                violations.append(violation)

    return render(request, "detection/result.html", {
        "uploaded_image": "/media/temp.jpg",
        "violations": violations,
        "violation_count": len(violations),
        "location": DEFAULT_LOCATION
    })
# -----------------------------
# Webcam (safe placeholders)
# -----------------------------
def webcam_page(request):
    return render(request, "detection/webcam.html")


def webcam_feed(request):
    return StreamingHttpResponse(
        b"",
        content_type="multipart/x-mixed-replace; boundary=frame"
    )


def start_webcam(request):
    return webcam_page(request)


def stop_webcam(request):
    return webcam_page(request)