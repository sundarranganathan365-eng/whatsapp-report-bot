import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from urllib.parse import quote

from services.student_service import student_service
from services.report_service import build_report

router = APIRouter(prefix="/admin/reports", tags=["Admin - Reports"])

@router.get("/preview/{roll_no}", summary="Preview report logic (admin)")
def preview_report(roll_no: str, class_name: str = None, report_type: str = "weekly"):
    try:
        students = student_service.get_all_students(search_query=roll_no)
        if class_name:
            student = next((s for s in students if str(s["roll_no"]).strip() == str(roll_no).strip() and s["class_name"].upper() == class_name.upper()), None)
        else:
            student = next((s for s in students if str(s["roll_no"]).strip() == str(roll_no).strip()), None)
        
        if not student and students:
            student = students[0]

        if not student:
            raise HTTPException(status_code=404, detail=f"Student with Roll No {roll_no} not found.")

        class_name = student["class_name"]
        student_name = student["name"]
        
        result = build_report(roll_no, class_name, student_name, report_type=report_type)
        
        pdf_filename = os.path.basename(result["pdf_path"])
        pdf_url = f"/api/pdf/{quote(pdf_filename)}"

        return {
            "status": "success",
            "data": {
                "student_name": student_name,
                "roll_no": roll_no,
                "class_name": class_name,
                "summary": result.get("summary", ""),
                "weekly_report": result.get("weekly_snapshot", ""),
                "full_overview": result.get("full_overview", ""),
                "report_type": report_type,
                "pdf_url": pdf_url
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")
