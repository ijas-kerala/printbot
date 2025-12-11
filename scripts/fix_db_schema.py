import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "printbot.db")

def migrate_db():
    print(f"Checking database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "total_pages" not in columns:
            print("Adding missing column 'total_pages' to 'jobs' table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN total_pages INTEGER DEFAULT 0")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column 'total_pages' already exists. No action needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
