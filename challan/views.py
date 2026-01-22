from django.shortcuts import render
from django.db.models import Q
from .models import Challan

def search_challan(request):
    query = request.GET.get("q")
    search_type = request.GET.get("type")  # vehicle / challan

    challans = []

    if query:
        if search_type == "vehicle":
            challans = Challan.objects.select_related("violation").filter(
                violation__vehicle_number__iexact=query
            )
        else:  # challan number
            challans = Challan.objects.select_related("violation").filter(
                echallan_number__iexact=query
            )

    return render(request, "challan/search.html", {
        "challans": challans,
        "query": query,
    })