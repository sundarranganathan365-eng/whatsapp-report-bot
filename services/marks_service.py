import sys, os
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service

class MarksService:
    @classmethod
    def get_marks(cls, sheet_type: str, roll_no: str, class_name: str) -> List[Dict]:
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid table type. Must be 'tests' or 'exams'.")

        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()

        table = "tests" if sheet_type == "tests" else "exams"
        query = f"""
            SELECT roll_no, class_name, date, subject, marks 
            FROM {table} 
            WHERE roll_no = %s AND UPPER(class_name) = %s
            ORDER BY date DESC
        """
        records = db_service.execute_query(query, (roll_no, class_name))

        results = []
        for r in records:
            results.append({
                "Roll No": str(r["roll_no"]).strip(),
                "Class": str(r["class_name"]).strip().upper(),
                "Date": str(r["date"]),
                "Subject": str(r["subject"]).strip(),
                "Marks": float(r["marks"])
            })
        return results

    @classmethod
    def add_mark(cls, sheet_type: str, roll_no: str, subject: str, date: str, marks: float, class_name: str):
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid table type. Must be 'tests' or 'exams'.")

        roll_no = str(roll_no).strip()
        subject = str(subject).strip()
        date = str(date).strip()
        marks = float(marks)
        class_name = str(class_name).strip().upper()

        table = "tests" if sheet_type == "tests" else "exams"
        query = f"INSERT INTO {table} (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)"
        db_service.execute_query(query, (roll_no, class_name, date, subject, marks), fetchall=False)
        return {"roll_no": roll_no, "subject": subject, "date": date, "marks": marks, "class_name": class_name}

    @classmethod
    def add_marks_bulk(cls, sheet_type: str, records: List[Dict]):
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid table type. Must be 'tests' or 'exams'.")
        if not records:
            return []

        args_list = []
        for r in records:
            args_list.append((
                str(r.get("roll_no", "")).strip(),
                str(r.get("class_name", "")).strip().upper(),
                str(r.get("date", "")).strip(),
                str(r.get("subject", "")).strip(),
                float(r.get("marks", 0))
            ))

        table = "tests" if sheet_type == "tests" else "exams"
        query = f"INSERT INTO {table} (roll_no, class_name, date, subject, marks) VALUES (%s, %s, %s, %s, %s)"
        db_service.execute_many(query, args_list)
        return records

    @classmethod
    def delete_mark(cls, sheet_type: str, roll_no: str, subject: str, date: str, class_name: str):
        if sheet_type not in ["tests", "exams"]:
            raise ValueError("Invalid table type.")

        roll_no = str(roll_no).strip()
        subject = str(subject).strip().lower()
        date = str(date).strip()
        class_name = str(class_name).strip().upper()

        table = "tests" if sheet_type == "tests" else "exams"
        query = f"DELETE FROM {table} WHERE roll_no = %s AND UPPER(class_name) = %s AND date = %s AND LOWER(subject) = %s"
        count = db_service.execute_query(query, (roll_no, class_name, date, subject), fetchall=False)
        if count == 0:
            raise ValueError(f"Mark record not found in {sheet_type}.")
        return True

marks_service = MarksService()
