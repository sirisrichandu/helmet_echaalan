from django.shortcuts import render
from .models import Challan

def search_challan(request):
    query = request.GET.get("q")   # GET, not POST
    search_type = request.GET.get("type")

    challans = []

    if query:
        if search_type == "vehicle":
            challans = Challan.objects.select_related("violation").filter(
                violation__vehicle_number__iexact=query.strip()
            )
        else:
            challans = Challan.objects.select_related("violation").filter(
                echallan_number=query.strip()
            )

    return render(request, "challan/search.html", {
        "challans": challans,
        "query": query,
    })