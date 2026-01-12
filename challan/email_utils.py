from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta

def send_challan_email(challan):
    violation = challan.violation
    vehicle = violation.vehicle

    due_date = challan.issued_at + timedelta(days=90)

    subject = f"e-Challan Notice | {challan.echallan_number}"

    message = f"""
Dear {vehicle.owner_name},

Your vehicle has violated traffic rules.

📌 Vehicle Number: {vehicle.vehicle_number}
📍 Location: {violation.location}
💰 Fine Amount: ₹{challan.fine_amount}
📅 Date: {violation.detected_at.strftime('%d-%m-%Y %H:%M')}
⏳ Payment Due: {due_date.strftime('%d-%m-%Y')}

Please pay the fine within 90 days to avoid penalties.

Regards,
Traffic Department
"""

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [vehicle.owner_email],
    )

    # Attach violation image
    if violation.image:
        email.attach_file(violation.image.path)

    email.send(fail_silently=False)
