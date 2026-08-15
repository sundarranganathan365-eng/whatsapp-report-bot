"""
generate_charts.py
------------------
Generates 3 charts from student stats and saves them as PNG files.
Optimized for ultra-fast execution (<1 sec) to prevent webhook timeouts.
"""

import os
import matplotlib
matplotlib.use("Agg")          # headless — no display required
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

CHART_DIR_BASE = ".tmp/charts"

# Fast matplotlib defaults
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.autolayout'] = True


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def chart_attendance_trend(stats: dict, roll_no: str) -> str:
    """Line chart: cumulative attendance % over time (fast rendering)."""
    out_dir = _ensure_dir(os.path.join(CHART_DIR_BASE, roll_no))
    out_path = os.path.join(out_dir, "attendance_trend.png")

    trend = stats["attendance"]["trend"]
    fig, ax = plt.subplots(figsize=(6, 3))

    if not trend:
        ax.text(0.5, 0.5, "No attendance data", ha="center", va="center", fontsize=11, color="gray")
        ax.axis("off")
    else:
        # Thin data points for fast rendering (last 30 days max)
        subset = trend[-30:] if len(trend) > 30 else trend
        dates = [r["date"] for r in subset]
        pcts = [r["cumulative_pct"] for r in subset]

        step = max(1, len(dates) // 6)
        x_indices = list(range(len(dates)))

        ax.plot(x_indices, pcts, marker="o", linewidth=2, color="#4A90D9", markersize=4, label="Attendance %")
        ax.axhline(75, color="#E74C3C", linestyle="--", linewidth=1, label="75% Threshold")

        ax.set_xticks(x_indices[::step])
        ax.set_xticklabels(dates[::step], rotation=30, ha="right", fontsize=7)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        ax.set_ylim(0, 105)
        ax.set_title("Attendance Trend", fontsize=11, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)

    fig.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)
    return out_path


def chart_test_trend(stats: dict, roll_no: str) -> str:
    """Line chart: test marks over time, coloured by subject."""
    out_dir = _ensure_dir(os.path.join(CHART_DIR_BASE, roll_no))
    out_path = os.path.join(out_dir, "test_trend.png")

    trend = stats["tests"]["trend"]
    fig, ax = plt.subplots(figsize=(6, 3))

    if not trend:
        ax.text(0.5, 0.5, "No test data", ha="center", va="center", fontsize=11, color="gray")
        ax.axis("off")
    else:
        subset = trend[-15:] if len(trend) > 15 else trend
        subjects = {}
        for t in subset:
            subjects.setdefault(t["subject"], {"dates": [], "marks": []})
            subjects[t["subject"]]["dates"].append(t["date"])
            subjects[t["subject"]]["marks"].append(t["marks"])

        colors = ["#4A90D9", "#E67E22", "#27AE60", "#9B59B6", "#E74C3C"]

        for idx, (subject, data) in enumerate(subjects.items()):
            color = colors[idx % len(colors)]
            ax.plot(data["dates"], data["marks"], marker="o", linewidth=2, color=color, markersize=4, label=subject)

        ax.set_title("Test Marks Trend", fontsize=11, fontweight="bold")
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=0.3)
        plt.xticks(rotation=30, ha="right", fontsize=7)
        ax.legend(fontsize=7)

    fig.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)
    return out_path


def chart_exam_comparison(stats: dict, roll_no: str) -> str:
    """Bar chart: exam marks per subject."""
    out_dir = _ensure_dir(os.path.join(CHART_DIR_BASE, roll_no))
    out_path = os.path.join(out_dir, "exam_comparison.png")

    by_subject = stats["exams"]["by_subject"]
    fig, ax = plt.subplots(figsize=(6, 3))

    if not by_subject:
        ax.text(0.5, 0.5, "No exam data", ha="center", va="center", fontsize=11, color="gray")
        ax.axis("off")
    else:
        subjects = list(by_subject.keys())
        marks = [by_subject[s] for s in subjects]
        colors = ["#4A90D9", "#E67E22", "#27AE60", "#9B59B6", "#E74C3C"]

        bars = ax.bar(subjects, marks, color=colors[:len(subjects)], width=0.4)
        for bar, val in zip(bars, marks):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val}", ha="center", va="bottom", fontsize=8, fontweight="bold")

        ax.set_title("Exam Marks by Subject", fontsize=11, fontweight="bold")
        ax.set_ylim(0, 115)
        ax.grid(axis="y", alpha=0.3)

    fig.savefig(out_path, dpi=80, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_all_charts(stats: dict) -> dict:
    """Generate all 3 charts quickly."""
    roll_no = stats["student"]["roll_no"]
    return {
        "attendance": chart_attendance_trend(stats, roll_no),
        "tests": chart_test_trend(stats, roll_no),
        "exams": chart_exam_comparison(stats, roll_no),
    }
