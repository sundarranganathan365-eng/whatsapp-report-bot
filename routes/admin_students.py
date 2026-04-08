import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from services.student_service import student_service

router = APIRouter(prefix="/admin/students", tags=["Admin - Students"])

class StudentCreate(BaseModel):
    roll_no: str
    name: str
    class_name: str

class StudentUpdate(BaseModel):
    name: str
    class_name: str

@router.get("/", summary="Get all students")
def get_students(search: Optional[str] = Query(None, description="Search by Name or Roll No")):
    try:
        students = student_service.get_all_students(search_query=search)
        return {"status": "success", "data": students, "count": len(students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", summary="Add a new student")
def add_student(student: StudentCreate):
    try:
        new_student = student_service.add_student(student.roll_no, student.name, student.class_name)
        return {"status": "success", "data": new_student}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{roll_no}", summary="Update an existing student")
def update_student(roll_no: str, student: StudentUpdate):
    try:
        updated_student = student_service.update_student(
            original_roll_no=roll_no, 
            original_class=student.class_name, # In the UI, we'll pass the current class in the body
            name=student.name, 
            new_class=student.class_name
        )
        return {"status": "success", "data": updated_student}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{roll_no}", summary="Delete a student")
def delete_student(roll_no: str, class_name: str = Query(..., description="Class name required for uniqueness")):
    try:
        student_service.delete_student(roll_no, class_name)
        return {"status": "success", "message": f"Student with Roll No {roll_no} in Class {class_name} deleted."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
