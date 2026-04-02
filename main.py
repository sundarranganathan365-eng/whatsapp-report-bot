"""
main.py
-------
FastAPI application entry point.

Run with:
  uvicorn main:app --reload --port 8000
"""

import os, logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.report import router as report_router
from routes.whatsapp import router as whatsapp_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure output dirs exist
os.makedirs(".tmp/reports", exist_ok=True)
os.makedirs(".tmp/charts", exist_ok=True)

app = FastAPI(
    title="Student Report Bot API",
    description="WhatsApp bot backend — generates student PDF reports from Google Sheets",
    version="1.0.0",
)

# Serve generated PDFs publicly so Twilio can fetch them
app.mount("/api/pdf", StaticFiles(directory=".tmp/reports"), name="pdf")

# Routes
app.include_router(report_router, prefix="/api")
app.include_router(whatsapp_router, prefix="/api")


@app.get("/")
def root():
    return {
        "status": "running",
        "endpoints": {
            "POST /api/get-report":  "Returns PDF for a roll number",
            "POST /api/get-summary": "Returns JSON text summary",
            "POST /api/whatsapp":    "Twilio WhatsApp webhook",
        },
    }
