from django.db import models
from vehicles.models import Vehicle


class Violation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    # 🔗 Linked Vehicle (VERY IMPORTANT)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='violations',
        help_text="Linked automatically using OCR vehicle number"
    )

    # 📷 Evidence Images
    image = models.ImageField(
        upload_to='violations/',
        null=True,
        blank=True
    )

    plate_image = models.ImageField(
        upload_to='plates/',
        null=True,
        blank=True
    )

    # 🚗 Detection Results
    vehicle_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_index=True
    )

    helmet_detected = models.BooleanField(
        default=False,
        help_text="True = helmet worn, False = violation"
    )

    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="OCR confidence percentage"
    )

    # 📍 Location (Google Maps)
    location = models.CharField(
        max_length=100,
        default='Bhimavaram'
    )

    latitude = models.FloatField(
        default=16.5449
    )

    longitude = models.FloatField(
        default=81.5212
    )

    # 🕒 Time
    detected_at = models.DateTimeField(
        auto_now_add=True
    )

    # ✅ Admin Decision
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # =========================
    # STRING REPRESENTATION
    # =========================
    def __str__(self):
        return f"{self.vehicle_number or 'UNKNOWN'} | {self.status}"

    # =========================
    # META
    # =========================
    class Meta:
        ordering = ['-detected_at']
        verbose_name = "Helmet Violation"
        verbose_name_plural = "Helmet Violations"
