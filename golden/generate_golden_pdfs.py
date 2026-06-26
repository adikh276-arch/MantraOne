import os
try:
    from fpdf import FPDF
except ImportError:
    os.system("pip install fpdf2")
    from fpdf import FPDF

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def create_pdf(filename, title, patient, content_lines):
    path = os.path.join(REPORTS_DIR, filename)
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="MantraOne Health Labs", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Report: {title}", ln=True)
    pdf.cell(200, 10, txt=f"Patient: {patient}", ln=True)
    pdf.cell(200, 10, txt="Date: 2023-10-15", ln=True)
    pdf.line(10, 50, 200, 50)
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=11)
    for line in content_lines:
        pdf.multi_cell(0, 8, txt=line)
        
    pdf.output(path)
    print(f"Generated {path}")

if __name__ == "__main__":
    create_pdf(
        "diabetes_lab.pdf",
        "HbA1c & Fasting Glucose",
        "Anil Sharma",
        [
            "Test Results:",
            "- HbA1c: 8.2% (High) - Reference: < 5.7%",
            "- Fasting Blood Glucose: 165 mg/dL (High) - Reference: < 100 mg/dL",
            "- Post-Prandial Glucose: 210 mg/dL (High)",
            "",
            "Notes: Patient presents with uncontrolled Type 2 Diabetes.",
            "Recommended starting Metformin 500mg BD.",
            "Needs strict diet control and daily exercise."
        ]
    )

    create_pdf(
        "thyroid_report.pdf",
        "Thyroid Function Test",
        "Priya Sharma",
        [
            "Test Results:",
            "- TSH: 8.5 uIU/mL (High) - Reference: 0.4 - 4.0 uIU/mL",
            "- Free T4: 0.8 ng/dL (Low) - Reference: 0.9 - 1.7 ng/dL",
            "- Free T3: 2.1 pg/mL (Normal)",
            "",
            "Notes: Clinical hypothyroidism confirmed.",
            "Recommended Thyroxine 50mcg daily before breakfast.",
            "Re-evaluate after 6 weeks."
        ]
    )

    create_pdf(
        "cbc_report.pdf",
        "Complete Blood Count",
        "Karthik Iyer",
        [
            "Test Results:",
            "- Hemoglobin: 14.5 g/dL (Normal)",
            "- WBC: 6,500 /cumm (Normal)",
            "- Platelets: 250,000 /cumm (Normal)",
            "",
            "Notes: All values within normal physiological limits."
        ]
    )

    create_pdf(
        "vaccination_record.pdf",
        "Pediatric Vaccination Log",
        "Aarav Singh",
        [
            "Vaccination Record:",
            "- 2022-01-15: MMR (Dose 1) - Administered",
            "- 2022-03-20: DTaP (Dose 1) - Administered",
            "- 2023-01-10: Hepatitis A (Dose 1) - Administered",
            "",
            "Upcoming:",
            "- Flu Shot due next month."
        ]
    )
