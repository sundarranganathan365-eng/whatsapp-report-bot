"""
routes/whatsapp.py
------------------
Twilio WhatsApp webhook handler with interactive report options.
Uses MySQL persistent session store & direct TwiML delivery.
Guaranteed to always return valid TwiML XML response on any event or error.
"""

import sys, os, re, logging
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
logger = logging.getLogger(__name__)

router = APIRouter()

TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM         = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
PUBLIC_BASE_URL     = os.getenv("PUBLIC_BASE_URL", "")

# In-memory session store fallback
IN_MEMORY_SESSIONS = {}

WELCOME_MESSAGE = (
    "👋 *Welcome to the Student Academic Report Bot!*\n\n"
    "To request a student report, please send your details in this format:\n\n"
    "👉 `Name: Rahul, Class: 10, Roll: 23`\n"
    "_(or simply `Class: 10, Roll: 23`)_\n\n"
    "After sending details, you can choose between a *Weekly Report* or *Full Academic Overview*! 📊"
)

GREETING_WORDS = {
    "hi", "hello", "hey", "heyy", "heyyy", "hiii", "helloo", 
    "start", "help", "hii", "helo", "menu", "bot", "welcome",
    "good morning", "good evening", "good afternoon", "restart"
}

def is_greeting_message(text: str) -> bool:
    clean = text.lower().strip()
    clean_alpha = re.sub(r'[^a-z\s]', '', clean).strip()
    if clean_alpha in GREETING_WORDS or clean in GREETING_WORDS:
        return True
    # Short message without numbers or colons or 'roll'
    if len(clean) < 12 and not re.search(r'\d', clean) and ":" not in clean and "roll" not in clean:
        return True
    return False


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


def _clear_user_session(sender_phone: str):
    if sender_phone in IN_MEMORY_SESSIONS:
        del IN_MEMORY_SESSIONS[sender_phone]
    db_service.delete_session(sender_phone)


@router.post("/whatsapp", summary="Twilio WhatsApp webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
):
    twiml = MessagingResponse()
    try:
        incoming = Body.strip()
        config = config_service.get_config()
        
        if not config.get("is_active", True):
            twiml.message("😴 The bot is currently paused by the administrator. Please try again later.")
            return Response(content=str(twiml), media_type="application/xml")

        # ── Greeting / Start / Reset ─────────────────────────────────────────────
        if not incoming or is_greeting_message(incoming):
            _clear_user_session(From)
            reply = config.get("default_reply", WELCOME_MESSAGE)
            twiml.message(reply)
            return Response(content=str(twiml), media_type="application/xml")

        clean_in = incoming.lower().strip()
        session = _get_user_session(From)

        # Dynamic base URL resolution — filter out dead ngrok or localhost URLs
        if PUBLIC_BASE_URL and "ngrok" not in PUBLIC_BASE_URL and "localhost" not in PUBLIC_BASE_URL:
            base_url = PUBLIC_BASE_URL.rstrip('/')
        else:
            # Handle reverse proxies (e.g. Render https)
            scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
            netloc = request.headers.get("x-forwarded-host", request.url.netloc)
            base_url = f"{scheme}://{netloc}".rstrip('/')

        # ── Option Selection (reply '1' or '2') for active session ───────────────
        if clean_in in ["1", "2", "weekly", "full", "overview", "all"] and session:
            report_type = "weekly" if clean_in in ["1", "weekly"] else "full"
            return _send_report_for_session(From, session, report_type, twiml, base_url)

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
                return _send_report_for_session(From, session, explicit_type, twiml, base_url)

            display_class = _clean_class(class_name)

            # Prompt options after student details received
            menu_text = (
                f"👤 *Student Details Received:*\n"
                f"• Name: {student_name}\n"
                f"• Class: {display_class}\n"
                f"• Roll No: {roll_no}\n\n"
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
            f"❌ Missing required details: *{missing_str}*.\n\n"
            "Please send your details in this format:\n"
            "👉 `Name: Rahul, Class: 10, Roll: 23`"
        )
        return Response(content=str(twiml), media_type="application/xml")

    except Exception as err:
        logger.error(f"Error in whatsapp_webhook: {err}", exc_info=True)
        # Always return valid TwiML so Twilio never receives a 500 HTTP error
        err_response = MessagingResponse()
        err_response.message("⚠️ An error occurred processing your request. Please send 'Hey' to restart.")
        return Response(content=str(err_response), media_type="application/xml")


def _send_report_for_session(sender: str, session: dict, report_type: str, twiml: MessagingResponse, base_url: str):
    roll_no = session["roll_no"]
    class_name = session["class_name"]
    student_name = session.get("name", "Student")

    try:
        result = build_report(roll_no, class_name, student_name, report_type=report_type)
    except ValueError as e:
        twiml.message(f"❌ {str(e)}\nPlease double check the Name, Class, and Roll No.")
        return Response(content=str(twiml), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error building report: {e}", exc_info=True)
        twiml.message(f"⚠️ Error generating report: {e}")
        return Response(content=str(twiml), media_type="application/xml")

    pdf_filename = os.path.basename(result["pdf_path"])
    pdf_url = f"{base_url.rstrip('/')}/api/pdf/{pdf_filename}"

    # First TwiML message: Formatted text report
    msg1 = twiml.message()
    msg1.body(result["report_text"])

    # Second TwiML message: PDF attachment (only when valid HTTPS URL available)
    if base_url.startswith("https://"):
        msg2 = twiml.message()
        msg2.body("📎 Detailed PDF report attached above.")
        msg2.media(pdf_url)

    return Response(content=str(twiml), media_type="application/xml")
