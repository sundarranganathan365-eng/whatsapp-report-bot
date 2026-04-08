import sys
import os
import random
from datetime import datetime, timedelta

# Ensure parent dir is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from services.sheets_service import sheets_service

def repopulate():
    print("🚀 Starting 6-Month Bulk Data Repopulation...")
    
    # 1. Clear existing data and ENSURE HEADERS
    sheet_headers = {
        "students": ["Roll No", "Class", "Name"],
        "attendance": ["Roll No", "Class", "Date", "Status"],
        "tests": ["Roll No", "Class", "Subject", "Date", "Marks", "Out Of"],
        "exams": ["Roll No", "Class", "Subject", "Date", "Marks", "Out Of"]
    }

    for sheet, headers in sheet_headers.items():
        print(f"🧹 Clearing and resetting headers: {sheet}")
        ws = sheets_service.get_worksheet(sheet)
        ws.clear()
        ws.update("A1", [headers])
    
    # 2. Student Generation
    first_names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Suresh", "Meena", "Arjun", "Kavita", 
                   "Vijay", "Rani", "Rohan", "Sonal", "Karan", "Pooja", "Deepak", "Aarti", "Aditya", "Neha"]
    last_names = ["Kumar", "Sharma", "Verma", "Singh", "Patel", "Gupta", "Joshi", "Das", "Reddy", "Nair"]
    
    students = [] # List of tuples (roll, class, name)
    students_rows = []
    standards = ["8", "9", "10"]
    
    for std in standards:
        for roll in range(1, 51):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            students.append((str(roll), std, name))
            students_rows.append([str(roll), std, name])
            
    sheets_service.append_rows("students", students_rows)
    print(f"✅ Generated 150 students.")

    # 3. Time-based Data Generation (Attendance, Tests, Exams)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    attendance_rows = []
    tests_rows = []
    exams_rows = []
    
    current_date = start_date
    test_counter = 0
    
    print(f"📅 Generating history from {start_date.date()} to {end_date.date()}...")
    
    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() < 5:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Attendance for all students
            for roll, std, name in students:
                status = "Present" if random.random() < 0.9 else "Absent"
                attendance_rows.append([roll, std, date_str, status])
            
            # Tests every ~25 days
            test_counter += 1
            if test_counter % 25 == 0:
                for roll, std, name in students:
                    for sub in ["Math", "Science"]:
                        marks = random.randint(40, 95)
                        tests_rows.append([roll, std, sub, date_str, str(marks), "100"])
            
            # Exams (Mid-term around day 90)
            if test_counter == 90:
                print(f"📝 Adding Mid-term Exam data for {date_str}...")
                for roll, std, name in students:
                    for sub in ["Math", "Science"]:
                        marks = random.randint(45, 98)
                        exams_rows.append([roll, std, sub, date_str, str(marks), "100"])

        current_date += timedelta(days=1)

    print("📤 Uploading Attendance (Slow batching)...")
    # Batch attendance in chunks of 5000 to prevent timeouts
    for i in range(0, len(attendance_rows), 5000):
        sheets_service.append_rows("attendance", attendance_rows[i:i+5000])
        print(f"   - Uploaded {min(i+5000, len(attendance_rows))}/{len(attendance_rows)} rows")

    print("📤 Uploading Tests...")
    sheets_service.append_rows("tests", tests_rows)
    
    print("📤 Uploading Exams...")
    sheets_service.append_rows("exams", exams_rows)

    print("✅ Full 6-Month Data Repopulation Complete!")

if __name__ == "__main__":
    repopulate()
