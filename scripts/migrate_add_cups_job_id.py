import sys
import os

# Add parent directory to path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine

def migrate():
    print("Running migration: Adding cups_job_id to jobs table...")
    
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(jobs)"))
            columns = [row.name for row in result]
            
            if "cups_job_id" in columns:
                print("Column 'cups_job_id' already exists. Skipping.")
                return

            # SQLite doesn't support adding columns with constraints easily if there's data, 
            # but nullable integer is fine.
            conn.execute(text("ALTER TABLE jobs ADD COLUMN cups_job_id INTEGER"))
            print("Successfully added 'cups_job_id' column.")
            
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
