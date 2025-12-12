import sqlite3
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, Base
from web.models.models import Job

def fix_schema():
    print("Fixing database schema...")
    # Raw SQL to drop the table is safest to ensure clean slate
    # Then let SQLAlchemy recreate it
    try:
        conn = sqlite3.connect('printbot.db')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS jobs")
        conn.commit()
        conn.close()
        print("Dropped 'jobs' table.")
        
        # Recreate using metadata
        Base.metadata.create_all(bind=engine)
        print("Recreated tables from models.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_schema()
