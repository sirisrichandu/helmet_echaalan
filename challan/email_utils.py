from django.core.mail import EmailMessage
from django.conf import settings
from datetime import timedelta
from django.utils.timezone import now

from .pdf_utils import generate_challan_pdf


def send_challan_email(challan):
    violation = challan.violation
    vehicle = violation.vehicle

    if not vehicle or not vehicle.owner_email:
        return

    due_date = challan.issued_at + timedelta(days=90)

    subject = f"e-Challan Notice | {challan.echallan_number}"

    message = f"""
Dear {vehicle.owner_name},

Your vehicle has violated traffic rules.

📌 Vehicle Number: {vehicle.vehicle_number}
📍 Location: {violation.location}
💰 Fine Amount: ₹{challan.fine_amount}
📅 Violation Date: {violation.detected_at.strftime('%d-%m-%Y %H:%M')}
⏳ Payment Due Date: {due_date.strftime('%d-%m-%Y')}

Please pay the fine within 90 days to avoid penalties.

Regards,
Traffic Department
"""

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[vehicle.owner_email],
    )

    # 📎 Attach violation image
    if violation.image:
        email.attach_file(violation.image.path)

    # 📄 Attach PDF challan
    pdf_path = generate_challan_pdf(challan)
    email.attach_file(pdf_path)

    email.send(fail_silently=False)
