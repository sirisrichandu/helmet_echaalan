import os
import cv2
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse


# =========================
# DEFAULT LOCATION
# =========================
DEFAULT_LOCATION = {
    "name": "Bhimavaram",
    "lat": 16.5449,
    "lng": 81.5212
}


# =========================
# UPLOAD + SIMPLE DETECTION
# =========================
def upload_image(request):

    if request.method == "GET":
        return render(request, "detection/upload.html")

    if request.method == "POST":
        image = request.FILES.get("media")

        if not image:
            return render(request, "detection/upload.html", {
                "error": "Please upload an image"
            })

        # Save uploaded image
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        img_path = os.path.join(settings.MEDIA_ROOT, image.name)

        with open(img_path, "wb+") as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Load image with OpenCV
        img = cv2.imread(img_path)

        # -------------------------
        # SIMPLE DEMO LOGIC
        # -------------------------
        helmet_worn = False          # Assume no helmet (demo)
        vehicle_number = "AP 39 AB 1234"   # Demo number plate
        confidence = 85

        challan_required = not helmet_worn

        return render(request, "detection/result.html", {
            "uploaded_image": settings.MEDIA_URL + image.name,
            "helmet_worn": helmet_worn,
            "vehicle_number": vehicle_number,
            "confidence": confidence,
            "challan_required": challan_required,
            "location": DEFAULT_LOCATION
        })
