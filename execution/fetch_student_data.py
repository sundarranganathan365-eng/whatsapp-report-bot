"""
fetch_student_data.py
---------------------
Connects to MySQL database and fetches all records related to a given roll number and class.
Supports flexible lookup (e.g. Class '8' matches '8A', name fallback).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service
from dotenv import load_dotenv

load_dotenv()

def fetch_student_data(roll_no: str, class_name: str, student_name: str = None) -> dict:
    """
    Fetch all data for a student identified by roll_no, class_name, or student_name from MySQL.
    """
    roll_no = str(roll_no).strip()
    cls_input = str(class_name).strip().upper()

    student_row = None

    # Helper function to query student
    def find_student(r_no, c_name, s_name):
        # Exact roll + exact class
        q1 = "SELECT roll_no, class_name, name FROM students WHERE roll_no = %s AND UPPER(class_name) = %s"
        res = db_service.execute_query(q1, (r_no, c_name), fetchone=True)
        if res:
            return res

        # Exact roll + prefix class (e.g. '8' -> '8A')
        q2 = "SELECT roll_no, class_name, name FROM students WHERE roll_no = %s AND UPPER(class_name) LIKE %s"
        res = db_service.execute_query(q2, (r_no, f"{c_name}%"), fetchone=True)
        if res:
            return res

        # Name match in class
        if s_name:
            q3 = "SELECT roll_no, class_name, name FROM students WHERE LOWER(name) LIKE %s AND (UPPER(class_name) = %s OR UPPER(class_name) LIKE %s)"
            res = db_service.execute_query(q3, (f"%{s_name.strip().lower()}%", c_name, f"{c_name}%"), fetchone=True)
            if res:
                return res

        return None

    student_row = find_student(roll_no, cls_input, student_name)

    if not student_row:
        # Fallback: find any student matching name across all classes
        if student_name:
            q_name = "SELECT roll_no, class_name, name FROM students WHERE LOWER(name) LIKE %s"
            student_row = db_service.execute_query(q_name, (f"%{student_name.strip().lower()}%",), fetchone=True)

    if not student_row:
        raise ValueError(f"Student not found for Roll No '{roll_no}' in Class '{class_name}'.")

    real_roll = str(student_row["roll_no"]).strip()
    real_class = str(student_row["class_name"]).strip().upper()

    student = {
        "roll_no": real_roll,
        "name": str(student_row["name"]).strip(),
        "class": real_class,
    }

    # Fetch Attendance Records
    query_attendance = "SELECT date, status FROM attendance WHERE roll_no = %s AND UPPER(class_name) = %s ORDER BY date ASC"
    att_rows = db_service.execute_query(query_attendance, (real_roll, real_class))
    attendance = [
        {"date": str(r["date"]), "status": str(r["status"]).strip()}
        for r in att_rows
    ]

    # Fetch Test Marks
    query_tests = "SELECT date, subject, marks FROM tests WHERE roll_no = %s AND UPPER(class_name) = %s ORDER BY date ASC"
    test_rows = db_service.execute_query(query_tests, (real_roll, real_class))
    tests = [
        {
            "date": str(r["date"]),
            "subject": str(r["subject"]).strip(),
            "marks": float(r["marks"]),
        }
        for r in test_rows
    ]

    # Fetch Exam Marks
    query_exams = "SELECT date, subject, marks FROM exams WHERE roll_no = %s AND UPPER(class_name) = %s ORDER BY date ASC"
    exam_rows = db_service.execute_query(query_exams, (real_roll, real_class))
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
