from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("Helmet E-Challan System is Live")

urlpatterns = [
    # Home page
    path('', home, name='home'),

    # Public challan search
    path('challan/', include('challan.urls')),
]

# Serve media only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
