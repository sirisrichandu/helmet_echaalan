"""
URL configuration for helmet_echaalan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("Helmet E-Challan System is Live")
urlpatterns = [
    # ❌ Do NOT expose detection / webcam
    # ❌ Do NOT expose admin to public (optional)

    # ✅ Public challan system
    path('', include('challan.urls')),
    path('', home),                 # ✅ FIX
    path('challan/', include('challan.urls')),
]

# Serve media only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

