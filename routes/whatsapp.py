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
from services.config_service import config_service

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
    
    config = config_service.get_config()
    if not config.get("is_active", True):
        twiml.message("😴 The bot is currently paused by the administrator. Please try again later.")
        return Response(content=str(twiml), media_type="application/xml")

    # ── Greeting ─────────────────────────────────────────────────────────────
    if incoming.lower() in GREETINGS or not incoming:
        twiml.message(config.get("default_reply", USAGE_MESSAGE))
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

    # ── Immediate acknowledgment ──────────────────────────────────────────────
    # We return a quick TwiML response so Twilio doesn't time out while we generate the PDF.
    # The actual report content will be sent via the REST API below.
    twiml.message("⏳ *Generating your report...* Please wait a moment.")

    # ── Send report via Twilio REST API ───────────────────────────────────────
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # 1. Send the text snapshot (Last 7 Days)
        client.messages.create(
            from_=TWILIO_FROM,
            to=From,
            body=result["weekly_snapshot"]
        )

        # 2. Add a tiny delay if needed or just send the PDF immediately
        pdf_filename = os.path.basename(result["pdf_path"])
        pdf_url = f"{PUBLIC_BASE_URL}/api/pdf/{pdf_filename}"
        
        # 3. Send the PDF attachment
        client.messages.create(
            from_=TWILIO_FROM,
            to=From,
            media_url=[pdf_url],
            body="📎 Your full PDF report is attached above.",
        )
    except Exception as e:
        # If REST API fails, we can't do much but log it
        print(f"ERROR sending WhatsApp report: {e}")

    return Response(content=str(twiml), media_type="application/xml")
