from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_pdf(weight, distance, cost, user_email):
    """
    Membuat file PDF hasil perhitungan freight.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Judul
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "Freight Calculator Report")

    # Detail
    c.setFont("Helvetica", 12)
    c.drawString(50, 760, f"User: {user_email}")
    c.drawString(50, 740, f"Berat (kg): {weight}")
    c.drawString(50, 720, f"Jarak (km): {distance}")
    c.drawString(50, 700, f"Total Biaya: Rp {cost:,.0f}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 50, f"Generated Freight Calculator by {user_email}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
