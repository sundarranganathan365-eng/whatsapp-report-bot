import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from services.db_service import db_service

def repopulate():
    print("🚀 Starting 6-Month Bulk Data Repopulation for MySQL...")
    
    # 1. Clear existing data
    print("🧹 Clearing MySQL tables...")
    db_service.init_db()
    db_service.execute_query("TRUNCATE TABLE exams")
    db_service.execute_query("TRUNCATE TABLE tests")
    db_service.execute_query("TRUNCATE TABLE attendance")
    db_service.execute_query("DELETE FROM students")
    
    # 2. Student Generation
    first_names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Suresh", "Meena", "Arjun", "Kavita", 
                   "Vijay", "Rani", "Rohan", "Sonal", "Karan", "Pooja", "Deepak", "Aarti", "Aditya", "Neha"]
    last_names = ["Kumar", "Sharma", "Verma", "Singh", "Patel", "Gupta", "Joshi", "Das", "Reddy", "Nair"]
    
    students = [] # List of tuples (roll, class, name)
    student_args = []
    standards = ["8", "9", "10"]
    
    for std in standards:
        for roll in range(1, 51):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            students.append((str(roll), std, name))
            student_args.append((str(roll), std, name))
            
    db_service.execute_many("INSERT INTO students (roll_no, class_name, name) VALUES (%s, %s, %s)", student_args)
    print(f"✅ Generated 150 students.")

    # 3. Time-based Data Generation (Attendance, Tests, Exams)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    attendance_args = []
    tests_args = []
    exams_args = []
    
    current_date = start_date
    test_counter = 0
    
    print(f"📅 Generating history from {start_date.date()} to {end_date.date()}...")
    
    while current_date <= end_date:
        if current_date.weekday() < 5: # Weekdays
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Attendance for all students
            for roll, std, name in students:
                status = "P" if random.random() < 0.9 else "A"
                attendance_args.append((roll, std, date_str, status))
            
            # Tests every ~25 days
            test_counter += 1
            if test_counter % 25 == 0:
                for roll, std, name in students:
                    for sub in ["Math", "Science"]:
                        marks = random.randint(40, 95)
                        tests_args.append((roll, std, date_str, sub, marks))
            
            # Exams (Mid-term around day 90)
            if test_counter == 90:
                print(f"📝 Adding Mid-term Exam data for {date_str}...")
                for roll, std, name in students:
                    for sub in ["Math", "Science"]:
                        marks = random.randint(45, 98)
                        exams_args.append((roll, std, date_str, sub, marks))

        current_date += timedelta(days=1)

    print("📤 Inserting Attendance records into MySQL...")
    db_service.execute_many("INSERT INTO attendance (roll_no, class_name, date, status) VALUES (%s, %s, %s, %s)", attendance_args)

    print("📤 Inserting Tests records into MySQL...")
    db_service.execute_many("INSERT INTO tests (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)", tests_args)
    
    print("📤 Inserting Exams records into MySQL...")
    db_service.execute_many("INSERT INTO exams (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)", exams_args)

    print("✅ Full 6-Month Data Repopulation Complete!")

if __name__ == "__main__":
    repopulate()
