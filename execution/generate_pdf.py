"""
generate_pdf.py
---------------
Generates an executive, highly readable PDF student report using ReportLab.

Inputs:
  - stats:       dict from calculate_stats.build_full_stats()
  - chart_paths: dict from generate_charts.generate_all_charts()

Output:
  - PDF file saved to .tmp/reports/<roll_no>_report.pdf
  - Returns path to the generated PDF
"""

import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

REPORT_DIR = ".tmp/reports"

def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path

def _clean_text_for_pdf(text: str) -> str:
    """Removes WhatsApp markdown characters like * _ ` and emojis for crisp PDF display."""
    if not text:
        return ""
    text = text.replace("*", "").replace("_", "").replace("`", "")
    # Remove emojis that might fail in standard ReportLab Helvetica font
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    return text.strip()

def generate_pdf(stats: dict, chart_paths: dict) -> str:
    _ensure_dir(REPORT_DIR)
    student = stats["student"]
    roll_no = str(student.get("roll_no", "1")).strip()
    out_path = os.path.join(REPORT_DIR, f"{roll_no}_report.pdf")

    # Document setup with 1.5 cm margins for maximum printable area
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    # ── Color Palette ────────────────────────────────────────────────────────
    PRIMARY = colors.HexColor("#0F172A")       # Deep Slate Header
    SECONDARY = colors.HexColor("#0284C7")     # Sky Blue Accent
    TEXT_DARK = colors.HexColor("#334155")     # Body Text Slate
    TEXT_LIGHT = colors.HexColor("#64748B")    # Secondary Text Slate
    BG_CARD = colors.HexColor("#F8FAFC")       # Soft Card Background
    BORDER_COLOR = colors.HexColor("#CBD5E1")  # Soft Border Gray
    GREEN_ACCENT = colors.HexColor("#16A34A")  # Success Green
    RED_ACCENT = colors.HexColor("#DC2626")    # Warning Red

    # ── Typography & Styles ──────────────────────────────────────────────────
    header_title_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontSize=18,
        leading=22,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
    )

    header_sub_style = ParagraphStyle(
        "HeaderSub",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#94A3B8"),
        alignment=TA_LEFT,
    )

    header_date_style = ParagraphStyle(
        "HeaderDate",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#38BDF8"),
        alignment=TA_RIGHT,
    )

    section_heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=PRIMARY,
        fontName="Helvetica-Bold",
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
    )

    card_label_style = ParagraphStyle(
        "CardLabel",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9,
        textColor=TEXT_LIGHT,
        fontName="Helvetica-Bold",
    )

    card_val_style = ParagraphStyle(
        "CardVal",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=PRIMARY,
        fontName="Helvetica-Bold",
    )

    kpi_num_style = ParagraphStyle(
        "KpiNum",
        parent=styles["Normal"],
        fontSize=14,
        leading=17,
        textColor=PRIMARY,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    )

    kpi_label_style = ParagraphStyle(
        "KpiLabel",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
    )

    story = []

    # ── 1. HEADER BANNER ─────────────────────────────────────────────────────
    now_str = datetime.now().strftime("%b %d, %Y")
    header_data = [
        [
            Paragraph("STUDENT ACADEMIC PERFORMANCE REPORT", header_title_style),
            Paragraph(f"Date: <b>{now_str}</b>", header_date_style)
        ],
        [
            Paragraph("Official Student Evaluation & Performance Progress", header_sub_style),
            Paragraph("Session 2025–2026", header_date_style)
        ]
    ]

    header_table = Table(header_data, colWidths=[12.5 * cm, 5.5 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3 * cm))

    # ── 2. STUDENT PROFILE & KPI CARDS GRID ──────────────────────────────────
    att = stats["attendance"]
    tests = stats["tests"]
    exams = stats["exams"]

    # Student Info Table
    info_cell_data = [
        [
            Paragraph("STUDENT NAME", card_label_style),
            Paragraph("CLASS / SECTION", card_label_style),
            Paragraph("ROLL NO", card_label_style)
        ],
        [
            Paragraph(student.get("name", "—"), card_val_style),
            Paragraph(student.get("class", "—"), card_val_style),
            Paragraph(str(student.get("roll_no", "—")), card_val_style)
        ]
    ]
    info_box = Table(info_cell_data, colWidths=[5.5 * cm, 3.2 * cm, 2.3 * cm])
    info_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    # KPI Box (Attendance %, Test Avg, Exam Avg)
    att_pct = att.get("percentage", 0.0)
    att_color = GREEN_ACCENT if att_pct >= 75 else RED_ACCENT
    
    kpi_cell_data = [
        [
            Paragraph(f"<font color='{att_color.hexval()}'><b>{att_pct}%</b></font>", kpi_num_style),
            Paragraph(f"<b>{tests.get('average', 0.0)}</b>", kpi_num_style),
            Paragraph(f"<b>{exams.get('average', 0.0)}</b>", kpi_num_style)
        ],
        [
            Paragraph("ATTENDANCE", kpi_label_style),
            Paragraph("TEST AVG", kpi_label_style),
            Paragraph("EXAM AVG", kpi_label_style)
        ]
    ]
    kpi_box = Table(kpi_cell_data, colWidths=[2.3 * cm, 2.3 * cm, 2.4 * cm])
    kpi_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
        ("BOX", (0, 0), (-1, -1), 0.75, SECONDARY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    # Top Row Container
    top_grid = Table([[info_box, kpi_box]], colWidths=[11 * cm, 7 * cm])
    top_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(top_grid)
    story.append(Spacer(1, 0.3 * cm))

    # ── 3. ATTENDANCE SUMMARY ────────────────────────────────────────────────
    att_flowables = [
        Paragraph("📅 Attendance Overview", section_heading_style),
        HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=6)
    ]

    att_summary_data = [
        ["Total Days", "Present", "Absent", "Attendance Rate", "Status"],
        [
            str(att["total"]),
            str(att["present"]),
            str(att["absent"]),
            f"{att['percentage']}%",
            "Satisfactory" if att["percentage"] >= 75 else "Low Attendance"
        ]
    ]
    att_table = Table(att_summary_data, colWidths=[3.2 * cm, 2.8 * cm, 2.8 * cm, 4.2 * cm, 5.0 * cm])
    _apply_table_style(att_table, header_bg=PRIMARY if att["percentage"] >= 75 else RED_ACCENT)
    att_flowables.append(att_table)

    if att["percentage"] < 75:
        att_flowables.append(Spacer(1, 0.15 * cm))
        warn_box = Table([[Paragraph("⚠️ <b>Warning:</b> Attendance is below mandatory 75% requirement.", ParagraphStyle("W", parent=body_style, textColor=RED_ACCENT))]], colWidths=[18 * cm])
        warn_box.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
            ("BOX", (0,0), (-1,-1), 1, RED_ACCENT),
            ("PADDING", (0,0), (-1,-1), 4),
        ]))
        att_flowables.append(warn_box)

    att_flowables.append(Spacer(1, 0.2 * cm))
    _add_chart_embed(att_flowables, chart_paths.get("attendance"), "Attendance Trend Chart")
    story.append(KeepTogether(att_flowables))

    # ── 4. ACADEMIC PERFORMANCE (TESTS & EXAMS) ──────────────────────────────
    if tests["by_subject"]:
        test_flowables = [
            Spacer(1, 0.2 * cm),
            Paragraph("📝 Test Performance", section_heading_style),
            HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=6)
        ]

        test_headers = ["Subject", "Average Score", "Grade Status"]
        test_rows = [test_headers]
        for subj, avg in tests["by_subject"].items():
            badge = "Excellent (>= 75%)" if avg >= 75 else ("Moderate (60-74%)" if avg >= 60 else "Needs Attention (< 60%)")
            test_rows.append([subj, f"{avg}%", badge])
        
        test_table = Table(test_rows, colWidths=[6.5 * cm, 5.5 * cm, 6.0 * cm])
        _apply_table_style(test_table)
        test_flowables.append(test_table)
        
        test_flowables.append(Spacer(1, 0.2 * cm))
        _add_chart_embed(test_flowables, chart_paths.get("tests"), "Test Performance Chart")
        story.append(KeepTogether(test_flowables))

    # Exam Section
    if exams["by_subject"]:
        exam_flowables = [
            Spacer(1, 0.2 * cm),
            Paragraph("🎓 Exam Performance", section_heading_style),
            HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=6)
        ]

        exam_headers = ["Subject", "Exam Score", "Grade Status"]
        exam_rows = [exam_headers]
        for subj, avg in exams["by_subject"].items():
            badge = "Excellent (>= 75%)" if avg >= 75 else ("Moderate (60-74%)" if avg >= 60 else "Needs Attention (< 60%)")
            exam_rows.append([subj, f"{avg}%", badge])
        
        exam_table = Table(exam_rows, colWidths=[6.5 * cm, 5.5 * cm, 6.0 * cm])
        _apply_table_style(exam_table)
        exam_flowables.append(exam_table)

        exam_flowables.append(Spacer(1, 0.2 * cm))
        _add_chart_embed(exam_flowables, chart_paths.get("exams"), "Exam Performance Chart")
        story.append(KeepTogether(exam_flowables))

    # ── 5. PERFORMANCE INSIGHTS BOX ──────────────────────────────────────────
    insight_text = _clean_text_for_pdf(stats.get("full_overview_text", ""))

    # Remove trailing "(PDF attached below)" or similar notes from PDF body
    insight_text = re.sub(r'\(PDF attached.*\)', '', insight_text, flags=re.IGNORECASE).strip()

    insight_content = [
        [Paragraph(f"<b>Performance Summary & Recommendations:</b><br/><br/>{insight_text.replace(chr(10), '<br/>')}", body_style)]
    ]
    insight_box = Table(insight_content, colWidths=[18 * cm])
    insight_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
        ("BOX", (0, 0), (-1, -1), 1, SECONDARY),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    
    insight_flowables = [
        Spacer(1, 0.3 * cm),
        Paragraph("💡 Key Performance Insights", section_heading_style),
        HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=6),
        insight_box
    ]
    story.append(KeepTogether(insight_flowables))

    # ── 6. FOOTER ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=4))
    story.append(
        Paragraph(
            "This document is an official academic progress evaluation. "
            "For queries regarding this report, please contact school administration.",
            ParagraphStyle("FooterNote", parent=body_style, fontSize=7.5, textColor=TEXT_LIGHT, alignment=TA_CENTER)
        )
    )

    doc.build(story)
    return out_path


def _add_chart_embed(flowables, path: str, title: str):
    if path and os.path.exists(path):
        img = Image(path, width=17.5 * cm, height=5.2 * cm)
        flowables.append(img)
    else:
        flowables.append(
            Paragraph(f"<i>[{title} not available]</i>", ParagraphStyle("ItalicNote", fontSize=8.5, textColor=colors.gray))
        )
    flowables.append(Spacer(1, 0.15 * cm))


def _apply_table_style(table, header_bg=colors.HexColor("#0F172A")):
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
