from django.shortcuts import render
from django.http import JsonResponse
from .models import Challan


def api_search_challan(request):
    query = request.GET.get('q')

    if not query:
        return JsonResponse({
            "success": False,
            "message": "Query parameter 'q' is required"
        })

    challans = Challan.objects.filter(
        echallan_number=query
    ) | Challan.objects.filter(
        violation__vehicle_number=query
    )

    data = []
    for c in challans:
        data.append({
            "echallan_number": c.echallan_number,
            "fine_amount": c.fine_amount,
            "paid": c.paid,
            "issued_at": c.issued_at.strftime("%Y-%m-%d %H:%M")
        })

    return JsonResponse({
        "success": True,
        "challans": data
    })
