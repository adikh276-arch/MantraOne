import os

try:
    from fpdf import FPDF
except ImportError:
    os.system("pip install fpdf2")
    from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
pdf.cell(200, 10, txt="MANTRA HEALTHCARE CLINIC", ln=True, align='C')
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Patient: Robert Smith", ln=True)
pdf.cell(200, 10, txt="Date: 2026-06-25", ln=True)
pdf.ln(10)

pdf.set_font("Arial", style='B', size=12)
pdf.cell(200, 10, txt="Clinical Notes:", ln=True)
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, txt="Patient reports worsening insomnia over the past 3 weeks, sleeping only 4 hours per night. Occasional mild chest tightness under stress. Blood pressure elevated at 145/90.")
pdf.ln(5)

pdf.set_font("Arial", style='B', size=12)
pdf.cell(200, 10, txt="Medications Prescribed:", ln=True)
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="1. Amlodipine 5mg - Take 1 tablet daily (for blood pressure)", ln=True)
pdf.cell(200, 10, txt="2. Melatonin 3mg - Take 1 tablet at bedtime (for sleep)", ln=True)
pdf.cell(200, 10, txt="3. STOP taking Ibuprofen daily.", ln=True)

pdf.output("demo/sample_prescription.pdf")
print("demo/sample_prescription.pdf generated.")
