from django.contrib import admin
from django.utils.html import format_html
from .models import Violation
from challan.utils import generate_challan


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = (
        'vehicle_number',
        'helmet_detected',
        'location',
        'detected_at',
        'status',
    )

    list_filter = ('status', 'helmet_detected', 'location')
    search_fields = ('vehicle_number',)

    readonly_fields = (
        'image_preview',
        'plate_preview',
        'detected_at',
        'confidence',
    )

    actions = ('approve_violation', 'reject_violation')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="250"/>', obj.image.url)
        return "No image"

    def plate_preview(self, obj):
        if obj.plate_image:
            return format_html('<img src="{}" width="180"/>', obj.plate_image.url)
        return "No plate"

    def approve_violation(self, request, queryset):
        for v in queryset:
            if v.status == 'PENDING':
                v.status = 'APPROVED'
                v.save()
                generate_challan(v)

        self.message_user(request, "Approved & e-Challan generated.")

    def reject_violation(self, request, queryset):
        queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, "Rejected. No fine generated.")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='PENDING')
