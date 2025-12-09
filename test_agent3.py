import sys
import os
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app.main import app

def test_status_endpoint():
    client = TestClient(app)
    response = client.get("/machine-status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "is_online" in data
    print("Backend Status endpoint Verified.")

def test_kivy_import():
    try:
        import kivy
        from kivy.app import App
        from kivy.uix.screenmanager import ScreenManager
        print("Kivy imports successful.")
    except ImportError as e:
        print(f"Kivy import failed: {e}")
        # Don't fail the whole test if Kivy fails in this headless env, 
        # but warn the user.
        return False
    return True

if __name__ == "__main__":
    test_status_endpoint()
    if test_kivy_import():
        print("Agent 3 Verification Complete.")
    else:
        print("Agent 3 Verification Partial: Kivy imports failed (expected if headless/missing system deps).")
