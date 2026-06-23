import os
import re
from datetime import datetime
from fpdf import FPDF
from crewai.tools import tool
from src.config.settings import OUTPUT_DIR


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Tech Viability Report | Agent Innovation", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


@tool("Generate PDF Report")
def generate_pdf_report(content: str, technology_name: str) -> str:
    """Generates a structured PDF report from markdown-like content.
    Returns the path to the generated PDF file."""

    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, f"Tech Viability Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, technology_name, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 8, f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.set_text_color(0, 0, 0)

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
        elif line.startswith("## "):
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 8, line[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        elif line.startswith("### "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, line[4:], new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif line.startswith("**") and ":**" in line:
            pdf.set_font("Helvetica", "B", 10)
            parts = line.split(":**", 1)
            label = parts[0].replace("**", "") + ":"
            value = parts[1].strip().rstrip("*") if len(parts) > 1 else ""
            pdf.cell(55, 6, label)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, value)
        elif line.startswith("- "):
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(5, 6, "")
            pdf.multi_cell(0, 6, f"  * {line[2:]}")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, line)

    slug = re.sub(r'[^a-z0-9]+', '_', technology_name.lower()).strip('_')
    filename = f"report_{slug}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)

    return f"PDF report saved to: {filepath}"
