
from django.urls import path
from .views import search_challan

urlpatterns = [
    path('', search_challan, name='search_challan'),
]