import os
import random
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# Configuration
TEST_CLASSES = ["10A", "10B", "9A", "9B", "8A"]
SUBJECTS = ["Maths", "Science", "English", "History", "Physics"]
FIRST_NAMES = ["Rahul", "Priya", "Amit", "Anjali", "Suresh", "Meera", "Vikram", "Sita", "Arjun", "Kavita"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Reddy", "Iyer", "Nair", "Das", "Joshi"]

def get_sheet_client():
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    return gspread.authorize(creds)

def seed_data():
    sheet_id = os.getenv("GOOGLE_SHEETS_KEY")
    client = get_sheet_client()
    ss = client.open_by_key(sheet_id)

    # 1. Clear and setup headers
    tabs = {
        "students": ["Roll No", "Class", "Name"],
        "attendance": ["Roll No", "Class", "Date", "Status"],
        "tests": ["Roll No", "Class", "Date", "Subject", "Marks"],
        "exams": ["Roll No", "Class", "Date", "Subject", "Marks"]
    }

    print("--- Clearing sheets and setting headers ---")
    for name, headers in tabs.items():
        ws = ss.worksheet(name)
        ws.clear()
        ws.update("A1", [headers])

    # 2. Generate 50 Students
    print("--- Generating 50 Students ---")
    students = []
    student_rows = []
    for i in range(1, 51):
        roll = str(i)
        cls = random.choice(TEST_CLASSES)
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        students.append({"roll": roll, "class": cls, "name": name})
        student_rows.append([roll, cls, name])
    
    ss.worksheet("students").append_rows(student_rows)

    # 3. Generate 6 Months of Records (Attendance, Tests, Exams)
    # 180 days back from today
    start_date = datetime.now() - timedelta(days=180)
    
    attendance_rows = []
    test_rows = []
    exam_rows = []

    print("--- Generating 6 Months of Records ---")
    for s in students:
        # Attendance: Daily for 180 days
        for day in range(180):
            date_str = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
            # 85% attendance rate
            status = "P" if random.random() < 0.85 else "A"
            attendance_rows.append([s["roll"], s["class"], date_str, status])

        # Tests: Every month (6 tests total per student)
        for t in range(6):
            date_str = (start_date + timedelta(days=t*30 + 15)).strftime("%Y-%m-%d")
            subj = random.choice(SUBJECTS)
            marks = random.randint(40, 100)
            test_rows.append([s["roll"], s["class"], date_str, subj, marks])

        # Exams: 2 Exams (Mid-term and Final)
        for e in range(2):
            date_str = (start_date + timedelta(days=e*90 + 80)).strftime("%Y-%m-%d")
            subj = random.choice(SUBJECTS)
            marks = random.randint(35, 98)
            exam_rows.append([s["roll"], s["class"], date_str, subj, marks])

    # Batch append for performance
    print("--- Writing Data to Sheets (this may take a minute) ---")
    ss.worksheet("attendance").append_rows(attendance_rows)
    ss.worksheet("tests").append_rows(test_rows)
    ss.worksheet("exams").append_rows(exam_rows)

    print("✅ SUCCESS! 50 students and 6 months of data populated.")

if __name__ == "__main__":
    seed_data()
