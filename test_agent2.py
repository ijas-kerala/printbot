import sys
import os
import shutil
# Add project root to python path
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from web.main import app
from core.database import Base, engine

client = TestClient(app)

def setup():
    # Re-create tables
    Base.metadata.create_all(bind=engine)
    # Ensure upload dir exists
    os.makedirs("uploads", exist_ok=True)

def test_upload_flow():
    # 1. Test Upload
    with open("test_upload.pdf", "wb") as f:
        f.write(b"%PDF-1.4 mock pdf content")
    
    with open("test_upload.pdf", "rb") as f:
        response = client.post("/upload", files={"file": ("test_upload.pdf", f, "application/pdf")})
    
    assert response.status_code == 200
    assert "Print Settings" in response.text
    
    # Extract job ID (naive way or just assume it is 1 if fresh db)
    # For robust test, we would parse response, but HTML parsing is messy here.
    # Let's assume job_id=1 for this fresh test
    job_id = 1
    
    # 2. Test Settings Render
    response = client.get(f"/settings/{job_id}")
    assert response.status_code == 200
    assert "Copies" in response.text
    
    # 3. Test Update Settings (HTMX)
    response = client.post(f"/update-settings/{job_id}", data={"copies": 2, "is_duplex": False})
    assert response.status_code == 200
    assert "Total" in response.text
    
    # 4. Cleanup
    os.remove("test_upload.pdf")
    shutil.rmtree("uploads", ignore_errors=True)
    os.makedirs("uploads", exist_ok=True)
    print("Agent 2 verification (Upload & Settings Flow) complete.")

if __name__ == "__main__":
    setup()
    try:
        test_upload_flow()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
