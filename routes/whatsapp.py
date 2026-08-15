"""
routes/whatsapp.py
------------------
Phase 4 — Twilio WhatsApp webhook handler with interactive report options.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

from utils.input_parser import parse_student_input, is_complete
from services.report_service import build_report
from services.config_service import config_service

load_dotenv()

router = APIRouter()

TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM         = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
PUBLIC_BASE_URL     = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

# In-memory session store: { sender_phone: {"roll_no": ..., "class_name": ..., "name": ...} }
USER_SESSIONS = {}

USAGE_MESSAGE = (
    "👋 *Welcome to the Student Report Bot!*\n\n"
    "Please send your details in this format:\n"
    "  `Name: Rahul, Class: 10A, Roll: 23`"
)

GREETINGS = {"hi", "hello", "hey", "start", "help", "hii", "helo", "menu"}


@router.post("/whatsapp", summary="Twilio WhatsApp webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
):
    incoming = Body.strip()
    twiml = MessagingResponse()
    
    config = config_service.get_config()
    if not config.get("is_active", True):
        twiml.message("😴 The bot is currently paused by the administrator. Please try again later.")
        return Response(content=str(twiml), media_type="application/xml")

    # ── Greeting ─────────────────────────────────────────────────────────────
    if incoming.lower() in GREETINGS or not incoming:
        twiml.message(config.get("default_reply", USAGE_MESSAGE))
        return Response(content=str(twiml), media_type="application/xml")

    # ── Option Selection (reply '1' or '2') for active session ───────────────
    clean_in = incoming.lower().strip()
    if clean_in in ["1", "2", "weekly", "full", "overview", "all"] and From in USER_SESSIONS:
        session = USER_SESSIONS[From]
        report_type = "weekly" if clean_in in ["1", "weekly"] else "full"
        return await _send_report_for_session(From, session, report_type, twiml)

    # ── Explicit option flag in single message e.g. Option: 1 / Report: 2 ───
    explicit_type = None
    if "option: 1" in clean_in or "option 1" in clean_in or "report: 1" in clean_in:
        explicit_type = "weekly"
    elif "option: 2" in clean_in or "option 2" in clean_in or "report: 2" in clean_in:
        explicit_type = "full"

    # ── Parse input for student details ─────────────────────────────────────
    parsed = parse_student_input(incoming)
    
    if is_complete(parsed):
        roll_no = parsed["roll_no"]
        class_name = parsed["class"]
        student_name = parsed["name"]
        
        # Save session
        session = {"roll_no": roll_no, "class_name": class_name, "name": student_name}
        USER_SESSIONS[From] = session

        # If user explicitly passed option in first message
        if explicit_type:
            return await _send_report_for_session(From, session, explicit_type, twiml)

        # Always ask user to choose option 1 or 2 after student details are sent
        menu_text = (
            f"👤 *Student Identified:* {student_name}\n"
            f"Class: {class_name} | Roll No: {roll_no}\n\n"
            f"Which report would you like to receive?\n\n"
            f"1️⃣ *Weekly Report* (7-day summary & tests)\n"
            f"2️⃣ *Full Academic Overview* (All-time stats & insights)\n\n"
            f"👉 Reply *1* for Weekly Report or *2* for Full Academic Overview"
        )
        twiml.message(menu_text)
        return Response(content=str(twiml), media_type="application/xml")

    # Incomplete details & no active session
    missing_str = ", ".join(parsed["missing"])
    twiml.message(
        f"❌ I'm missing some details: *{missing_str}*.\n\n"
        "Please send your details in this format:\n"
        "  `Name: Rahul, Class: 10A, Roll: 23`"
    )
    return Response(content=str(twiml), media_type="application/xml")


async def _send_report_for_session(sender: str, session: dict, report_type: str, twiml: MessagingResponse):
    roll_no = session["roll_no"]
    class_name = session["class_name"]
    student_name = session["name"]

    try:
        result = build_report(roll_no, class_name, student_name, report_type=report_type)
    except ValueError as e:
        twiml.message(f"❌ {str(e)}\nPlease double check the Name, Class, and Roll No.")
        return Response(content=str(twiml), media_type="application/xml")
    except Exception as e:
        twiml.message(f"⚠️ Error generating report: {e}")
        return Response(content=str(twiml), media_type="application/xml")

    twiml.message("⏳ *Generating your report...* Please wait a moment.")

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # 1. Send formatted text (Weekly or Full Overview)
        client.messages.create(
            from_=TWILIO_FROM,
            to=sender,
            body=result["report_text"]
        )

        # 2. Send PDF attachment
        pdf_filename = os.path.basename(result["pdf_path"])
        pdf_url = f"{PUBLIC_BASE_URL}/api/pdf/{pdf_filename}"
        
        client.messages.create(
            from_=TWILIO_FROM,
            to=sender,
            media_url=[pdf_url],
            body="📎 Detailed PDF report attached above."
        )
    except Exception as e:
        print(f"ERROR sending WhatsApp report: {e}")

    return Response(content=str(twiml), media_type="application/xml")
