import sys
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service

load_dotenv()

TEST_CLASSES = ["8", "9", "10"]
SUBJECTS = ["Maths", "Science", "English", "History", "Physics"]
FIRST_NAMES = ["Rahul", "Priya", "Amit", "Anjali", "Suresh", "Meera", "Vikram", "Sita", "Arjun", "Kavita", "Sneha", "Rohan", "Pooja", "Karan", "Aarti"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Reddy", "Iyer", "Nair", "Das", "Joshi", "Kumar"]

def seed_data():
    print("--- Initializing MySQL Database & Tables ---")
    db_service.init_db()

    print("--- Clearing existing data ---")
    db_service.execute_query("TRUNCATE TABLE exams")
    db_service.execute_query("TRUNCATE TABLE tests")
    db_service.execute_query("TRUNCATE TABLE attendance")
    db_service.execute_query("DELETE FROM students")

    # Generate 150 Students (Roll 1-50 for EACH class 8, 9, 10)
    print("--- Generating 150 Students (Roll 1-50 per class) ---")
    students = []
    student_args = []
    for cls in TEST_CLASSES:
        for roll_i in range(1, 51):
            roll = str(roll_i)
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            students.append({"roll": roll, "class": cls, "name": name})
            student_args.append((roll, cls, name))

    query_students = "INSERT INTO students (roll_no, class_name, name) VALUES (%s, %s, %s)"
    db_service.execute_many(query_students, student_args)

    # Generate 6 Months of Records (Attendance, Tests, Exams)
    start_date = datetime.now() - timedelta(days=180)

    attendance_args = []
    test_args = []
    exam_args = []

    print("--- Generating 6 Months of Records for all 150 students ---")
    for s in students:
        # Attendance: Daily for 180 days
        for day_offset in range(180):
            d = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            status = "Present" if random.random() > 0.15 else "Absent"
            attendance_args.append((s["roll"], s["class"], d, status))

        # Tests: ~6 periodic tests per student
        for t_idx in range(6):
            t_date = (start_date + timedelta(days=t_idx * 28 + random.randint(1, 5))).strftime("%Y-%m-%d")
            subj = random.choice(SUBJECTS)
            marks = round(random.uniform(45, 98), 1)
            test_args.append((s["roll"], s["class"], t_date, subj, marks))

        # Exams: ~2 exams per student
        for e_idx in range(2):
            e_date = (start_date + timedelta(days=e_idx * 75 + 30)).strftime("%Y-%m-%d")
            subj = random.choice(SUBJECTS)
            marks = round(random.uniform(40, 99), 1)
            exam_args.append((s["roll"], s["class"], e_date, subj, marks))

    print("--- Writing Data to MySQL ---")
    db_service.execute_many("INSERT INTO attendance (roll_no, class_name, date, status) VALUES (%s, %s, %s, %s)", attendance_args)
    db_service.execute_many("INSERT INTO tests (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)", test_args)
    db_service.execute_many("INSERT INTO exams (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)", exam_args)

    print("✅ SUCCESS! 150 students (Roll 1-50 for Classes 8, 9, 10) & 6 months data populated into MySQL.")

if __name__ == "__main__":
    seed_data()
