import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class GoogleSheetsService:
    def __init__(self):
        # Initializing client as None, we will fetch it lazily
        self._client = None
        self._spreadsheet = None

    def _get_spreadsheet(self):
        # Cache the client during the lifecycle of a request
        if self._spreadsheet:
            return self._spreadsheet

        import json
        client = None
        # Priority 1: Check for raw JSON string in env (Best for Cloud/Render)
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
            try:
                info = json.loads(creds_json)
                creds = Credentials.from_service_account_info(info, scopes=SCOPES)
                client = gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Error parsing GOOGLE_CREDENTIALS_JSON: {e}")

        # Priority 2: Check for file path (Best for local dev)
        if not client:
            creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
            full_path = os.path.join(os.path.dirname(__file__), "..", creds_path)
            # Use relative to project root or provided path
            if not os.path.exists(full_path):
                # Fallback to local
                full_path = creds_path

            if os.path.exists(full_path):
                creds = Credentials.from_service_account_file(full_path, scopes=SCOPES)
                client = gspread.authorize(creds)
            else:
                raise FileNotFoundError(
                    "No Google credentials found! Set GOOGLE_CREDENTIALS_JSON in env "
                    f"or provide a credentials.json file. Checked {full_path}"
                )

        sheet_id = os.getenv("GOOGLE_SHEETS_KEY")
        if not sheet_id:
            raise EnvironmentError("GOOGLE_SHEETS_KEY is not set.")
        
        self._client = client
        self._spreadsheet = client.open_by_key(sheet_id)
        return self._spreadsheet

    def get_worksheet(self, sheet_name: str):
        return self._get_spreadsheet().worksheet(sheet_name)

    def get_all_records(self, sheet_name: str):
        return self.get_worksheet(sheet_name).get_all_records()

    def append_row(self, sheet_name: str, row_data: list):
        ws = self.get_worksheet(sheet_name)
        ws.append_row(row_data)

    def append_rows(self, sheet_name: str, rows_data: list):
        ws = self.get_worksheet(sheet_name)
        ws.append_rows(rows_data)

    def update_row(self, sheet_name: str, row_index: int, row_data: list):
        ws = self.get_worksheet(sheet_name)
        ws.update(f'A{row_index}', [row_data])

    def delete_row(self, sheet_name: str, row_index: int):
        ws = self.get_worksheet(sheet_name)
        ws.delete_rows(row_index)

sheets_service = GoogleSheetsService()
