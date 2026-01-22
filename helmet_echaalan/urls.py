from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse






urlpatterns = [
    path('', include('challan.urls')),
]
# Serve media only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
