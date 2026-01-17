from django.shortcuts import render
from django.db.models import Q
from .models import Challan


def search_challan(request):
    """
    Search challan by:
    - eChallan number
    - vehicle number
    """

    query = request.GET.get('q', '').strip()
    challans = []

    if query:
        challans = Challan.objects.filter(
            Q(echallan_number__iexact=query) |
            Q(violation__vehicle_number__iexact=query)
        ).select_related('violation', 'violation__vehicle')

    return render(request, 'challan/search.html', {
        'challans': challans,
        'query': query
    })
