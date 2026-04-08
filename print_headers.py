import sys
import os

from services.sheets_service import sheets_service

def main():
    for sheet in ["students", "attendance", "tests", "exams"]:
        try:
            ws = sheets_service.get_worksheet(sheet)
            headers = ws.row_values(1)
            print(f"Sheet '{sheet}': {headers}")
        except Exception as e:
            print(f"Error on '{sheet}': {e}")

if __name__ == "__main__":
    main()
