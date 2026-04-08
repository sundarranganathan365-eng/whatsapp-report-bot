"""
fetch_student_data.py
---------------------
Connects to Google Sheets and fetches all rows related to a given roll number.

Required env vars:
  GOOGLE_SHEETS_KEY         — The Spreadsheet ID from the Google Sheet URL
  GOOGLE_CREDENTIALS_PATH   — Path to the service account credentials.json
"""

import sys
import os

# Ensure the parent directory is in the system path to allow importing from 'services'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.sheets_service import sheets_service
from dotenv import load_dotenv

load_dotenv()

def fetch_student_data(roll_no: str, class_name: str, student_name: str = None) -> dict:
    """
    Fetch all data for a student identified by roll_no and class_name.

    Returns a dict:
    {
        "student":    {"roll_no": ..., "name": ..., "class": ...},
        "attendance": [{"date": ..., "status": ...}, ...],
        "tests":      [{"date": ..., "subject": ..., "marks": ...}, ...],
        "exams":      [{"date": ..., "subject": ..., "marks": ...}, ...],
    }
    """
    roll_no = str(roll_no).strip()
    class_name = str(class_name).strip().upper()
    if student_name:
        student_name = str(student_name).strip().lower()

    # ── students sheet ──────────────────────────────────────────────────────
    students_data = sheets_service.get_all_records("students")

    student_row = None
    for row in students_data:
        row_roll = str(row.get("Roll No", "")).strip()
        row_class = str(row.get("Class", "")).strip().upper()
        row_name = str(row.get("Name", "")).strip().lower()

        if row_roll == roll_no and row_class == class_name:
            if student_name and student_name not in row_name and row_name not in student_name:
                continue # name mismatch
            student_row = row
            break

    if student_row is None:
        raise ValueError(
            f"Student not found for Roll No '{roll_no}' in Class '{class_name}'."
        )

    student = {
        "roll_no": roll_no,
        "name": student_row.get("Name", "Unknown"),
        "class": student_row.get("Class", "Unknown"),
    }

    def match_row(row):
        if str(row.get("Roll No", "")).strip() != roll_no:
            return False
        # If the sheet has a Class column, enforce that it matches too
        if "Class" in row and str(row.get("Class", "")).strip().upper() != class_name:
            return False
        return True

    # ── attendance sheet ────────────────────────────────────────────────────
    attendance_data = sheets_service.get_all_records("attendance")
    attendance = [
        {"date": str(row["Date"]), "status": str(row["Status"]).strip()}
        for row in attendance_data if match_row(row)
    ]

    # ── tests sheet ─────────────────────────────────────────────────────────
    tests_data = sheets_service.get_all_records("tests")
    tests = [
        {
            "date": str(row["Date"]),
            "subject": str(row["Subject"]),
            "marks": float(row["Marks"] if row["Marks"] != "" else 0),
        }
        for row in tests_data if match_row(row)
    ]

    # ── exams sheet ─────────────────────────────────────────────────────────
    exams_data = sheets_service.get_all_records("exams")
    exams = [
        {
            "date": str(row["Date"]),
            "subject": str(row["Subject"]),
            "marks": float(row["Marks"] if row["Marks"] != "" else 0),
        }
        for row in exams_data if match_row(row)
    ]

    return {
        "student": student,
        "attendance": attendance,
        "tests": tests,
        "exams": exams,
    }


# ── quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json, sys
    if len(sys.argv) < 3:
        print("Usage: python3 execution/fetch_student_data.py <roll> <class> [name]")
        sys.exit(1)
        
    roll = sys.argv[1]
    cls = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else None
    
    data = fetch_student_data(roll, cls, name)
    print(json.dumps(data, indent=2))
