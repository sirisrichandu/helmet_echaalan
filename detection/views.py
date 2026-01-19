import os
import cv2

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse


# =========================
# DEFAULT LOCATION
# =========================

DEFAULT_LOCATION = {
    "name": "Bhimavaram",
    "lat": 16.5449,
    "lng": 81.5212
}


# =========================
# WEBCAM PAGE
# =========================

def webcam_page(request):
    return HttpResponse("Webcam page working successfully ✅")


# =========================
# WEBCAM FEED (PLACEHOLDER)
# =========================

def webcam_feed(request):
    return StreamingHttpResponse(
        b"Webcam feed is disabled on server",
        content_type="text/plain"
    )


# =========================
# IMAGE UPLOAD (DEBUG SAFE)
# =========================

def upload_image(request):
    # ---------- GET ----------
    if request.method == "GET":
        return render(request, "detection/upload.html")

    # ---------- POST (DEBUG TEST) ----------
    if request.method == "POST":
        return HttpResponse(
            "POST request working ✅<br>"
            "Django setup is correct.<br>"
            "Error is inside AI / Cloudinary code."
        )
