import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from urllib.parse import quote

from services.student_service import student_service
from services.report_service import build_report

router = APIRouter(prefix="/admin/reports", tags=["Admin - Reports"])

@router.get("/preview/{roll_no}", summary="Preview report logic (admin)")
def preview_report(roll_no: str, class_name: str = None):
    try:
        # Step 1: Find the student to get class_name and name
        students = student_service.get_all_students(search_query=roll_no)
        # We need an exact match for roll_no since search_query does a substring search
        if class_name:
            student = next((s for s in students if s["roll_no"] == roll_no and s["class_name"].upper() == class_name.upper()), None)
        else:
            student = next((s for s in students if s["roll_no"] == roll_no), None)
        
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with Roll No {roll_no} not found.")

        # Step 2: Build report
        class_name = student["class_name"]
        student_name = student["name"]
        
        # build_report returns a dict with:
        # student_name, summary, weekly_snapshot, pdf_path, chart_paths
        result = build_report(roll_no, class_name, student_name)
        
        # Since the app mounts PDF public URL at '/api/pdf', we construct the download URL
        pdf_filename = os.path.basename(result["pdf_path"])
        pdf_url = f"/api/pdf/{quote(pdf_filename)}"

        return {
            "status": "success",
            "data": {
                "student_name": student_name,
                "roll_no": roll_no,
                "class_name": class_name,
                "summary": result.get("summary", ""),
                "weekly_snapshot": result.get("weekly_snapshot", ""),
                "pdf_url": pdf_url
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")
