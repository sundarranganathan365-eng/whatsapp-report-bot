import sys, os
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service

class AttendanceService:
    @classmethod
    def get_attendance(cls, roll_no: str, class_name: str) -> List[Dict]:
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()
        
        query = """
            SELECT roll_no, class_name, date, status 
            FROM attendance 
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
                "Status": str(r["status"]).strip()
            })
        return results

    @classmethod
    def add_attendance(cls, roll_no: str, date: str, status: str, class_name: str):
        roll_no = str(roll_no).strip()
        date = str(date).strip()
        status = str(status).strip()
        class_name = str(class_name).strip().upper()

        query = "INSERT INTO attendance (roll_no, class_name, date, status) VALUES (%s, %s, %s, %s)"
        db_service.execute_query(query, (roll_no, class_name, date, status), fetchall=False)
        return {"roll_no": roll_no, "date": date, "status": status, "class_name": class_name}

    @classmethod
    def add_attendance_bulk(cls, records: List[Dict]):
        if not records:
            return []

        args_list = []
        for r in records:
            args_list.append((
                str(r.get("roll_no", "")).strip(),
                str(r.get("class_name", "")).strip().upper(),
                str(r.get("date", "")).strip(),
                str(r.get("status", "")).strip()
            ))

        query = "INSERT INTO attendance (roll_no, class_name, date, status) VALUES (%s, %s, %s, %s)"
        db_service.execute_many(query, args_list)
        return records

    @classmethod
    def delete_attendance(cls, roll_no: str, date: str, class_name: str):
        roll_no = str(roll_no).strip()
        date = str(date).strip()
        class_name = str(class_name).strip().upper()

        query = "DELETE FROM attendance WHERE roll_no = %s AND UPPER(class_name) = %s AND date = %s"
        count = db_service.execute_query(query, (roll_no, class_name, date), fetchall=False)
        if count == 0:
            raise ValueError(f"Attendance record not found for Roll '{roll_no}', Class '{class_name}', Date '{date}'.")
        return True

attendance_service = AttendanceService()
