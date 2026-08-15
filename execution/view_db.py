import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.db_service import db_service

def main():
    print("==========================================")
    print("       MySQL Database Inspector           ")
    print("==========================================")

    try:
        # Check tables
        tables_query = "SHOW TABLES"
        tables = db_service.execute_query(tables_query)
        
        if not tables:
            print("⚠️ No tables found in database!")
            return

        table_names = [list(t.values())[0] for t in tables]
        print(f"📊 Tables found ({len(table_names)}): {', '.join(table_names)}\n")

        for table in table_names:
            count_query = f"SELECT COUNT(*) as total FROM {table}"
            count_res = db_service.execute_query(count_query, fetchone=True)
            total = count_res["total"] if count_res else 0
            
            print(f"------------------------------------------")
            print(f"📁 Table: {table} (Total rows: {total})")
            print(f"------------------------------------------")

            if total > 0:
                sample_query = f"SELECT * FROM {table} LIMIT 5"
                rows = db_service.execute_query(sample_query)
                print(json.dumps(rows, indent=2, default=str))
            else:
                print("   (Table is empty)")
            print("\n")

    except Exception as e:
        print(f"❌ Error connecting to MySQL: {e}")
        print("\n💡 Make sure MySQL server is running and .env configuration is correct.")

if __name__ == "__main__":
    main()
