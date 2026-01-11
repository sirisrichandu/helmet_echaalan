from django.contrib import admin
from .models import Challan


@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    # =========================
    # LIST VIEW
    # =========================
    list_display = (
        "echallan_number",
        "get_vehicle_number",
        "fine_amount",
        "issued_at",
        "paid",
    )

    list_filter = (
        "paid",
        "issued_at",
    )

    search_fields = (
        "echallan_number",
        "violation__vehicle_number",
    )

    ordering = ("-issued_at",)

    # =========================
    # READ-ONLY FIELDS
    # =========================
    readonly_fields = (
        "echallan_number",
        "issued_at",
    )

    # =========================
    # CUSTOM DISPLAY METHODS
    # =========================
    def get_vehicle_number(self, obj):
        return obj.violation.vehicle_number or "Not detected"

    get_vehicle_number.short_description = "Vehicle Number"

