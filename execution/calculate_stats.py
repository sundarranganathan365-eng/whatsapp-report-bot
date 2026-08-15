"""
calculate_stats.py
------------------
Pure calculation layer — takes raw student data (from fetch_student_data.py)
and returns computed statistics and formatted WhatsApp report templates.
"""

from datetime import datetime, timedelta

def get_badge(val: float) -> str:
    if val >= 75:
        return "🟢"
    elif val >= 60:
        return "🟡"
    else:
        return "🔴"

def calculate_attendance(attendance: list) -> dict:
    if not attendance:
        return {
            "total": 0,
            "present": 0,
            "absent": 0,
            "percentage": 0.0,
            "trend": [],
        }

    sorted_records = sorted(attendance, key=lambda r: r["date"])
    present_count = 0
    trend = []
    for i, record in enumerate(sorted_records, start=1):
        status = str(record["status"]).strip().lower()
        if status in ["present", "p"]:
            present_count += 1
        trend.append(
            {
                "date": record["date"],
                "cumulative_pct": round((present_count / i) * 100, 2),
            }
        )

    total = len(sorted_records)
    pct = round((present_count / total) * 100, 1) if total > 0 else 0.0
    return {
        "total": total,
        "present": present_count,
        "absent": total - present_count,
        "percentage": pct,
        "trend": trend,
    }


def calculate_test_stats(tests: list) -> dict:
    if not tests:
        return {"average": 0.0, "by_subject": {}, "trend": []}

    sorted_tests = sorted(tests, key=lambda r: r["date"])

    by_subject: dict = {}
    for t in sorted_tests:
        subj = t["subject"]
        by_subject.setdefault(subj, []).append(float(t["marks"]))

    subject_avg = {
        subj: round(sum(marks) / len(marks), 1)
        for subj, marks in by_subject.items()
    }

    all_marks = [float(t["marks"]) for t in sorted_tests]
    overall_avg = round(sum(all_marks) / len(all_marks), 1)

    trend = [
        {"date": t["date"], "subject": t["subject"], "marks": float(t["marks"])}
        for t in sorted_tests
    ]

    return {
        "average": overall_avg,
        "by_subject": subject_avg,
        "trend": trend,
    }


def calculate_exam_stats(exams: list) -> dict:
    if not exams:
        return {"average": 0.0, "by_subject": {}, "trend": []}

    sorted_exams = sorted(exams, key=lambda r: r["date"])

    by_subject: dict = {}
    for e in sorted_exams:
        subj = e["subject"]
        by_subject.setdefault(subj, []).append(float(e["marks"]))

    subject_avg = {
        subj: round(sum(marks) / len(marks), 1)
        for subj, marks in by_subject.items()
    }

    all_marks = [float(e["marks"]) for e in sorted_exams]
    overall_avg = round(sum(all_marks) / len(all_marks), 1)

    trend = [
        {"date": e["date"], "subject": e["subject"], "marks": float(e["marks"])}
        for e in sorted_exams
    ]

    return {
        "average": overall_avg,
        "by_subject": subject_avg,
        "trend": trend,
    }


def build_weekly_report_text(stats: dict, raw_data: dict, days: int = 7) -> str:
    """Format Option 1: Weekly Report Snapshot"""
    student = stats["student"]
    
    # 1. Date Range
    sorted_att = sorted(raw_data["attendance"], key=lambda r: r["date"], reverse=True)
    recent_att = sorted_att[:days] if sorted_att else []
    
    if recent_att:
        dates = [r["date"] for r in recent_att]
        min_dt = datetime.strptime(min(dates), "%Y-%m-%d")
        max_dt = datetime.strptime(max(dates), "%Y-%m-%d")
        week_str = f"{min_dt.strftime('%d')}–{max_dt.strftime('%d %b')}"
    else:
        now = datetime.now()
        week_str = f"{(now - timedelta(days=6)).strftime('%d')}–{now.strftime('%d %b')}"

    # 2. Attendance stats for recent window
    if recent_att:
        p_count = sum(1 for r in recent_att if str(r["status"]).strip().lower() in ["present", "p"])
        att_total = len(recent_att)
        att_pct = round((p_count / att_total) * 100, 1)
    else:
        p_count, att_total, att_pct = 0, 0, stats["attendance"]["percentage"]

    att_badge = get_badge(att_pct)

    # 3. Recent Tests (last 3-5 tests)
    sorted_tests = sorted(raw_data["tests"], key=lambda r: r["date"], reverse=True)
    recent_tests = sorted_tests[:4]

    test_lines = []
    if recent_tests:
        # Group latest by subject
        seen_subj = set()
        for t in recent_tests:
            subj = t["subject"]
            if subj not in seen_subj:
                seen_subj.add(subj)
                m = float(t["marks"])
                test_lines.append(f"{subj}: {int(m) if m.is_integer() else m}/100 {get_badge(m)}")
    else:
        test_lines.append("No tests recorded for this week.")

    # 4. Weekly Insight
    by_subj = stats["tests"]["by_subject"] or stats["exams"]["by_subject"]
    insights = []
    if att_pct >= 80:
        insights.append("Overall performance and attendance are stable.")
    elif att_pct >= 60:
        insights.append("Attendance is satisfactory, but consistent focus is needed.")
    else:
        insights.append("Attendance requires immediate attention.")

    if by_subj:
        strongest = max(by_subj.items(), key=lambda x: x[1])
        weakest = min(by_subj.items(), key=lambda x: x[1])
        insights.append(f"{strongest[0]} is the strongest subject.")
        if weakest[0] != strongest[0]:
            insights.append(f"{weakest[0]} needs some attention.")
    else:
        insights.append("Academic activity is steady.")

    weekly_text = (
        f"👤 *{student['name']}*\n"
        f"Class: {student['class']} | Roll No: {student['roll_no']}\n"
        f"Week: {week_str}\n\n"
        f"📅 *ATTENDANCE*\n"
        f"Present: {p_count}/{att_total}\n"
        f"Attendance: {att_pct}% {att_badge}\n\n"
        f"📝 *RECENT TESTS*\n" +
        "\n".join(test_lines) + "\n\n"
        f"📈 *WEEKLY INSIGHT*\n" +
        "\n".join(insights) + "\n\n"
        f"📄 *Detailed Weekly Report*\n"
        f"*(PDF attached below)*"
    )
    return weekly_text


