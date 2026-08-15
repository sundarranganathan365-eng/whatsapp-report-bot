# Directive: Phase 1 — Core Logic

## Goal
Fetch student data from MySQL database and generate a PDF report with charts.

## Inputs
- `roll_no` (string): The student's roll number
- `class_name` (string): Class/Section (e.g. 10A)

## Tools / Scripts
| Task | Script |
|------|--------|
| Initialize database | `execution/init_db.py` |
| Fetch data from MySQL | `execution/fetch_student_data.py` |
| Calculate attendance/test/exam stats | `execution/calculate_stats.py` |
| Generate charts | `execution/generate_charts.py` |
| Generate PDF report | `execution/generate_pdf.py` |
| End-to-end test | `execution/run_report.py` |

## Outputs
- Charts saved to `.tmp/charts/<roll_no>/`
- PDF saved to `.tmp/reports/<roll_no>_report.pdf`

## MySQL Database Structure
Table 1 — `students`: id | roll_no | class_name | name
Table 2 — `attendance`: id | roll_no | class_name | date | status
Table 3 — `tests`: id | roll_no | class_name | date | subject | marks
Table 4 — `exams`: id | roll_no | class_name | date | subject | marks

## Environment Variables Required
- `MYSQL_HOST` — Database host (default: localhost)
- `MYSQL_PORT` — Database port (default: 3306)
- `MYSQL_USER` — Database username (default: root)
- `MYSQL_PASSWORD` — Database password
- `MYSQL_DATABASE` — Database name (default: student_report_db)


## Edge Cases
- Roll number not found → raise ValueError with clear message
- Sheet missing a column → raise KeyError
- No attendance records → attendance % = 0, warn user
- No test/exam records → averages = 0, warn user

## Learnings (append here as you discover issues)
- (none yet)
