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
        existing_columns = [info[1] for info in cursor.fetchall()]
        
        expected_columns = {
            "total_pages": "INTEGER DEFAULT 0",
            "page_range": "STRING NULL"
        }

        for col_name, col_def in expected_columns.items():
            if col_name not in existing_columns:
                print(f"Adding missing column '{col_name}' to 'jobs' table...")
                try:
                    cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_def}")
                    conn.commit()
                    print(f"Added column '{col_name}'.")
                except Exception as e:
                    print(f"Failed to add column '{col_name}': {e}")
            else:
                print(f"Column '{col_name}' already exists. No action needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
