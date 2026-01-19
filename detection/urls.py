from django.urls import path
from . import views

urlpatterns = [
    # Home / upload page
    path('', views.upload_image, name='upload_image'),

    # Webcam test page
    path('webcam/', views.webcam_page, name='webcam_page'),

    # Webcam video feed (placeholder for cloud)
    path('video-feed/', views.webcam_feed, name='webcam_feed'),
]
