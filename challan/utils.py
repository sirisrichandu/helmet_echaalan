import random
from .models import Challan
from .email_utils import send_challan_email


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
    Generate challan ONLY after admin approval
    """

    # 🚫 Prevent duplicate challans
    if violation.challans.exists():
        return violation.challans.first()

    fine_amount = 0 if violation.helmet_detected else 500

    challan = Challan.objects.create(
        violation=violation,
        echallan_number=generate_unique_echallan_number(),
        fine_amount=fine_amount
    )

    # 📧 Send email if vehicle + email exist
    try:
        if violation.vehicle and violation.vehicle.owner_email:
            send_challan_email(challan)
    except Exception as e:
        # ❗ Never block challan creation due to email failure
        print("Email sending failed:", e)

    return challan
