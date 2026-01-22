from django.shortcuts import render
from .models import Challan
from django.http import JsonResponse

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
def api_check_challan(request):
    vehicle_number = request.GET.get("vehicle_number")

    if not vehicle_number:
        return JsonResponse({
            "success": False,
            "message": "Vehicle number is required"
        })

    challans = Challan.objects.filter(
        vehicle__vehicle_number__iexact=vehicle_number.strip().upper()
    )

    if not challans.exists():
        return JsonResponse({
            "success": True,
            "challans": [],
            "message": "No challans found"
        })

    data = []
    for c in challans:
        data.append({
            "challan_number": c.challan_number,
            "vehicle_number": c.vehicle.vehicle_number,
            "amount": c.amount,
            "status": c.status,
            "date": c.created_at.strftime("%Y-%m-%d")
        })

    return JsonResponse({
        "success": True,
        "challans": data
    })
