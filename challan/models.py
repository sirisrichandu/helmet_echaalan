from django.db import models
from detection.models import Violation


class Challan(models.Model):
    violation = models.ForeignKey(
        Violation,
        on_delete=models.CASCADE,
        related_name='challans'
    )

    echallan_number = models.CharField(
        max_length=5,
        unique=True,
        db_index=True
    )

    fine_amount = models.IntegerField()
    issued_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.echallan_number
