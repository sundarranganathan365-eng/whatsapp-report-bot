"""
run_report.py
-------------
End-to-end runner for Phase 1.  Orchestrates:
  1. Fetch student data from Google Sheets
  2. Calculate statistics
  3. Generate charts
  4. Generate PDF

Usage:
  python execution/run_report.py <roll_no> <class_name> [student_name]

  Example:
  python execution/run_report.py 23 10A Rahul
"""

import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from fetch_student_data import fetch_student_data
from calculate_stats import build_full_stats
from generate_charts import generate_all_charts
from generate_pdf import generate_pdf


def run_full_report(roll_no: str, class_name: str, student_name: str = None) -> dict:
    """
    Run the full pipeline for a given roll number and class.

    Returns:
    {
        "student_name": str,
        "summary": str,          # human-readable text summary
        "pdf_path": str,
        "chart_paths": dict,
    }
    """
    print(f"[1/4] Fetching data for Roll No: {roll_no}, Class: {class_name} ...")
    raw_data = fetch_student_data(roll_no, class_name, student_name)

    print("[2/4] Calculating statistics ...")
    stats = build_full_stats(raw_data)

    print("[3/4] Generating charts ...")
    chart_paths = generate_all_charts(stats)

    print("[4/4] Generating PDF ...")
    pdf_path = generate_pdf(stats, chart_paths)

    # Build a text summary (used later for WhatsApp message)
    att = stats["attendance"]
    tests = stats["tests"]
    exams = stats["exams"]
    student = stats["student"]

    summary_lines = [
        f"📋 *Report for {student['name']}* (Class {student['class']}, Roll {roll_no})",
        "",
        f"📅 *Attendance:* {att['percentage']}% ({att['present']}/{att['total']} days)",
    ]

    if att["percentage"] < 75:
        summary_lines.append("   ⚠️ Below 75% — attendance is a concern!")

    if tests["by_subject"]:
        summary_lines.append(f"\n📝 *Test Average:* {tests['average']}")
        for subj, avg in tests["by_subject"].items():
            summary_lines.append(f"   • {subj}: {avg}")

    if exams["by_subject"]:
        summary_lines.append(f"\n🎓 *Exam Average:* {exams['average']}")
        for subj, avg in exams["by_subject"].items():
            summary_lines.append(f"   • {subj}: {avg}")

    summary = "\n".join(summary_lines)

    print("\n✅ Report generation complete!")
    print(f"   PDF: {pdf_path}")
    print("\n--- Summary ---")
    print(summary)
    print("\n--- WhatsApp Message (Weekly Snapshot) ---")
    print(stats["weekly_snapshot"])

    return {
        "student_name": student["name"],
        "summary": summary,
        "pdf_path": pdf_path,
        "chart_paths": chart_paths,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python execution/run_report.py <roll_no> <class_name> [student_name]")
        sys.exit(1)
        
    roll = sys.argv[1]
    class_name = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        result = run_full_report(roll, class_name, name)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except EnvironmentError as e:
        print(f"\n❌ Config Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
