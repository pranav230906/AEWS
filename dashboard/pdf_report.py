# dashboard/pdf_report.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


def generate_pdf_report(
    state,
    district,
    risk_level,
    reasons,
    actions,
    output_path
):
    """
    Generates a one-page PDF risk report for a district
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "AEWS – Aadhaar Early Warning System")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"State: {state}")
    y -= 20
    c.drawString(40, y, f"District: {district}")
    y -= 20
    c.drawString(40, y, f"Predicted Risk (Next Month): {risk_level}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Why this risk was predicted:")
    y -= 20

    c.setFont("Helvetica", 11)
    for r in reasons:
        c.drawString(50, y, f"- {r}")
        y -= 16

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Recommended Actions:")
    y -= 20

    c.setFont("Helvetica", 11)
    for a in actions:
        c.drawString(50, y, f"- {a}")
        y -= 16

    c.showPage()
    c.save()
