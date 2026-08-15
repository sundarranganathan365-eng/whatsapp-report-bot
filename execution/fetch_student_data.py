"""
fetch_student_data.py
---------------------
Connects to MySQL database and fetches all records related to a given roll number and class.
Supports flexible lookup, numeric grade extraction (e.g. '10A' -> '10'), and fallback student generation.
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service
from dotenv import load_dotenv

load_dotenv()

def fetch_student_data(roll_no: str, class_name: str, student_name: str = None) -> dict:
    """
    Fetch all data for a student identified by roll_no, class_name, or student_name from MySQL.
    Always returns valid student data structure with fallback matching.
    """
    roll_no = str(roll_no).strip()
    raw_cls = str(class_name).strip()
    
    # Extract numeric grade e.g. '10A' -> '10'
    m_cls = re.search(r'\d+', raw_cls)
    cls_input = m_cls.group(0) if m_cls else raw_cls.upper()

    student_row = None

    # 1. Exact roll_no and class match
    q1 = "SELECT roll_no, class_name, name FROM students WHERE roll_no = %s AND (UPPER(class_name) = %s OR UPPER(class_name) = %s)"
    student_row = db_service.execute_query(q1, (roll_no, cls_input, raw_cls.upper()), fetchone=True)

    # 2. Match roll_no and class starting with class_name (e.g. '8' -> '8A')
    if not student_row:
        q2 = "SELECT roll_no, class_name, name FROM students WHERE roll_no = %s AND UPPER(class_name) LIKE %s"
        student_row = db_service.execute_query(q2, (roll_no, f"{cls_input}%"), fetchone=True)

    # 3. Match by student_name if provided
    if not student_row and student_name:
        q3 = "SELECT roll_no, class_name, name FROM students WHERE LOWER(name) LIKE %s"
        student_row = db_service.execute_query(q3, (f"%{student_name.strip().lower()}%",), fetchone=True)

    # 4. Match by roll_no alone
    if not student_row:
        q4 = "SELECT roll_no, class_name, name FROM students WHERE roll_no = %s LIMIT 1"
        student_row = db_service.execute_query(q4, (roll_no,), fetchone=True)

    # 5. Fallback: Create student record on the fly if roll/class combo not found
    if not student_row:
        fallback_name = student_name.strip() if student_name else f"Student {roll_no}"
        db_service.execute_query(
            "INSERT INTO students (roll_no, class_name, name) VALUES (%s, %s, %s)",
            (roll_no, cls_input, fallback_name)
        )
        student_row = {"roll_no": roll_no, "class_name": cls_input, "name": fallback_name}

    real_roll = str(student_row["roll_no"]).strip()
    real_class = str(student_row["class_name"]).strip().upper()

    m_real = re.search(r'\d+', real_class)
    display_class = m_real.group(0) if m_real else real_class

    student = {
        "roll_no": real_roll,
        "name": str(student_row["name"]).strip(),
        "class": display_class,
        "raw_class": real_class,
    }

    # Fetch Attendance Records
    query_attendance = "SELECT date, status FROM attendance WHERE roll_no = %s AND (UPPER(class_name) = %s OR UPPER(class_name) = %s) ORDER BY date ASC"
    att_rows = db_service.execute_query(query_attendance, (real_roll, real_class, display_class))
    attendance = [
        {"date": str(r["date"]), "status": str(r["status"]).strip()}
        for r in att_rows
    ]

    # Fetch Test Marks
    query_tests = "SELECT date, subject, marks FROM tests WHERE roll_no = %s AND (UPPER(class_name) = %s OR UPPER(class_name) = %s) ORDER BY date ASC"
    test_rows = db_service.execute_query(query_tests, (real_roll, real_class, display_class))
    tests = [
        {
            "date": str(r["date"]),
            "subject": str(r["subject"]).strip(),
            "marks": float(r["marks"]),
        }
        for r in test_rows
    ]

    # Fetch Exam Marks
    query_exams = "SELECT date, subject, marks FROM exams WHERE roll_no = %s AND (UPPER(class_name) = %s OR UPPER(class_name) = %s) ORDER BY date ASC"
    exam_rows = db_service.execute_query(query_exams, (real_roll, real_class, display_class))
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
