from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/detect/')),  # ROOT FIX
    path('admin/', admin.site.urls),
    path('detect/', include('detection.urls')),
    path('accounts/', include('accounts.urls')),
    path('challan/', include('challan.urls')),
]
