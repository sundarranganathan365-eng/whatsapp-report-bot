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


def build_report(roll_no: str, class_name: str, student_name: str = None, report_type: str = "weekly") -> dict:
    """
    Full pipeline: fetch → calculate → chart → PDF.

    report_type: 'weekly' / '1'  OR  'full' / '2' / 'overview'

    Returns:
    {
        "student_name": str,
        "summary":      str,
        "report_text":   str,   # Selected report text format
        "weekly_snapshot": str,
        "full_overview": str,
        "pdf_path":     str,
        "chart_paths":  dict,
    }
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

    # Select report text based on type
    rtype = str(report_type).lower().strip()
    if rtype in ["full", "2", "overview", "all"]:
        selected_text = stats["full_overview_text"]
    else:
        selected_text = stats["weekly_report_text"]

    return {
        "student_name": stats["student"]["name"],
        "summary": selected_text,
        "report_text": selected_text,
        "weekly_snapshot": stats["weekly_report_text"],
        "full_overview": stats["full_overview_text"],
        "pdf_path": pdf_path,
        "chart_paths": chart_paths,
    }
