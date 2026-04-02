import json
import os

def generate_string():
    path = "credentials.json"
    if not os.path.exists(path):
        print(f"❌ Error: {path} not found in the current directory.")
        return

    with open(path, "r") as f:
        data = json.load(f)
        single_line = json.dumps(data)
        print("\n--- GOOGLE_CREDENTIALS_JSON (Single Line) ---")
        print(single_line)
        print("-------------------------------------------\n")
        print("✅ Copy the string above and paste it into your Render Environment Variables.")

if __name__ == "__main__":
    generate_string()
