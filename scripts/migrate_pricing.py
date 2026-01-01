import sys
import os

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine

def migrate():
    print("Migrating PricingRule table...")
    with engine.connect() as conn:
        try:
            # Check if column exists (naive check)
            conn.execute(text("SELECT is_duplex FROM pricing_rules LIMIT 1"))
            print("Column 'is_duplex' already exists.")
        except Exception:
            print("Adding 'is_duplex' column...")
            try:
                conn.execute(text("ALTER TABLE pricing_rules ADD COLUMN is_duplex BOOLEAN DEFAULT 0"))
                conn.commit()
                print("Migration successful.")
            except Exception as e:
                print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
