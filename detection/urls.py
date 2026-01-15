from django.urls import path
from .views import upload_image, webcam_feed

urlpatterns = [
    path('upload/', upload_image, name='upload'),
    path('webcam/', webcam_feed, name='webcam'),
]