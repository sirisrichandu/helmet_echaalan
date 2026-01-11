import os
import cv2

from django.shortcuts import render
from django.conf import settings
from django.core.files.base import ContentFile

from .models import Violation
from .utils import detect_helmet_violation, detect_plates_and_ocr


# ===============================
# DEFAULT LOCATION
# ===============================
DEFAULT_LOCATION = {
    "name": "Bhimavaram",
    "lat": 16.5449,
    "lng": 81.5212
}


# ===============================
# UPLOAD VIEW
# ===============================
def upload_image(request):
    if request.method == "POST":
        image = request.FILES.get("media")

        if not image:
            return render(request, "detection/upload.html", {
                "error": "Please upload an image"
            })

        return handle_image(request, image)

    return render(request, "detection/upload.html")


# ===============================
# IMAGE HANDLER
# ===============================
def handle_image(request, image_file):
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp_upload.jpg")

    with open(temp_path, "wb+") as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    # 🚨 True = NO HELMET
    violation_detected = detect_helmet_violation(temp_path)

    # ===============================
    # HELMET WORN → NO DB SAVE
    # ===============================
    if not violation_detected:
        return render(request, "detection/result.html", {
            "helmet_detected": True,
            "uploaded_image": "/media/temp_upload.jpg",
            "vehicle_number": None,
            "plate_image": None,
            "confidence": None,
            "location": DEFAULT_LOCATION
        })

    # ===============================
    # NO HELMET → SAVE VIOLATION
    # ===============================
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

    # ---- PLATE + OCR ----
    plates, _ = detect_plates_and_ocr(temp_path)

    vehicle_number = None
    confidence = None
    plate_image_url = None

    if plates:
        best = plates[0]
        vehicle_number = best.get("text")
        confidence = best.get("confidence")

        if best.get("img") is not None:
            plate_dir = os.path.join(settings.MEDIA_ROOT, "plates")
            os.makedirs(plate_dir, exist_ok=True)

            plate_path = os.path.join(plate_dir, f"{violation.id}.jpg")
            cv2.imwrite(plate_path, best["img"])

            violation.plate_image = f"plates/{violation.id}.jpg"
            plate_image_url = violation.plate_image.url

        violation.vehicle_number = vehicle_number
        violation.confidence = confidence

    violation.save()

    return render(request, "detection/result.html", {
        "helmet_detected": False,
        "uploaded_image": violation.image.url,
        "vehicle_number": vehicle_number,
        "plate_image": plate_image_url,
        "confidence": confidence,
        "location": DEFAULT_LOCATION
    })
from django.http import StreamingHttpResponse

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