def build_full_overview_text(stats: dict, raw_data: dict) -> str:
    """Format Option 2: Student All Details (Academic Overview)"""
    student = stats["student"]
    att_pct = stats["attendance"]["percentage"]
    
    # Combined Subject Averages (Tests + Exams)
    tests_subj = stats["tests"]["by_subject"]
    exams_subj = stats["exams"]["by_subject"]
    
    all_subjects = set(list(tests_subj.keys()) + list(exams_subj.keys()))
    combined_subj = {}
    for s in all_subjects:
        vals = []
        if s in tests_subj: vals.append(tests_subj[s])
        if s in exams_subj: vals.append(exams_subj[s])
        combined_subj[s] = round(sum(vals) / len(vals), 1)

    if combined_subj:
        overall_avg = round(sum(combined_subj.values()) / len(combined_subj), 1)
        strongest = max(combined_subj.items(), key=lambda x: x[1])
        weakest = min(combined_subj.items(), key=lambda x: x[1])
        strongest_str = f"{strongest[0]} — {int(strongest[1]) if strongest[1].is_integer() else strongest[1]}%"
        weakest_str = f"{weakest[0]} — {int(weakest[1]) if weakest[1].is_integer() else weakest[1]}%"
    else:
        overall_avg = 0.0
        strongest_str = "N/A"
        weakest_str = "N/A"

    # Status
    if overall_avg >= 75 and att_pct >= 75:
        status_str = "🟢 Good"
        trend_str = "Improving ↗️"
    elif overall_avg >= 60 and att_pct >= 60:
        status_str = "🟡 Moderate"
        trend_str = "Stable ➡️"
    else:
        status_str = "🔴 Needs Improvement"
        trend_str = "Needs Attention ↘️"

    # Insight paragraph
    first_name = student["name"].split()[0]
    if overall_avg >= 75:
        insight_p = (
            f"{first_name} is maintaining good academic performance "
            f"with consistent attendance. "
        )
    else:
        insight_p = (
            f"{first_name} needs additional focus across key subjects "
            f"to improve overall scores. "
        )
    
    if combined_subj and weakest[0] != strongest[0]:
        insight_p += f"{weakest[0]} requires additional attention to improve the overall average."

    full_text = (
        f"Name: *{student['name']}*\n"
        f"Class: {student['class']}\n"
        f"Roll No: {student['roll_no']}\n\n"
        f"📊 *ACADEMIC OVERVIEW*\n"
        f"Overall Average: {overall_avg}%\n"
        f"Attendance: {att_pct}%\n"
        f"Status: {status_str}\n\n"
        f"🏆 *STRONGEST SUBJECT*\n"
        f"{strongest_str}\n\n"
        f"⚠️ *NEEDS ATTENTION*\n"
        f"{weakest_str}\n\n"
        f"📈 *PERFORMANCE*\n"
        f"Current Trend: {trend_str}\n\n"
        f"💡 *OVERALL INSIGHT*\n"
        f"{insight_p}\n\n"
        f"📄 *Full Student Report*\n"
        f"*(PDF attached below)*"
    )
    return full_text


def build_full_stats(raw_data: dict) -> dict:
    stats = {
        "student": raw_data["student"],
        "attendance": calculate_attendance(raw_data["attendance"]),
        "tests": calculate_test_stats(raw_data["tests"]),
        "exams": calculate_exam_stats(raw_data["exams"]),
    }
    stats["weekly_report_text"] = build_weekly_report_text(stats, raw_data)
    stats["full_overview_text"] = build_full_overview_text(stats, raw_data)
    stats["weekly_snapshot"] = stats["weekly_report_text"]
    return stats
