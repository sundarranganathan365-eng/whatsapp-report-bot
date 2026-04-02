"""
calculate_stats.py
------------------
Pure calculation layer — takes raw student data (from fetch_student_data.py)
and returns computed statistics.  No I/O, no network calls.
"""


def calculate_attendance(attendance: list) -> dict:
    """
    attendance: [{"date": "...", "status": "Present"/"Absent"}, ...]

    Returns:
    {
        "total": int,
        "present": int,
        "absent": int,
        "percentage": float,
        "trend": [{"date": ..., "cumulative_pct": float}, ...]   # for line chart
    }
    """
    if not attendance:
        return {
            "total": 0,
            "present": 0,
            "absent": 0,
            "percentage": 0.0,
            "trend": [],
        }

    # Sort by date (ISO format strings sort lexicographically correctly)
    sorted_records = sorted(attendance, key=lambda r: r["date"])

    present_count = 0
    trend = []
    for i, record in enumerate(sorted_records, start=1):
        status = record["status"].strip().lower()
        if status == "present" or status == "p":
            present_count += 1
        trend.append(
            {
                "date": record["date"],
                "cumulative_pct": round((present_count / i) * 100, 2),
            }
        )

    total = len(sorted_records)
    return {
        "total": total,
        "present": present_count,
        "absent": total - present_count,
        "percentage": round((present_count / total) * 100, 2),
        "trend": trend,
    }


def calculate_test_stats(tests: list) -> dict:
    """
    tests: [{"date": ..., "subject": ..., "marks": float}, ...]

    Returns:
    {
        "average": float,
        "by_subject": {"Maths": 85.0, ...},
        "trend": [{"date": ..., "marks": float, "subject": ...}, ...]
    }
    """
    if not tests:
        return {"average": 0.0, "by_subject": {}, "trend": []}

    sorted_tests = sorted(tests, key=lambda r: r["date"])

    by_subject: dict = {}
    for t in sorted_tests:
        subj = t["subject"]
        by_subject.setdefault(subj, []).append(t["marks"])

    subject_avg = {
        subj: round(sum(marks) / len(marks), 2)
        for subj, marks in by_subject.items()
    }

    all_marks = [t["marks"] for t in sorted_tests]
    overall_avg = round(sum(all_marks) / len(all_marks), 2)

    trend = [
        {"date": t["date"], "subject": t["subject"], "marks": t["marks"]}
        for t in sorted_tests
    ]

    return {
        "average": overall_avg,
        "by_subject": subject_avg,
        "trend": trend,
    }


def calculate_exam_stats(exams: list) -> dict:
    """
    exams: [{"date": ..., "subject": ..., "marks": float}, ...]

    Returns:
    {
        "average": float,
        "by_subject": {"Maths": 90.0, ...},
        "trend": [{"date": ..., "marks": float, "subject": ...}, ...]
    }
    """
    if not exams:
        return {"average": 0.0, "by_subject": {}, "trend": []}

    sorted_exams = sorted(exams, key=lambda r: r["date"])

    by_subject: dict = {}
    for e in sorted_exams:
        subj = e["subject"]
        by_subject.setdefault(subj, []).append(e["marks"])

    subject_avg = {
        subj: round(sum(marks) / len(marks), 2)
        for subj, marks in by_subject.items()
    }

    all_marks = [e["marks"] for e in sorted_exams]
    overall_avg = round(sum(all_marks) / len(all_marks), 2)

    trend = [
        {"date": e["date"], "subject": e["subject"], "marks": e["marks"]}
        for e in sorted_exams
    ]

    return {
        "average": overall_avg,
        "by_subject": subject_avg,
        "trend": trend,
    }


def build_full_stats(raw_data: dict) -> dict:
    """
    Convenience wrapper — accepts the dict from fetch_student_data and
    returns a single stats dict.
    """
    stats = {
        "student": raw_data["student"],
        "attendance": calculate_attendance(raw_data["attendance"]),
        "tests": calculate_test_stats(raw_data["tests"]),
        "exams": calculate_exam_stats(raw_data["exams"]),
    }
    stats["weekly_snapshot"] = _get_weekly_snapshot(raw_data)
    return stats


def _get_weekly_snapshot(raw_data: dict, days: int = 7) -> str:
    """
    Returns a short text string summarizing only the last 7 days.
    """
    from datetime import datetime, timedelta

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Weekly Attendance
    week_att = [r for r in raw_data["attendance"] if r["date"] >= cutoff]
    present = sum(1 for r in week_att if r["status"].strip().lower() in ["present", "p"])
    total = len(week_att)
    att_str = f"{present}/{total} days" if total > 0 else "No records"

    # Weekly Tests/Exams
    week_tests = [r for r in raw_data["tests"] if r["date"] >= cutoff]
    week_exams = [r for r in raw_data["exams"] if r["date"] >= cutoff]

    test_msg = ""
    if week_tests:
        avg = sum(r["marks"] for r in week_tests) / len(week_tests)
        test_msg = f"\n📝 *Tests:* Avg {avg:.1f} ({len(week_tests)} tests)"

    exam_msg = ""
    if week_exams:
        avg = sum(r["marks"] for r in week_exams) / len(week_exams)
        exam_msg = f"\n🎓 *Exams:* Avg {avg:.1f} ({len(week_exams)} exams)"

    snapshot = (
        f"📅 *Last 7 Days*\n"
        f"• Attendance: {att_str}"
        f"{test_msg}"
        f"{exam_msg}"
    )
    return snapshot


# ── quick test (no Google Sheets needed) ────────────────────────────────────
if __name__ == "__main__":
    import json

    sample = {
        "student": {"roll_no": "23", "name": "Rahul", "class": "10A"},
        "attendance": [
            {"date": "2024-01-01", "status": "Present"},
            {"date": "2024-01-02", "status": "Absent"},
            {"date": "2024-01-03", "status": "Present"},
            {"date": "2024-01-04", "status": "Present"},
        ],
        "tests": [
            {"date": "2024-01-10", "subject": "Maths", "marks": 82},
            {"date": "2024-01-11", "subject": "Science", "marks": 76},
            {"date": "2024-02-10", "subject": "Maths", "marks": 90},
        ],
        "exams": [
            {"date": "2024-03-01", "subject": "Maths", "marks": 88},
            {"date": "2024-03-02", "subject": "Science", "marks": 74},
        ],
    }

    stats = build_full_stats(sample)
    print(json.dumps(stats, indent=2))
