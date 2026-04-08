import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from services.marks_service import marks_service
from services.student_service import student_service

router = APIRouter(prefix="/admin/marks", tags=["Admin - Marks"])

class MarkCreate(BaseModel):
    roll_no: str
    subject: str
    date: str
    marks: float
    class_name: str = ""

from typing import List

class BulkMarkCreate(BaseModel):
    records: List[MarkCreate]

@router.get("/{sheet_type}/{roll_no}", summary="Get marks for a student")
def get_marks(sheet_type: str, roll_no: str, class_name: str = Query(..., description="Class name required")):
    try:
        records = marks_service.get_marks(sheet_type, roll_no, class_name)
        return {"status": "success", "data": records}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{sheet_type}", summary="Add a mark record (test/exam)")
def add_mark(sheet_type: str, record: MarkCreate):
    try:
        class_name = record.class_name
        if not class_name:
            student = student_service.get_student_by_roll_no(record.roll_no)
            if student:
                class_name = student.get("class_name", "")

        new_record = marks_service.add_mark(
            sheet_type, record.roll_no, record.subject, record.date, record.marks, class_name
        )
        return {"status": "success", "data": new_record}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{sheet_type}/bulk", summary="Add multiple mark records (test/exam)")
def add_marks_bulk(sheet_type: str, payload: BulkMarkCreate):
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
                "subject": record.subject,
                "marks": record.marks,
                "class_name": class_name
            })
            
        new_records = marks_service.add_marks_bulk(sheet_type, dict_records)
        return {"status": "success", "data": new_records}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{sheet_type}/{roll_no}", summary="Delete a mark record")
def delete_mark(sheet_type: str, roll_no: str, subject: str = Query(...), date: str = Query(...), class_name: str = Query(...)):
    try:
        marks_service.delete_mark(sheet_type, roll_no, subject, date, class_name)
        return {"status": "success", "message": f"Mark record deleted from {sheet_type}."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
