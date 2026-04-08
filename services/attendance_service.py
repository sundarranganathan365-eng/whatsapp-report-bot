import sys, os
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.sheets_service import sheets_service

class AttendanceService:
    SHEET_NAME = "attendance"

    @classmethod
    def get_attendance(cls, roll_no: str, class_name: str) -> List[Dict]:
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()
        records = sheets_service.get_all_records(cls.SHEET_NAME)
        
        results = []
        for row in records:
            row_roll = str(row.get("Roll No", "")).strip()
            row_class = str(row.get("Class", "")).strip().upper()
            if row_roll == roll_no and row_class == class_name:
                results.append(row)
        return results

    @classmethod
    def add_attendance(cls, roll_no: str, date: str, status: str, class_name: str):
        ws = sheets_service.get_worksheet(cls.SHEET_NAME)
        headers = ws.row_values(1)
        
        row_data = []
        for header in headers:
            h = header.strip().lower()
            if h == "roll no":
                row_data.append(roll_no)
            elif h == "date":
                row_data.append(date)
            elif h == "status":
                row_data.append(status)
            elif h == "class":
                row_data.append(class_name)
            else:
                row_data.append("")
                
        # Optional: Prevent duplicates for same day/student/class
        # cls.delete_attendance(roll_no, date, class_name) # Un-comment to overwrite

        sheets_service.append_row(cls.SHEET_NAME, row_data)
        return {"roll_no": roll_no, "date": date, "status": status}

    @classmethod
    def add_attendance_bulk(cls, records: List[Dict]):
        if not records:
            return []
            
        ws = sheets_service.get_worksheet(cls.SHEET_NAME)
        headers = ws.row_values(1)
        
        all_rows = []
        for r in records:
            row_data = []
            for header in headers:
                h = header.strip().lower()
                if h == "roll no": row_data.append(r.get("roll_no", ""))
                elif h == "date": row_data.append(r.get("date", ""))
                elif h == "status": row_data.append(r.get("status", ""))
                elif h == "class": row_data.append(r.get("class_name", ""))
                else: row_data.append("")
            all_rows.append(row_data)
            
        sheets_service.append_rows(cls.SHEET_NAME, all_rows)
        return records

    @classmethod
    def delete_attendance(cls, roll_no: str, date: str, class_name: str):
        roll_no = str(roll_no).strip()
        date = str(date).strip()
        class_name = str(class_name).strip().upper()
        
        records = sheets_service.get_all_records(cls.SHEET_NAME)
        row_idx_to_delete = None
        for idx, row in enumerate(records):
            row_roll = str(row.get("Roll No", "")).strip()
            row_class = str(row.get("Class", "")).strip().upper()
            row_date = str(row.get("Date", "")).strip()
            if row_roll == roll_no and row_class == class_name and row_date == date:
                row_idx_to_delete = idx + 2 # +2 because 1-based indexing and header row
                break
                
        if row_idx_to_delete is None:
            raise ValueError("Attendance record not found.")
            
        sheets_service.delete_row(cls.SHEET_NAME, row_idx_to_delete)
        return True

attendance_service = AttendanceService()
