from django.urls import path
from .views import search_challan, api_search_challan

urlpatterns = [
    # Web page (HTML)
    path('search/', search_challan, name='search_challan'),

    # API (JSON)
    path('api/search/', api_search_challan, name='api_search_challan'),
]
