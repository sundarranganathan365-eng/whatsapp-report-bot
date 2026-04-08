import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.attendance_service import attendance_service
from services.student_service import student_service

router = APIRouter(prefix="/admin/attendance", tags=["Admin - Attendance"])

class AttendanceCreate(BaseModel):
    roll_no: str
    date: str
    status: str
    class_name: str = ""

from typing import List

class BulkAttendanceCreate(BaseModel):
    records: List[AttendanceCreate]

@router.get("/{roll_no}", summary="Get attendance records for a student")
def get_attendance(roll_no: str, class_name: str = Query(..., description="Class name required")):
    try:
        records = attendance_service.get_attendance(roll_no, class_name)
        return {"status": "success", "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", summary="Add an attendance record")
def add_attendance(record: AttendanceCreate):
    try:
        # Auto-resolve class_name from students sheet if empty
        class_name = record.class_name
        if not class_name:
            student = student_service.get_student_by_roll_no(record.roll_no)
            if student:
                class_name = student.get("class_name", "")

        new_record = attendance_service.add_attendance(
            record.roll_no, record.date, record.status, class_name
        )
        return {"status": "success", "data": new_record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", summary="Add multiple attendance records")
def add_attendance_bulk(payload: BulkAttendanceCreate):
    try:
        dict_records = []
        for record in payload.records:
            class_name = record.class_name
            if not class_name:
                student = student_service.get_student_by_roll_no(record.roll_no)
                if student:
                    class_name = student.get("class_name", "")
            dict_records.append({
                "roll_no": record.roll_no,
                "date": record.date,
                "status": record.status,
                "class_name": class_name
            })
            
        new_records = attendance_service.add_attendance_bulk(dict_records)
        return {"status": "success", "data": new_records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{roll_no}", summary="Delete an attendance record by date")
def delete_attendance(roll_no: str, date: str, class_name: str = Query(..., description="Class name required")):
    try:
        attendance_service.delete_attendance(roll_no, date, class_name)
        return {"status": "success", "message": "Attendance record deleted."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
