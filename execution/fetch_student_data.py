"""
fetch_student_data.py
---------------------
Connects to Google Sheets and fetches all rows related to a given roll number.

Required env vars:
  GOOGLE_SHEETS_KEY         — The Spreadsheet ID from the Google Sheet URL
  GOOGLE_CREDENTIALS_PATH   — Path to the service account credentials.json
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_sheet_client():
    """Authenticate and return a gspread client."""
    import json
    
    # Priority 1: Check for raw JSON string in env (Best for Cloud/Render)
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        try:
            info = json.loads(creds_json)
            creds = Credentials.from_service_account_info(info, scopes=SCOPES)
            return gspread.authorize(creds)
        except Exception as e:
            print(f"⚠️ Error parsing GOOGLE_CREDENTIALS_JSON: {e}")

    # Priority 2: Check for file path (Best for local dev)
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    if os.path.exists(creds_path):
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        return gspread.authorize(creds)
    
    raise FileNotFoundError(
        "No Google credentials found! Set GOOGLE_CREDENTIALS_JSON in env "
        "or provide a credentials.json file."
    )


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

    sheet_id = os.getenv("GOOGLE_SHEETS_KEY")
    if not sheet_id:
        raise EnvironmentError(
            "GOOGLE_SHEETS_KEY is not set. Add it to your .env file."
        )

    client = get_sheet_client()
    spreadsheet = client.open_by_key(sheet_id)

    # ── students sheet ──────────────────────────────────────────────────────
    students_ws = spreadsheet.worksheet("students")
    students_data = students_ws.get_all_records()

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
    attendance_ws = spreadsheet.worksheet("attendance")
    attendance_data = attendance_ws.get_all_records()
    attendance = [
        {"date": str(row["Date"]), "status": str(row["Status"]).strip()}
        for row in attendance_data if match_row(row)
    ]

    # ── tests sheet ─────────────────────────────────────────────────────────
    tests_ws = spreadsheet.worksheet("tests")
    tests_data = tests_ws.get_all_records()
    tests = [
        {
            "date": str(row["Date"]),
            "subject": str(row["Subject"]),
            "marks": float(row["Marks"] if row["Marks"] != "" else 0),
        }
        for row in tests_data if match_row(row)
    ]

    # ── exams sheet ─────────────────────────────────────────────────────────
    exams_ws = spreadsheet.worksheet("exams")
    exams_data = exams_ws.get_all_records()
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
