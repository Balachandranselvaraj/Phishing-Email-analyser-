import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from config import REPORT_DIR


def generate_pdf_report(scan_id, result):
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, f"scan_{scan_id}.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 50

    def line(text, size=11):
        nonlocal y
        if y < 60:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica", size)
        c.drawString(40, y, str(text)[:110])
        y -= 18

    line("Email Analyzer Report", 16)
    line("=" * 80)
    summary = result.get("email_summary", {})
    risk = result.get("risk", {})
    line(f"Subject: {summary.get('subject', '')}")
    line(f"From: {summary.get('from', '')}")
    line(f"To: {summary.get('to', '')}")
    line(f"Risk Score: {risk.get('score')} / 100")
    line(f"Verdict: {risk.get('verdict')}")
    line(f"Recommendation: {risk.get('recommendation')}")
    line("")

    for section_name in ["header_analysis", "url_analysis", "attachment_analysis", "content_analysis"]:
        line(section_name.replace("_", " ").title(), 13)
        section = result.get(section_name, {})
        if isinstance(section, dict):
            for key, value in section.items():
                if key == "results" and isinstance(value, list):
                    line(f"{key}: {len(value)} item(s)")
                    for item in value[:5]:
                        line(f" - {item}")
                else:
                    line(f"{key}: {value}")
        line("")

    c.save()
    return path
