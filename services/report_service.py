"""
services/report_service.py
--------------------------
Orchestration layer between the FastAPI routes and the execution scripts.
Calls Phase 1 scripts in order and returns a unified result dict.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from execution.fetch_student_data import fetch_student_data
from execution.calculate_stats import build_full_stats
from execution.generate_charts import generate_all_charts
from execution.generate_pdf import generate_pdf


def build_report(roll_no: str, class_name: str, student_name: str = None) -> dict:
    """
    Full pipeline: fetch → calculate → chart → PDF.

    Returns:
    {
        "student_name": str,
        "summary":      str,   # WhatsApp-formatted text
        "pdf_path":     str,
        "chart_paths":  dict,
    }

    Raises:
        ValueError        — student not found
        EnvironmentError  — missing env vars / credentials
        Exception         — unexpected failures
    """
    roll_no = str(roll_no).strip()
    class_name = str(class_name).strip()
    
    # 1. Fetch
    raw_data = fetch_student_data(roll_no, class_name, student_name)
    

    # 2. Calculate
    stats = build_full_stats(raw_data)

    # 3. Charts
    chart_paths = generate_all_charts(stats)

    # 4. PDF
    pdf_path = generate_pdf(stats, chart_paths)

    # 5. Build WhatsApp text summary
    summary = _build_summary(stats)

    return {
        "student_name": stats["student"]["name"],
        "summary": summary,
        "weekly_snapshot": stats["weekly_snapshot"],
        "pdf_path": pdf_path,
        "chart_paths": chart_paths,
    }


def _build_summary(stats: dict) -> str:
    """Build a WhatsApp-friendly plain-text summary."""
    student = stats["student"]
    att     = stats["attendance"]
    tests   = stats["tests"]
    exams   = stats["exams"]

    lines = [
        f"📋 *Report: {student['name']}*",
        f"Class: {student['class']} | Roll No: {student['roll_no']}",
        "",
        f"📅 *Attendance*",
        f"   {att['percentage']}% ({att['present']}/{att['total']} days)",
    ]

    if att["percentage"] < 75:
        lines.append("   ⚠️ Below 75% threshold!")

    if tests["by_subject"]:
        lines.append(f"\n📝 *Tests* (Avg: {tests['average']})")
        for subj, avg in tests["by_subject"].items():
            lines.append(f"   • {subj}: {avg}")
    else:
        lines.append("\n📝 *Tests*: No records found")

    if exams["by_subject"]:
        lines.append(f"\n🎓 *Exams* (Avg: {exams['average']})")
        for subj, avg in exams["by_subject"].items():
            lines.append(f"   • {subj}: {avg}")
    else:
        lines.append("\n🎓 *Exams*: No records found")

    lines.append("\n📄 PDF report attached.")
    return "\n".join(lines)
