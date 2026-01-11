from django.db import models


class Violation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    # 📷 Evidence Images
    image = models.ImageField(upload_to='violations/', null=True, blank=True)
    plate_image = models.ImageField(upload_to='plates/', null=True, blank=True)

    # 🚗 Detection Results
    vehicle_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    helmet_detected = models.BooleanField(default=False)
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
    detected_at = models.DateTimeField(auto_now_add=True)

    # ✅ Admin Decision
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    def __str__(self):
        return f"{self.vehicle_number or 'UNKNOWN'} - {self.detected_at.strftime('%d-%m-%Y %H:%M')}"

    class Meta:
        ordering = ['-detected_at']
