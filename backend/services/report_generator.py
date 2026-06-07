from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.config import get_settings


class ReportGenerator:
    def __init__(self) -> None:
        self.settings = get_settings()

    def create_pdf(self, audit_result: dict[str, Any], filename: str | None = None) -> Path:
        report_name = filename or "compliance_audit_report.pdf"
        output_path = self.settings.reports_dir / report_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=12))
        story = [Paragraph("Automated Compliance Audit Report", styles["Title"]), Spacer(1, 0.2 * inch)]
        story.append(Paragraph(f"Overall Risk: {audit_result.get('overall_risk', 'unknown')}", styles["Heading2"]))
        story.append(Paragraph(audit_result.get("summary", ""), styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))

        violations = audit_result.get("violations", [])
        for violation in violations:
            table_data = [
                ["Question", violation.get("question", "")],
                ["Finding", violation.get("finding", "")],
                ["Severity", violation.get("severity", "")],
                ["Status", violation.get("status", "")],
                ["Citations", ", ".join(chunk.get("chunk_id", "") for chunk in violation.get("citations", []))],
            ]
            table = Table(table_data, colWidths=[1.4 * inch, 4.9 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0f172a")),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                        ("BACKGROUND", (1, 0), (1, -1), colors.whitesmoke),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ]
                )
            )
            story.append(KeepTogether([Paragraph("Finding", styles["Heading3"]), table, Spacer(1, 0.15 * inch)]))

        recommendations = audit_result.get("recommendations", [])
        if recommendations:
            story.append(Paragraph("Recommendations", styles["Heading2"]))
            for item in recommendations:
                story.append(Paragraph(f"• {item}", styles["BodyText"]))

        doc.build(story)
        output_path.write_bytes(buffer.getvalue())
        return output_path


report_generator = ReportGenerator()
