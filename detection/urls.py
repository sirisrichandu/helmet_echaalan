from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # ROOT → detection home
    path('', lambda request: redirect('/detect/')),

    path('admin/', admin.site.urls),
    path('detect/', include('detection.urls')),
    path('accounts/', include('accounts.urls')),
    path('challan/', include('challan.urls')),
]
