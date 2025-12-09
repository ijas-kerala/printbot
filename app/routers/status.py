from fastapi import APIRouter, Depends
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.models import Job

router = APIRouter()

@router.get("/machine-status")
def get_machine_status(db: Session = Depends(get_db)):
    # Get latest active job
    latest_job = db.query(Job).order_by(Job.created_at.desc()).first()
    
    status_text = "Ready"
    if latest_job:
        if latest_job.status == "printing":
            status_text = f"Printing Job #{latest_job.id}"
        elif latest_job.status == "payment_pending":
            status_text = "Waiting for Payment"
        elif latest_job.status == "paid":
             status_text = "Processing Job..."
    
    return {
        "status": status_text,
        "is_online": True,
        "wifi_strength": "Good" # Mock
    }
