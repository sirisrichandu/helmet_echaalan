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
from .utils import detect_bikes, detect_helmet_violation, detect_plates_and_ocr
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

    # Save uploaded image
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp.jpg")
    with open(temp_path, "wb+") as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    uploaded_image_url = "/media/temp.jpg"

    img = cv2.imread(temp_path)
    output = img.copy()

    # 🔴 Helmet detection ON FULL IMAGE (CRITICAL FIX)
    violation_found = detect_helmet_violation(temp_path)

    bikes = detect_bikes(img)
    violations = []

    for (x1, y1, x2, y2) in bikes:

        if violation_found:
            # 🔴 RED BOX
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(output, "NO HELMET", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

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

            # 🔍 Plate detection ONLY on violation
            plates = detect_plates_and_ocr(temp_path)
            if plates:
                best = plates[0]
                violation.vehicle_number = best["text"]
                violation.confidence = best["confidence"]

                plate_dir = os.path.join(settings.MEDIA_ROOT, "plates")
                os.makedirs(plate_dir, exist_ok=True)
                plate_path = os.path.join(plate_dir, f"{violation.id}.jpg")
                cv2.imwrite(plate_path, best["img"])
                violation.plate_image = f"plates/{violation.id}.jpg"

                try:
                    violation.vehicle = Vehicle.objects.get(
                        vehicle_number=violation.vehicle_number
                    )
                except Vehicle.DoesNotExist:
                    pass

            violation.save()
            violations.append(violation)

        else:
            # 🟢 GREEN BOX
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(output, "HELMET", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Save annotated output
    ann_dir = os.path.join(settings.MEDIA_ROOT, "annotated")
    os.makedirs(ann_dir, exist_ok=True)
    ann_path = os.path.join(ann_dir, "result.jpg")
    cv2.imwrite(ann_path, output)

    return render(request, "detection/result.html", {
        "violations": violations,
        "uploaded_image": uploaded_image_url,
        "annotated_image": "/media/annotated/result.jpg",
        "location": DEFAULT_LOCATION
    })


# Webcam placeholders
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
