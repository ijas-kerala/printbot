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


from web.services.cleanup_service import cleanup_service

def cleanup_worker():
    """
    Background worker that runs cleanup periodically.
    """
    while True:
        try:
            cleanup_service.cleanup_old_jobs()
            # Run cleanup every 1 hour (3600 seconds)
            time.sleep(3600)
        except Exception as e:
            print(f"Cleanup Worker Error: {e}")
            time.sleep(300) # Retry in 5 mins if error

def start_worker():
    # Job Processor Thread
    processing_thread = threading.Thread(target=process_jobs, daemon=True)
    processing_thread.start()
    
    # Cleanup Thread
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

