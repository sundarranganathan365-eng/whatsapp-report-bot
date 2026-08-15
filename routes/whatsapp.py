"""
routes/whatsapp.py
------------------
Phase 4 — Twilio WhatsApp webhook handler with interactive report options.
Uses MySQL persistent session store & direct TwiML delivery.
"""

import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

from utils.input_parser import parse_student_input, is_complete
from services.report_service import build_report
from services.config_service import config_service
from services.db_service import db_service

load_dotenv()

router = APIRouter()

TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM         = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
PUBLIC_BASE_URL     = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

# In-memory session store fallback
IN_MEMORY_SESSIONS = {}

USAGE_MESSAGE = (
    "👋 *Welcome to the Student Report Bot!*\n\n"
    "Please send your details in this format:\n"
    "  `Name: Rahul, Class: 10A, Roll: 23`"
)

GREETINGS = {"hi", "hello", "hey", "start", "help", "hii", "helo", "menu"}


def _clean_class(cls_str: str) -> str:
    if not cls_str:
        return ""
    m = re.search(r'\d+', str(cls_str))
    return m.group(0) if m else str(cls_str).strip()


def _get_user_session(sender_phone: str) -> dict | None:
    session = db_service.get_session(sender_phone)
    if session:
        return session
    return IN_MEMORY_SESSIONS.get(sender_phone)


def _save_user_session(sender_phone: str, session: dict):
    IN_MEMORY_SESSIONS[sender_phone] = session
    db_service.save_session(sender_phone, session["roll_no"], session["class_name"], session["name"])


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
    session = _get_user_session(From)

    if clean_in in ["1", "2", "weekly", "full", "overview", "all"] and session:
        report_type = "weekly" if clean_in in ["1", "weekly"] else "full"
        return _send_report_for_session(From, session, report_type, twiml)

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
        
        # Save session to MySQL & memory
        session = {"roll_no": roll_no, "class_name": class_name, "name": student_name}
        _save_user_session(From, session)

        # If user explicitly passed option in first message
        if explicit_type:
            return _send_report_for_session(From, session, explicit_type, twiml)

        display_class = _clean_class(class_name)

        # Always ask user to choose option 1 or 2 after student details are sent
        menu_text = (
            f"👤 *Student Identified:* {student_name}\n"
            f"Class: {display_class} | Roll No: {roll_no}\n\n"
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


def _send_report_for_session(sender: str, session: dict, report_type: str, twiml: MessagingResponse):
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

    # Construct direct TwiML response with text report and PDF media attachment
    pdf_filename = os.path.basename(result["pdf_path"])
    pdf_url = f"{PUBLIC_BASE_URL.rstrip('/')}/api/pdf/{pdf_filename}"

    # First TwiML message: Formatted text report
    msg1 = twiml.message()
    msg1.body(result["report_text"])

    # Second TwiML message: PDF attachment
    msg2 = twiml.message()
    msg2.body("📎 Detailed PDF report attached above.")
    msg2.media(pdf_url)

    # Optional: also try Twilio REST API push if keys configured
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_ACCOUNT_SID.startswith("AC"):
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                from_=TWILIO_FROM,
                to=sender,
                body=result["report_text"]
            )
            client.messages.create(
                from_=TWILIO_FROM,
                to=sender,
                media_url=[pdf_url],
                body="📎 Detailed PDF report attached above."
            )
        except Exception as e:
            print(f"REST API secondary push notice (handled by TwiML): {e}")

    return Response(content=str(twiml), media_type="application/xml")
