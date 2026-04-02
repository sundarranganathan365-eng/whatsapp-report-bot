"""
routes/whatsapp.py
------------------
Phase 4 — Twilio WhatsApp webhook handler.

Twilio sends a POST to this endpoint every time a user messages the bot.
We parse the message, call the report service, and reply with text + PDF.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

from utils.input_parser import parse_student_input, is_complete
from services.report_service import build_report

load_dotenv()

router = APIRouter()

TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM         = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# Public base URL of your server — needed so Twilio can fetch the PDF
# Set this in .env once you have an ngrok/public URL
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

USAGE_MESSAGE = (
    "👋 *Welcome to the Student Report Bot!*\n\n"
    "Send your details in this format:\n"
    "  `Name: Rahul, Class: 10A, Roll: 23`\n\n"
    "Or just send your roll number:\n"
    "  `Roll: 23`\n\n"
    "I'll send back your full academic report as a PDF 📄"
)

GREETINGS = {"hi", "hello", "hey", "start", "help", "hii", "helo"}


@router.post("/whatsapp", summary="Twilio WhatsApp webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
):
    """
    Twilio posts here on every incoming WhatsApp message.
    Content-Type: application/x-www-form-urlencoded
    """
    incoming = Body.strip()
    twiml = MessagingResponse()

    # ── Greeting ─────────────────────────────────────────────────────────────
    if incoming.lower() in GREETINGS or not incoming:
        twiml.message(USAGE_MESSAGE)
        return Response(content=str(twiml), media_type="application/xml")

    # ── Parse input ──────────────────────────────────────────────────────────
    parsed = parse_student_input(incoming)
    
    if not is_complete(parsed):
        missing_str = ", ".join(parsed["missing"])
        twiml.message(
            f"❌ I'm missing some details: *{missing_str}*.\n\n"
            "Please send your details in this format:\n"
            "  `Name: Rahul, Class: 10A, Roll: 23`"
        )
        return Response(content=str(twiml), media_type="application/xml")

    roll_no = parsed["roll_no"]
    class_name = parsed["class"]
    student_name = parsed["name"]

    # ── Generate report ───────────────────────────────────────────────────────
    try:
        result = build_report(roll_no, class_name, student_name)
    except ValueError as e:
        twiml.message(
            f"❌ {str(e)}\n"
            "Please double check the Name, Class, and Roll No."
        )
        return Response(content=str(twiml), media_type="application/xml")
    except EnvironmentError:
        twiml.message(
            "⚠️ The bot is not configured properly.\n"
            "Please contact the administrator."
        )
        return Response(content=str(twiml), media_type="application/xml")
    except Exception as e:
        twiml.message(
            f"⚠️ Something went wrong while generating the report.\n"
            f"Error: {e}\n\nPlease try again in a moment."
        )
        return Response(content=str(twiml), media_type="application/xml")

    # ── Send text summary first ───────────────────────────────────────────────
    # We now use the 'weekly_snapshot' (last 7 days) as the text reply
    # while keeping the full data in the PDF report.
    twiml.message(result["weekly_snapshot"])

    # ── Send PDF via Twilio REST API (TwiML can't attach files directly) ─────
    pdf_filename = os.path.basename(result["pdf_path"])
    pdf_url = f"{PUBLIC_BASE_URL}/api/pdf/{pdf_filename}"

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=TWILIO_FROM,
            to=From,
            media_url=[pdf_url],
            body="📎 Your PDF report is attached above.",
        )
    except Exception as e:
        # Don't fail —text summary already sent
        msg = twiml.message(
            f"⚠️ Report generated but PDF could not be sent.\n"
            f"Reason: {e}"
        )

    return Response(content=str(twiml), media_type="application/xml")
