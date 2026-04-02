# Directive: Phase 1 — Core Logic

## Goal
Fetch student data from Google Sheets and generate a PDF report with charts.

## Inputs
- `roll_no` (string): The student's roll number

## Tools / Scripts
| Task | Script |
|------|--------|
| Fetch data from Google Sheets | `execution/fetch_student_data.py` |
| Calculate attendance/test/exam stats | `execution/calculate_stats.py` |
| Generate charts | `execution/generate_charts.py` |
| Generate PDF report | `execution/generate_pdf.py` |
| End-to-end test | `execution/run_report.py` |

## Outputs
- Charts saved to `.tmp/charts/<roll_no>/`
- PDF saved to `.tmp/reports/<roll_no>_report.pdf`

## Google Sheets Structure
Sheet 1 — `students`: Roll No | Name | Class
Sheet 2 — `attendance`: Roll No | Date | Status (Present/Absent)
Sheet 3 — `tests`: Roll No | Date | Subject | Marks
Sheet 4 — `exams`: Roll No | Date | Subject | Marks

## Environment Variables Required
- `GOOGLE_SHEETS_KEY` — The Google Sheet ID (from the URL)
- `GOOGLE_CREDENTIALS_PATH` — Path to credentials.json (default: `credentials.json`)

## Edge Cases
- Roll number not found → raise ValueError with clear message
- Sheet missing a column → raise KeyError
- No attendance records → attendance % = 0, warn user
- No test/exam records → averages = 0, warn user

## Learnings (append here as you discover issues)
- (none yet)
