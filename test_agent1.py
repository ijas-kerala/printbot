import sys
import os

# Add project root to python path
sys.path.append(os.getcwd())

try:
    from core.database import Base, engine, SessionLocal
    from web.models.models import Job, PricingRule, Payment
    from web.services.razorpay_service import razorpay_service
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_db():
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        # Create a dummy pricing rule
        rule = PricingRule(min_pages=1, price_per_page=5.0)
        db.add(rule)
        db.commit()
        print("Database tables created and write test successful.")
        db.close()
    except Exception as e:
        print(f"Database test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_db()
    print("Agent 1 verification complete.")
