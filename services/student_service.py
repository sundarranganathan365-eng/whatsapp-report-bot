import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.sheets_service import sheets_service

class StudentService:
    SHEET_NAME = "students"

    @classmethod
    def get_all_students(cls, search_query=None):
        records = sheets_service.get_all_records(cls.SHEET_NAME)
        
        normalized_records = []
        for row in records:
            # Case-insensitive header matching
            row_lower = {str(k).strip().lower(): v for k, v in row.items()}
            
            roll_no = str(row_lower.get("roll no", "")).strip()
            if not roll_no: continue
            
            name = str(row_lower.get("name", "")).strip()
            class_name = str(row_lower.get("class", "")).strip().upper()
            
            student = {
                "roll_no": roll_no,
                "name": name,
                "class_name": class_name,
                "original_row": row
            }
            normalized_records.append(student)

        if search_query:
            search_query = str(search_query).lower()
            normalized_records = [
                s for s in normalized_records 
                if search_query in s["name"].lower() or search_query in s["roll_no"].lower()
            ]

        return normalized_records

    @classmethod
    def _find_row_index(cls, roll_no: str, class_name: str):
        # We need to find the absolute row index (1-based, including header)
        records = sheets_service.get_all_records(cls.SHEET_NAME)
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()
        
        for idx, row in enumerate(records):
            row_roll = str(row.get("Roll No", "")).strip()
            row_class = str(row.get("Class", "")).strip().upper()
            if row_roll == roll_no and row_class == class_name:
                return idx + 2 # idx 0 corresponds to row 2 in sheets
        return None

    @classmethod
    def get_student_by_roll_no(cls, roll_no: str, class_name: str):
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()
        records = cls.get_all_students()
        for s in records:
            if s["roll_no"] == roll_no and s["class_name"] == class_name:
                return s
        return None

    @classmethod
    def add_student(cls, roll_no: str, name: str, class_name: str):
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()
        existing = cls._find_row_index(roll_no, class_name)
        if existing is not None:
            raise ValueError(f"Student with Roll No {roll_no} in Class {class_name} already exists.")
        
        ws = sheets_service.get_worksheet(cls.SHEET_NAME)
        headers = ws.row_values(1)
        
        row_data = []
        for header in headers:
            h = header.strip().lower()
            if h == "roll no": row_data.append(roll_no)
            elif h == "name": row_data.append(name)
            elif h == "class": row_data.append(class_name)
            else: row_data.append("")

        sheets_service.append_row(cls.SHEET_NAME, row_data)
        return {"roll_no": roll_no, "name": name, "class_name": class_name}

    @classmethod
    def update_student(cls, original_roll_no: str, original_class: str, name: str, new_class: str):
        # Note: In this generic update, we find by original keys
        row_index = cls._find_row_index(original_roll_no, original_class)
        if row_index is None:
            raise ValueError(f"Student not found.")

        ws = sheets_service.get_worksheet(cls.SHEET_NAME)
        headers = ws.row_values(1)
        
        row_data = []
        for header in headers:
            h = header.strip().lower()
            if h == "roll no": row_data.append(original_roll_no)
            elif h == "name": row_data.append(name)
            elif h == "class": row_data.append(new_class)
            else: row_data.append("")

        sheets_service.update_row(cls.SHEET_NAME, row_index, row_data)
        return {"roll_no": original_roll_no, "name": name, "class_name": new_class}

    @classmethod
    def delete_student(cls, roll_no: str, class_name: str):
        row_index = cls._find_row_index(roll_no, class_name)
        if row_index is None:
            raise ValueError(f"Student not found.")

        sheets_service.delete_row(cls.SHEET_NAME, row_index)
        return True

student_service = StudentService()
