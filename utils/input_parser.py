"""
utils/input_parser.py
---------------------
Extracts Name, Class, and Roll No from WhatsApp message text.

ALL THREE are required to uniquely identify a student:
  - Same roll number can exist across different classes
  - Name is used as an extra validation check

Handles inputs like:
  "Name: Rahul, Class: 10A, Roll: 23"
  "name=Priya class=10B roll=7"
  "Rahul / 10A / 23"
"""

import re


REQUIRED_FIELDS = ["name", "class", "roll_no"]


def parse_student_input(text: str) -> dict:
    """
    Extract all 3 required fields from free-form text.

    Returns:
    {
        "name":    str | None,
        "class":   str | None,
        "roll_no": str | None,
        "missing": list[str],   # list of missing field labels (empty if all found)
    }
    """
    text = text.strip()

    result = {
        "name":    _extract_name(text),
        "class":   _extract_class(text),
        "roll_no": _extract_roll(text),
    }

    missing = []
    if not result["name"]:
        missing.append("Name")
    if not result["class"]:
        missing.append("Class")
    if not result["roll_no"]:
        missing.append("Roll No")

    result["missing"] = missing
    return result


def is_complete(parsed: dict) -> bool:
    """Returns True only if all 3 fields were found."""
    return len(parsed["missing"]) == 0


# ── field extractors ─────────────────────────────────────────────────────────

def _extract_name(text: str) -> str | None:
    # "Name: Rahul" / "Name = Rahul" / "name - Rahul"
    match = re.search(
        r"\bname\s*[:\-=]\s*([A-Za-z][A-Za-z ]{0,49})(?:\s*[,\n]|$)",
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # Slash format: "Rahul / 10A / 23"  (Name is first segment)
    slash = _try_slash_format(text)
    if slash:
        return slash.get("name")

    return None


def _extract_class(text: str) -> str | None:
    # "Class: 10A" / "class = 10B"
    match = re.search(
        r"\bclass\s*[:\-=]\s*([A-Za-z0-9]{1,10})",
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip().upper()

    slash = _try_slash_format(text)
    if slash:
        return slash.get("class")

    return None


def _extract_roll(text: str) -> str | None:
    # "Roll: 23" / "Roll No: 007" / "Roll Number = 5"
    match = re.search(
        r"\broll[\w\s]*[:\-=]\s*(\d+)",
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # "roll is 23"
    match = re.search(r"\broll[\w\s]*\bis\b\s*(\d+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # "for roll 99"
    match = re.search(r"\bfor\s+roll[\w\s]*\s+(\d+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    slash = _try_slash_format(text)
    if slash:
        return slash.get("roll_no")

    return None


def _try_slash_format(text: str) -> dict | None:
    """
    Tries to parse 'Rahul / 10A / 23' style input.
    Returns {"name": ..., "class": ..., "roll_no": ...} or None.
    """
    parts = [p.strip() for p in re.split(r"[/|,]", text)]
    parts = [p for p in parts if p]  # remove empty

    if len(parts) == 3:
        name_part, class_part, roll_part = parts
        if re.fullmatch(r"\d+", roll_part):   # last part is a number
            return {
                "name":    name_part if re.match(r"[A-Za-z]", name_part) else None,
                "class":   class_part.upper() if re.match(r"[A-Za-z0-9]", class_part) else None,
                "roll_no": roll_part,
            }
    return None


# ── quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        # should pass (all 3 found)
        "Name: Rahul, Class: 10A, Roll: 23",
        "name=Priya class=10B roll=7",
        "Rahul / 10A / 23",
        "Name: Ali, Roll: 5, Class: 9C",
        # partial (should show missing fields)
        "Roll: 23",
        "Name: Rahul, Roll: 23",
        "Class: 10A, Roll: 23",
        # should fail
        "hi",
        "hello there",
    ]

    print(f"{'Input':<45} {'Result'}")
    print("-" * 80)
    for msg in test_cases:
        p = parse_student_input(msg)
        if is_complete(p):
            print(f"  {msg:<43} ✅  Name={p['name']!r}, Class={p['class']!r}, Roll={p['roll_no']!r}")
        else:
            print(f"  {msg:<43} ❌  Missing: {p['missing']}")
