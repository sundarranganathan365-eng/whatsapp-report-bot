import sys
import os
import random

# Ensure parent dir is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from services.sheets_service import sheets_service

def repopulate():
    print("🚀 Starting Data Repopulation...")
    
    # 1. Clear existing data (headers should stay in row 1)
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
        ws.clear() # Clear everything
        ws.update("A1", [headers]) # Restore correct headers
    
    # 2. Student Generation
    first_names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Suresh", "Meena", "Arjun", "Kavita", 
                   "Vijay", "Rani", "Rohan", "Sonal", "Karan", "Pooja", "Deepak", "Aarti", "Aditya", "Neha"]
    last_names = ["Kumar", "Sharma", "Verma", "Singh", "Patel", "Gupta", "Joshi", "Das", "Reddy", "Nair"]
    
    students_to_add = []
    standards = ["8", "9", "10"]
    
    for std in standards:
        print(f"📝 Generating 50 students for Standard {std}th...")
        for roll in range(1, 51):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            # Map to headers: ['Roll No', 'Class', 'Name']
            students_to_add.append([str(roll), std, name])
            
    # Batch append students
    sheets_service.append_rows("students", students_to_add)
    print(f"✅ Successfully added {len(students_to_add)} students.")

    # 3. Optional: Add some dummy attendance for verification
    # Let's say we mark Everyone in 10th grade as Present for today 2024-04-08
    print("📅 Adding dummy attendance for today...")
    attendance_to_add = []
    for roll in range(1, 51):
        # Headers: ['Roll No', 'Class', 'Date', 'Status']
        attendance_to_add.append([str(roll), "10", "2024-04-08", "Present"])
    
    sheets_service.append_rows("attendance", attendance_to_add)
    print("✅ Dummy data added.")

if __name__ == "__main__":
    repopulate()
