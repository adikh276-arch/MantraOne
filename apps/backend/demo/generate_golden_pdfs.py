import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../../../golden/reports")


def create_pdf(filename, title, patient, content_lines):
    path = os.path.join(REPORTS_DIR, filename)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    c = canvas.Canvas(path, pagesize=letter)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, 10 * inch, "MantraOne Health Labs")

    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, 9.5 * inch, f"Report: {title}")
    c.drawString(1 * inch, 9.25 * inch, f"Patient: {patient}")
    c.drawString(1 * inch, 9.0 * inch, "Date: 2023-10-15")

    # Line
    c.line(1 * inch, 8.8 * inch, 7.5 * inch, 8.8 * inch)

    # Content
    c.setFont("Helvetica", 11)
    y = 8.3 * inch
    for line in content_lines:
        c.drawString(1 * inch, y, line)
        y -= 0.3 * inch

    c.save()


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
            "Needs strict diet control and daily exercise.",
        ],
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
            "Re-evaluate after 6 weeks.",
        ],
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
            "Notes: All values within normal physiological limits.",
        ],
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
            "- Flu Shot due next month.",
        ],
    )
    print("Golden PDFs generated successfully.")
