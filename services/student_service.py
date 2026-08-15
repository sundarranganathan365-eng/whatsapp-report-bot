import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service

class StudentService:
    @classmethod
    def get_all_students(cls, search_query=None):
        if search_query:
            query = """
                SELECT roll_no, name, class_name 
                FROM students 
                WHERE LOWER(name) LIKE %s OR LOWER(roll_no) LIKE %s
                ORDER BY class_name, CAST(roll_no AS UNSIGNED), roll_no
            """
            pattern = f"%{str(search_query).lower()}%"
            records = db_service.execute_query(query, (pattern, pattern))
        else:
            query = """
                SELECT roll_no, name, class_name 
                FROM students 
                ORDER BY class_name, CAST(roll_no AS UNSIGNED), roll_no
            """
            records = db_service.execute_query(query)

        normalized_records = []
        for s in records:
            normalized_records.append({
                "roll_no": str(s["roll_no"]).strip(),
                "name": str(s["name"]).strip(),
                "class_name": str(s["class_name"]).strip().upper(),
                "original_row": s
            })

        return normalized_records

    @classmethod
    def get_student_by_roll_no(cls, roll_no: str, class_name: str):
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()
        query = "SELECT roll_no, name, class_name FROM students WHERE roll_no = %s AND UPPER(class_name) = %s"
        record = db_service.execute_query(query, (roll_no, class_name), fetchone=True)
        if record:
            return {
                "roll_no": str(record["roll_no"]).strip(),
                "name": str(record["name"]).strip(),
                "class_name": str(record["class_name"]).strip().upper(),
                "original_row": record
            }
        return None

    @classmethod
    def add_student(cls, roll_no: str, name: str, class_name: str):
        roll_no = str(roll_no).strip()
        name = str(name).strip()
        class_name = str(class_name).strip().upper()

        existing = cls.get_student_by_roll_no(roll_no, class_name)
        if existing:
            raise ValueError(f"Student with Roll No '{roll_no}' in Class '{class_name}' already exists.")

        query = "INSERT INTO students (roll_no, class_name, name) VALUES (%s, %s, %s)"
        db_service.execute_query(query, (roll_no, class_name, name), fetchall=False)
        return {"roll_no": roll_no, "name": name, "class_name": class_name}

    @classmethod
    def update_student(cls, original_roll_no: str, original_class: str, name: str, new_class: str):
        original_roll_no = str(original_roll_no).strip()
        original_class = str(original_class).strip().upper()
        name = str(name).strip()
        new_class = str(new_class).strip().upper()

        existing = cls.get_student_by_roll_no(original_roll_no, original_class)
        if not existing:
            raise ValueError(f"Student not found for Roll No '{original_roll_no}' in Class '{original_class}'.")

        query = "UPDATE students SET name = %s, class_name = %s WHERE roll_no = %s AND UPPER(class_name) = %s"
        db_service.execute_query(query, (name, new_class, original_roll_no, original_class), fetchall=False)
        return {"roll_no": original_roll_no, "name": name, "class_name": new_class}

    @classmethod
    def delete_student(cls, roll_no: str, class_name: str):
        roll_no = str(roll_no).strip()
        class_name = str(class_name).strip().upper()

        existing = cls.get_student_by_roll_no(roll_no, class_name)
        if not existing:
            raise ValueError(f"Student not found for Roll No '{roll_no}' in Class '{class_name}'.")

        query = "DELETE FROM students WHERE roll_no = %s AND UPPER(class_name) = %s"
        db_service.execute_query(query, (roll_no, class_name), fetchall=False)
        return True

student_service = StudentService()
