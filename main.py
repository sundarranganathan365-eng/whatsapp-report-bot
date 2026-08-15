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
from fastapi.middleware.cors import CORSMiddleware
from routes.report import router as report_router
from routes.whatsapp import router as whatsapp_router
from routes.admin_students import router as admin_students_router
from routes.admin_attendance import router as admin_attendance_router
from routes.admin_marks import router as admin_marks_router
from routes.admin_reports import router as admin_reports_router
from routes.admin_bot import router as admin_bot_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure output dirs exist
os.makedirs(".tmp/reports", exist_ok=True)
os.makedirs(".tmp/charts", exist_ok=True)

app = FastAPI(
    title="Student Report Bot API",
    description="WhatsApp bot backend — generates student PDF reports from MySQL Database",
    version="1.0.0",
)

@app.on_event("startup")
def startup_event():
    try:
        from services.db_service import db_service
        db_service.init_db()
        logger.info("Database initialized successfully on startup.")
    except Exception as e:
        logger.warning(f"Database initialization deferred or failed on startup: {e}")


# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated PDFs publicly so Twilio can fetch them
app.mount("/api/pdf", StaticFiles(directory=".tmp/reports"), name="pdf")

# Routes
app.include_router(report_router, prefix="/api")
app.include_router(whatsapp_router, prefix="/api")
app.include_router(admin_students_router, prefix="/api")
app.include_router(admin_attendance_router, prefix="/api")
app.include_router(admin_marks_router, prefix="/api")
app.include_router(admin_reports_router, prefix="/api")
app.include_router(admin_bot_router, prefix="/api")


# Serve React Frontend
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {"status": "running", "message": "API is active. Frontend build not found."}

# SPA Catch-all (for React Router)
@app.exception_handler(404)
async def custom_404_handler(request, __):
    if not request.url.path.startswith("/api"):
        from fastapi.responses import FileResponse
        dist_path = os.path.join("frontend", "dist", "index.html")
        if os.path.exists(dist_path):
            return FileResponse(dist_path)
    return {"detail": "Not Found"}
