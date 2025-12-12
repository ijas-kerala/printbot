from fastapi import APIRouter, Depends
from core.database import get_db
from sqlalchemy.orm import Session
from web.models.models import Job

router = APIRouter()

@router.get("/status")
def get_machine_status(db: Session = Depends(get_db)):
    # Get latest active job
    latest_job = db.query(Job).order_by(Job.created_at.desc()).first()
    
    status_text = "ready"
    state_code = "idle"
    
    if latest_job:
        if latest_job.status == "printing":
            status_text = f"Printing Job #{latest_job.id}"
            state_code = "printing"
        elif latest_job.status == "payment_pending":
            status_text = "Waiting for Payment"
            state_code = "uploading"
        elif latest_job.status == "uploaded":
            status_text = "File Uploaded. configuring..."
            state_code = "uploading"
        elif latest_job.status == "paid":
             status_text = "Processing Job..."
             state_code = "printing"
    
    return {
        "status": status_text,
        "state": state_code,
        "printer": "online",
        "is_online": True,
        "wifi_strength": "Good" # Mock
    }
