from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload_image'),
    path('webcam/', views.webcam_page, name='webcam_page'),
    path('video-feed/', views.webcam_feed, name='webcam_feed'),
]
