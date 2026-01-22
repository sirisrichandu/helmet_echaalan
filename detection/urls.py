

from django.urls import path
from .views import upload_image, webcam_page, webcam_feed

urlpatterns = [
    path("upload/", upload_image, name="upload"),   # ✅ FIX
    path("webcam/", webcam_page, name="webcam"),
    path("webcam/feed/", webcam_feed, name="webcam_feed"),
]