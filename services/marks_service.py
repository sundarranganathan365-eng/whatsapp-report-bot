import sys, os
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.sheets_service import sheets_service

class MarksService:
    @classmethod
    def get_marks(cls, sheet_type: str, roll_no: str, class_name: str) -> List[Dict]:
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid sheet type. Must be 'tests' or 'exams'.")
            
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()
        records = sheets_service.get_all_records(sheet_type)
        
        results = []
        for row in records:
            row_roll = str(row.get("Roll No", "")).strip()
            row_class = str(row.get("Class", "")).strip().upper()
            if row_roll == roll_no and row_class == class_name:
                results.append(row)
        return results

    @classmethod
    def add_mark(cls, sheet_type: str, roll_no: str, subject: str, date: str, marks: float, class_name: str):
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid sheet type. Must be 'tests' or 'exams'.")
            
        ws = sheets_service.get_worksheet(sheet_type)
        headers = ws.row_values(1)
        
        row_data = []
        for header in headers:
            h = header.strip().lower()
            if h == "roll no":
                row_data.append(roll_no)
            elif h == "date":
                row_data.append(date)
            elif h == "subject":
                row_data.append(subject)
            elif h == "marks":
                row_data.append(marks)
            elif h == "class":
                row_data.append(class_name)
            else:
                row_data.append("")
                
        sheets_service.append_row(sheet_type, row_data)
        return {"roll_no": roll_no, "subject": subject, "date": date, "marks": marks}

    @classmethod
    def add_marks_bulk(cls, sheet_type: str, records: List[Dict]):
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid sheet type. Must be 'tests' or 'exams'.")
        if not records:
            return []
            
        ws = sheets_service.get_worksheet(sheet_type)
        headers = ws.row_values(1)
        
        all_rows = []
        for r in records:
            row_data = []
            for header in headers:
                h = header.strip().lower()
                if h == "roll no": row_data.append(r.get("roll_no", ""))
                elif h == "date": row_data.append(r.get("date", ""))
                elif h == "subject": row_data.append(r.get("subject", ""))
                elif h == "marks": row_data.append(r.get("marks", 0))
                elif h == "class": row_data.append(r.get("class_name", ""))
                else: row_data.append("")
            all_rows.append(row_data)
            
        sheets_service.append_rows(sheet_type, all_rows)
        return records

    @classmethod
    def delete_mark(cls, sheet_type: str, roll_no: str, subject: str, date: str, class_name: str):
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid sheet type.")
            
        roll_no = str(roll_no).strip()
        subject = str(subject).strip().lower()
        date = str(date).strip()
        class_name = str(class_name).strip().upper()
        
        records = sheets_service.get_all_records(sheet_type)
        row_idx_to_delete = None
        for idx, row in enumerate(records):
            row_roll = str(row.get("Roll No", "")).strip()
            row_class = str(row.get("Class", "")).strip().upper()
            row_date = str(row.get("Date", "")).strip()
            row_subj = str(row.get("Subject", "")).strip().lower()
            
            if row_roll == roll_no and row_class == class_name and row_date == date and row_subj == subject:
                row_idx_to_delete = idx + 2
                break
                
        if row_idx_to_delete is None:
            raise ValueError(f"Mark record not found in {sheet_type}.")
            
        sheets_service.delete_row(sheet_type, row_idx_to_delete)
        return True

marks_service = MarksService()
