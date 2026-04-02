# Directive: Phase 2–4 — API, Parser & WhatsApp Bot

## Goal
Expose the report pipeline as a FastAPI API, parse WhatsApp messages, and send reports back via Twilio.

## Tools / Scripts
| Task | File |
|------|------|
| API entry point | `main.py` |
| Report API route | `routes/report.py` |
| WhatsApp webhook | `routes/whatsapp.py` |
| Service orchestration | `services/report_service.py` |
| Input parser | `utils/input_parser.py` |

## Environment Variables Required
- `GOOGLE_SHEETS_KEY` — Sheet ID
- `GOOGLE_CREDENTIALS_PATH` — path to credentials.json
- `TWILIO_ACCOUNT_SID` — from Twilio console
- `TWILIO_AUTH_TOKEN` — from Twilio console
- `TWILIO_WHATSAPP_FROM` — `whatsapp:+14155238886` (sandbox)
- `PUBLIC_BASE_URL` — ngrok HTTPS URL (e.g. `https://abc123.ngrok.io`)

## Endpoints
- `GET  /`                  → health check
- `POST /api/get-report`    → returns PDF file
- `POST /api/get-summary`   → returns JSON summary
- `POST /api/whatsapp`      → Twilio webhook

## Error Handling
- Student not found → 404 JSON / WhatsApp reply
- Missing credentials → 500 JSON / WhatsApp reply
- Invalid roll number parse → WhatsApp asks user to re-format
- PDF send failure → text summary still sent; error note appended

## Learnings (append here as you discover issues)
- (none yet)
