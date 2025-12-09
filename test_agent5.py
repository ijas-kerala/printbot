import sys
import os
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.models import Job

# Seed DB for charts
def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Check if empty
    if db.query(Job).count() == 0:
        db.add(Job(filename="test1.pdf", status="completed", total_cost=10.0))
        db.add(Job(filename="test2.pdf", status="failed", total_cost=0.0))
        db.add(Job(filename="test3.pdf", status="paid", total_cost=50.0))
        db.commit()
    db.close()

def test_admin_flow():
    client = TestClient(app)
    
    # 1. Login
    # Note: Redirects are followed by default in TestClient usually, checking final url or cookies
    response = client.post("/admin/login", data={"username": "admin", "password": "password123"}, follow_redirects=False)
    assert response.status_code == 303
    assert "admin_user" in response.cookies
    
    # Set cookie for subsequent requests
    client.cookies.set("admin_user", "admin")
    
    # 2. Dashboard Access
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    assert "Total Revenue" in response.text
    
    # 3. Stats API
    response = client.get("/admin/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "data" in data
    
    # 4. Pricing Update
    response = client.post("/admin/api/pricing", data={"price": 10.0}, follow_redirects=False)
    assert response.status_code == 303
    
    print("Agent 5 Admin Verification Complete.")

if __name__ == "__main__":
    seed_data()
    test_admin_flow()
