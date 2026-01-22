from django.shortcuts import render
from .models import Challan
from django.db.models import Q

def search_challan(request):
    query = request.GET.get("q")
    challans = []

    if query:
        challans = Challan.objects.select_related("violation").filter(
            Q(echallan_number__iexact=query) |
            Q(violation__vehicle_number__iexact=query)
        )

    return render(request, "challan/search.html", {
        "query": query,
        "challans": challans,
    })