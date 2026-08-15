"""
fetch_student_data.py
---------------------
Connects to MySQL database and fetches all records related to a given roll number and class.
"""

import sys
import os

# Ensure the parent directory is in the system path to allow importing from 'services'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service
from dotenv import load_dotenv

load_dotenv()

def fetch_student_data(roll_no: str, class_name: str, student_name: str = None) -> dict:
    """
    Fetch all data for a student identified by roll_no and class_name from MySQL.

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

    # 1. Fetch Student Metadata
    if student_name:
        query_student = "SELECT roll_no, class_name, name FROM students WHERE roll_no = %s AND UPPER(class_name) = %s AND LOWER(name) LIKE %s"
        student_row = db_service.execute_query(query_student, (roll_no, class_name, f"%{student_name.strip().lower()}%"), fetchone=True)
    else:
        query_student = "SELECT roll_no, class_name, name FROM students WHERE roll_no = %s AND UPPER(class_name) = %s"
        student_row = db_service.execute_query(query_student, (roll_no, class_name), fetchone=True)

    if not student_row:
        raise ValueError(f"Student not found for Roll No '{roll_no}' in Class '{class_name}'.")

    student = {
        "roll_no": str(student_row["roll_no"]).strip(),
        "name": str(student_row["name"]).strip(),
        "class": str(student_row["class_name"]).strip().upper(),
    }

    # 2. Fetch Attendance Records
    query_attendance = "SELECT date, status FROM attendance WHERE roll_no = %s AND UPPER(class_name) = %s ORDER BY date ASC"
    att_rows = db_service.execute_query(query_attendance, (roll_no, class_name))
    attendance = [
        {"date": str(r["date"]), "status": str(r["status"]).strip()}
        for r in att_rows
    ]

    # 3. Fetch Test Marks
    query_tests = "SELECT date, subject, marks FROM tests WHERE roll_no = %s AND UPPER(class_name) = %s ORDER BY date ASC"
    test_rows = db_service.execute_query(query_tests, (roll_no, class_name))
    tests = [
        {
            "date": str(r["date"]),
            "subject": str(r["subject"]).strip(),
            "marks": float(r["marks"]),
        }
        for r in test_rows
    ]

    # 4. Fetch Exam Marks
    query_exams = "SELECT date, subject, marks FROM exams WHERE roll_no = %s AND UPPER(class_name) = %s ORDER BY date ASC"
    exam_rows = db_service.execute_query(query_exams, (roll_no, class_name))
    exams = [
        {
            "date": str(r["date"]),
            "subject": str(r["subject"]).strip(),
            "marks": float(r["marks"]),
        }
        for r in exam_rows
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
