import time
import threading
from sqlalchemy.orm import Session
from core.database import SessionLocal
from web.models.models import Job
from web.services.printer_service import printer_service
import traceback

def process_jobs():
    """
    Background worker that checks for 'paid' jobs and processes them.
    In a real app, this might be a Celery task.
    """
from web.services.job_processor import job_processor

def process_jobs():
    """
    Background worker that checks for 'paid' jobs and processes them.
    RELIABILITY MODE: Uses JobProcessor.
    """
    while True:
        try:
            job_processor.process_pending_jobs()
        except Exception as e:
            print(f"Worker Loop Critical Error: {e}")
            traceback.print_exc()
        
        time.sleep(5) # Poll every 5 seconds

def start_worker():
    thread = threading.Thread(target=process_jobs, daemon=True)
    thread.start()

