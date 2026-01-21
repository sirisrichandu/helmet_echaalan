from django.shortcuts import render
from .models import Challan


def search_challan(request):
    query = request.GET.get('q', '').strip()
    challans = []

    if query:
        challans = Challan.objects.filter(
            echallan_number__iexact=query
        )

    return render(
        request,
        'challan/search.html',
        {
            'challans': challans,
            'query': query
        }
    )
