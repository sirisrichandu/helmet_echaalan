from django.shortcuts import render
from .models import Challan


def search_challan(request):
    query = request.GET.get('q')

    challans = []
    if query:
        challans = Challan.objects.filter(
            echallan_number=query
        ) | Challan.objects.filter(
            violation__vehicle_number=query
        )

    return render(request, 'challan/search.html', {
        'challans': challans,
        'query': query
    })
