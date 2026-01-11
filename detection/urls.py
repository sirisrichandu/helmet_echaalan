from django.urls import path
from .views import upload_image,webcam_page,webcam_feed,start_webcam,stop_webcam

urlpatterns = [
    path('upload/', upload_image, name='upload'),
    path('webcam/', webcam_page, name='webcam'),
    path('webcam-feed/', webcam_feed, name='webcam_feed'),
     path('webcam/start/', start_webcam, name='start_webcam'),
     path('webcam/stop/', stop_webcam, name='stop_webcam'),

]
