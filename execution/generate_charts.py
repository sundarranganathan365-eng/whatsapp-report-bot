"""
generate_charts.py
------------------
Generates 3 charts from student stats and saves them as PNG files.

Charts:
  1. Attendance trend    — line chart  (cumulative %)
  2. Test marks trend    — line chart  (marks per test, coloured by subject)
  3. Exam comparison     — bar chart   (marks per subject)

Inputs: stats dict (from calculate_stats.build_full_stats)
Outputs: chart PNG files in .tmp/charts/<roll_no>/
"""

import os
import matplotlib
matplotlib.use("Agg")          # headless — no display required
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


CHART_DIR_BASE = ".tmp/charts"


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def chart_attendance_trend(stats: dict, roll_no: str) -> str:
    """Line chart: cumulative attendance % over time."""
    out_dir = _ensure_dir(os.path.join(CHART_DIR_BASE, roll_no))
    out_path = os.path.join(out_dir, "attendance_trend.png")

    trend = stats["attendance"]["trend"]
    if not trend:
        # Create a blank placeholder chart
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No attendance data available",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    dates = [r["date"] for r in trend]
    pcts = [r["cumulative_pct"] for r in trend]

    # ------ X-axis thinning for readability ----------------------------------
    max_labels = 10
    step = max(1, len(dates) // max_labels)
    x_indices = list(range(len(dates)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_indices, pcts, marker="o", linewidth=2.5,
            color="#4A90D9", markersize=5, label="Attendance %")
    ax.axhline(75, color="#E74C3C", linestyle="--", linewidth=1.5,
               label="75% threshold")

    ax.set_xticks(x_indices[::step])
    ax.set_xticklabels(dates[::step], rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax.set_ylim(0, 105)
    ax.set_title("Attendance Trend", fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Attendance %")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def chart_test_trend(stats: dict, roll_no: str) -> str:
    """Line chart: test marks over time, coloured by subject."""
    out_dir = _ensure_dir(os.path.join(CHART_DIR_BASE, roll_no))
    out_path = os.path.join(out_dir, "test_trend.png")

    trend = stats["tests"]["trend"]
    if not trend:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No test data available",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    # Group by subject for separate lines
    subjects: dict = {}
    for t in trend:
        subjects.setdefault(t["subject"], {"dates": [], "marks": []})
        subjects[t["subject"]]["dates"].append(t["date"])
        subjects[t["subject"]]["marks"].append(t["marks"])

    colors = ["#4A90D9", "#E67E22", "#27AE60", "#9B59B6",
              "#E74C3C", "#1ABC9C", "#F39C12", "#2C3E50"]

    fig, ax = plt.subplots(figsize=(10, 5))
    for idx, (subject, data) in enumerate(subjects.items()):
        color = colors[idx % len(colors)]
        ax.plot(data["dates"], data["marks"], marker="o", linewidth=2.5,
                color=color, markersize=6, label=subject)

    ax.set_title("Test Marks Trend by Subject", fontsize=15,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Marks")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def chart_exam_comparison(stats: dict, roll_no: str) -> str:
    """Bar chart: exam marks per subject."""
    out_dir = _ensure_dir(os.path.join(CHART_DIR_BASE, roll_no))
    out_path = os.path.join(out_dir, "exam_comparison.png")

    by_subject = stats["exams"]["by_subject"]
    if not by_subject:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No exam data available",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    subjects = list(by_subject.keys())
    marks = [by_subject[s] for s in subjects]

    colors = ["#4A90D9", "#E67E22", "#27AE60", "#9B59B6",
              "#E74C3C", "#1ABC9C", "#F39C12", "#2C3E50"]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(subjects, marks,
                  color=colors[:len(subjects)], width=0.5, edgecolor="white")

    # Label each bar
    for bar, val in zip(bars, marks):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val}", ha="center", va="bottom", fontsize=10,
                fontweight="bold")

    ax.set_title("Exam Marks by Subject", fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("Subject")
    ax.set_ylabel("Average Marks")
    ax.set_ylim(0, max(marks) * 1.2 if marks else 100)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_all_charts(stats: dict) -> dict:
    """
    Generate all 3 charts.
    Returns a dict with paths to each chart PNG.
    """
    roll_no = stats["student"]["roll_no"]
    return {
        "attendance": chart_attendance_trend(stats, roll_no),
        "tests": chart_test_trend(stats, roll_no),
        "exams": chart_exam_comparison(stats, roll_no),
    }


# ── quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from calculate_stats import build_full_stats

    sample = {
        "student": {"roll_no": "23", "name": "Rahul", "class": "10A"},
        "attendance": [
            {"date": "2024-01-01", "status": "Present"},
            {"date": "2024-01-02", "status": "Absent"},
            {"date": "2024-01-03", "status": "Present"},
            {"date": "2024-01-04", "status": "Present"},
            {"date": "2024-01-05", "status": "Present"},
        ],
        "tests": [
            {"date": "2024-01-10", "subject": "Maths", "marks": 82},
            {"date": "2024-01-11", "subject": "Science", "marks": 76},
            {"date": "2024-02-10", "subject": "Maths", "marks": 90},
            {"date": "2024-02-11", "subject": "Science", "marks": 85},
        ],
        "exams": [
            {"date": "2024-03-01", "subject": "Maths", "marks": 88},
            {"date": "2024-03-02", "subject": "Science", "marks": 74},
            {"date": "2024-03-03", "subject": "English", "marks": 91},
        ],
    }

    stats = build_full_stats(sample)
    chart_paths = generate_all_charts(stats)
    print("Charts saved:")
    for name, path in chart_paths.items():
        print(f"  {name}: {path}")
