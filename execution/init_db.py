import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service

def main():
    print("🚀 Initializing MySQL Database and Tables...")
    try:
        db_service.init_db()
        print("✅ MySQL Database Ready!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
