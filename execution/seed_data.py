import sys
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service

load_dotenv()

TEST_CLASSES = ["10A", "10B", "9A", "9B", "8A"]
SUBJECTS = ["Maths", "Science", "English", "History", "Physics"]
FIRST_NAMES = ["Rahul", "Priya", "Amit", "Anjali", "Suresh", "Meera", "Vikram", "Sita", "Arjun", "Kavita"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Reddy", "Iyer", "Nair", "Das", "Joshi"]

def seed_data():
    print("--- Initializing MySQL Database & Tables ---")
    db_service.init_db()

    print("--- Clearing existing data ---")
    db_service.execute_query("TRUNCATE TABLE exams")
    db_service.execute_query("TRUNCATE TABLE tests")
    db_service.execute_query("TRUNCATE TABLE attendance")
    db_service.execute_query("DELETE FROM students")

    # 1. Generate 50 Students
    print("--- Generating 50 Students ---")
    students = []
    student_args = []
    for i in range(1, 51):
        roll = str(i)
        cls = random.choice(TEST_CLASSES)
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        students.append({"roll": roll, "class": cls, "name": name})
        student_args.append((roll, cls, name))

    query_students = "INSERT INTO students (roll_no, class_name, name) VALUES (%s, %s, %s)"
    db_service.execute_many(query_students, student_args)

    # 2. Generate 6 Months of Records (Attendance, Tests, Exams)
    start_date = datetime.now() - timedelta(days=180)

    attendance_args = []
    test_args = []
    exam_args = []

    print("--- Generating 6 Months of Records ---")
    for s in students:
        # Attendance: Daily for 180 days
        for day in range(180):
            date_str = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
            status = "P" if random.random() < 0.85 else "A"
            attendance_args.append((s["roll"], s["class"], date_str, status))

        # Tests: Every month (6 tests total per student)
        for t in range(6):
            date_str = (start_date + timedelta(days=t*30 + 15)).strftime("%Y-%m-%d")
            subj = random.choice(SUBJECTS)
            marks = random.randint(40, 100)
            test_args.append((s["roll"], s["class"], date_str, subj, marks))

        # Exams: 2 Exams (Mid-term and Final)
        for e in range(2):
            date_str = (start_date + timedelta(days=e*90 + 80)).strftime("%Y-%m-%d")
            subj = random.choice(SUBJECTS)
            marks = random.randint(35, 98)
            exam_args.append((s["roll"], s["class"], date_str, subj, marks))

    print("--- Writing Data to MySQL ---")
    db_service.execute_many("INSERT INTO attendance (roll_no, class_name, date, status) VALUES (%s, %s, %s, %s)", attendance_args)
    db_service.execute_many("INSERT INTO tests (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)", test_args)
    db_service.execute_many("INSERT INTO exams (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)", exam_args)

    print("✅ SUCCESS! 50 students and 6 months of data populated into MySQL.")

if __name__ == "__main__":
    seed_data()
