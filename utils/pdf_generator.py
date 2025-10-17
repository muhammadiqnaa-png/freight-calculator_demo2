from fpdf import FPDF

def generate_pdf(results, filename="freight_result.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Freight Calculator Result", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Sailing Time: {results['sailing_time']:.2f} Hour", ln=True)
    pdf.cell(0, 10, f"Total Voyage Days: {results['total_voyage_days']:.2f} Days", ln=True)
    pdf.cell(0, 10, f"Total Consumption: {results['total_consumption']:.2f} Ltr", ln=True)
    pdf.cell(0, 10, f"Total Cost: Rp {results['total_cost']:.2f}", ln=True)
    pdf.cell(0, 10, f"Freight per Unit: Rp {results['freight_per_unit']:.2f}", ln=True)
    
    pdf.ln(10)
    pdf.cell(0, 10, "Profit Table 0-50%", ln=True)
    
    for row in results['profit_table']:
        pdf.cell(0, 8, f"{row['Percent']}% - Revenue: {row['Revenue']:.2f} | PPH: {row['PPH']:.2f} | Profit: {row['Profit']:.2f}", ln=True)
    
    pdf.output(filename)
    return filename
