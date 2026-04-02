"""
routes/report.py
----------------
POST /api/get-report   — Returns a PDF file for a given roll number
GET  /api/get-summary  — Returns a JSON text summary (used internally by WhatsApp phase)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.report_service import build_report

router = APIRouter()


# ── Request / Response schemas ───────────────────────────────────────────────

class ReportRequest(BaseModel):
    roll_no: str
    class_name: str
    student_name: str = None


class SummaryResponse(BaseModel):
    roll_no: str
    student_name: str
    summary: str
    pdf_path: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/get-report", summary="Generate and return PDF report for a student")
def get_report(request: ReportRequest):
    """
    Accepts roll number, class, and optional name, generates charts + PDF, 
    and returns the PDF file as a downloadable response.

    Input JSON:
        { 
            "roll_no": "23",
            "class_name": "10A",
            "student_name": "Rahul" 
        }

    Returns:
        PDF file (application/pdf)
    """
    try:
        result = build_report(request.roll_no, request.class_name, request.student_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    pdf_path = result["pdf_path"]
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF was not created on disk.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"report_{request.roll_no}.pdf",
    )


@router.post("/get-summary", response_model=SummaryResponse,
             summary="Get text summary + PDF path (used by WhatsApp webhook)")
def get_summary(request: ReportRequest):
    """
    Same as /get-report but returns a JSON summary instead of a file.
    Used internally by the Twilio WhatsApp handler.
    """
    try:
        result = build_report(request.roll_no, request.class_name, request.student_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    return SummaryResponse(
        roll_no=request.roll_no,
        student_name=result["student_name"],
        summary=result["summary"],
        pdf_path=result["pdf_path"],
    )
