from django.shortcuts import render
from django.db.models import Q
from .models import Challan


def search_challan(request):
    query = request.GET.get('q', '').strip()
    challans = []

    if query:
        challans = Challan.objects.filter(
            Q(challan_number__iexact=query) |
            Q(vehicle_number__iexact=query)
        )

    return render(
        request,
        'challan/search.html',
        {
            'challans': challans,
            'query': query
        }
    )
