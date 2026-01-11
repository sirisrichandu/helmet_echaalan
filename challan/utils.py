import random
from .models import Challan


def generate_unique_echallan_number():
    """
    Generates a unique 5-digit e-Challan number (00000–99999)
    """
    while True:
        number = f"{random.randint(0, 99999):05d}"
        if not Challan.objects.filter(echallan_number=number).exists():
            return number


def generate_challan(violation):
    """
    Called ONLY after admin approval
    """

    # Safety: avoid duplicates for same violation
    if violation.challans.exists():
        return violation.challans.first()

    fine_amount = 0 if violation.helmet_detected else 500

    challan = Challan.objects.create(
        violation=violation,
        echallan_number=generate_unique_echallan_number(),
        fine_amount=fine_amount
    )

    return challan
