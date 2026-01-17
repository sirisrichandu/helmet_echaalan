import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings


def generate_challan_pdf(challan):
    folder = os.path.join(settings.MEDIA_ROOT, "challan_pdfs")
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, f"{challan.echallan_number}.pdf")

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 50, "e-Challan Notice")
    c.drawString(50, height - 90, f"Challan No: {challan.echallan_number}")
    c.drawString(50, height - 120, f"Vehicle No: {challan.violation.vehicle_number}")
    c.drawString(50, height - 150, f"Fine Amount: ₹{challan.fine_amount}")
    c.drawString(50, height - 180, f"Location: {challan.violation.location}")
    c.drawString(50, height - 210, f"Issued At: {challan.issued_at.strftime('%d-%m-%Y')}")

    c.showPage()
    c.save()

    return path
