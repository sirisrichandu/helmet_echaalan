from django.shortcuts import render
from .models import Challan

def search_challan(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'challan')

    challans = []

    if query:
        if search_type == 'challan':
            challans = Challan.objects.filter(echallan_number=query)
        elif search_type == 'vehicle':
            challans = Challan.objects.filter(
                violation__vehicle_number__iexact=query
            )

    return render(request, 'challan/search.html', {
        'challans': challans,
        'query': query,
    })
