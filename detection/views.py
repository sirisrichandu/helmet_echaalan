import os
import cv2
from django.shortcuts import render
from django.conf import settings
from django.core.files.base import ContentFile

from .models import Violation
from vehicles.models import Vehicle

DEFAULT_LOCATION = {
    "name": "Bhimavaram",
    "lat": 16.5449,
    "lng": 81.5212
}

def upload_image(request):
    # ---------- SAFE GET ----------
    if request.method == "GET":
        return render(request, "detection/upload.html")

    # ---------- POST → AI ----------
    if request.method == "POST":
        image = request.FILES.get("media")
        if not image:
            return render(request, "detection/upload.html", {
                "error": "Please upload an image"
            })

        # 🔥 LAZY IMPORT (VERY IMPORTANT)
        from .utils import (
            detect_persons_and_bikes,
            detect_nohelmet_boxes,
            detect_plate_and_ocr,
            overlap,
        )

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp.jpg")

        with open(temp_path, "wb+") as f:
            for chunk in image.chunks():
                f.write(chunk)

        img = cv2.imread(temp_path)

        persons, bikes = detect_persons_and_bikes(img)
        nohelmets = detect_nohelmet_boxes(img)

        violations = []
        used_persons = set()

        for p in persons:
            for nh in nohelmets:
                if overlap(p, nh) and p not in used_persons:
                    used_persons.add(p)

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

                    for b in bikes:
                        if overlap(p, b):
                            bx1, by1, bx2, by2 = b
                            bike_crop = img[by1:by2, bx1:bx2]

                            plate = detect_plate_and_ocr(bike_crop)
                            if plate:
                                violation.vehicle_number = plate["text"]
                                violation.confidence = plate["confidence"]

                                plate_dir = os.path.join(settings.MEDIA_ROOT, "plates")
                                os.makedirs(plate_dir, exist_ok=True)

                                plate_path = os.path.join(
                                    plate_dir, f"{violation.id}.jpg"
                                )
                                cv2.imwrite(plate_path, plate["img"])
                                violation.plate_image = f"plates/{violation.id}.jpg"

                                try:
                                    vehicle = Vehicle.objects.get(
                                        vehicle_number__iexact=violation.vehicle_number.strip()
                                    )
                                    violation.vehicle = vehicle
                                except Vehicle.DoesNotExist:
                                    pass
                            break

                    violation.save()
                    violations.append(violation)
                    break

        return render(request, "detection/result.html", {
            "violations": violations,
            "uploaded_image": "/media/temp.jpg",
            "location": DEFAULT_LOCATION
        })
