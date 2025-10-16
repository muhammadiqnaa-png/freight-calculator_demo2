import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(df: pd.DataFrame, user: str):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 12)
    text.textLine(f"Freight Calculation Report for {user}")
    text.textLine("")

    for col in df.columns:
        text.textLine(f"{col} : {', '.join(map(str, df[col].tolist()))}")
    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
