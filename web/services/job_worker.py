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
    while True:
        try:
            db: Session = SessionLocal()
            # 1. Check for PAID jobs
            # We want to lock the row? SQLite doesn't strictly support FOR UPDATE well.
            # We'll just fetch one.
            job = db.query(Job).filter(Job.status == "paid").first()
            
            if job:
                print(f"Processing Job #{job.id}...")
                job.status = "processing"
                db.commit()
                
                # Conversion
                final_pdf = printer_service.convert_to_pdf(job.file_path)
                
                if final_pdf:
                    # Printing
                    job.status = "printing"
                    db.commit()
                    
                    cups_job_id = printer_service.print_job(
                        final_pdf, 
                        job.id, 
                        copies=job.copies, 
                        is_duplex=job.is_duplex,
                        page_range=job.page_range
                    )
                    
                    if cups_job_id:
                        job.status = "completed" # Technically 'sent_to_printer'
                        # We could poll CUPS for actual completion
                    else:
                        job.status = "failed_printer_error"
                else:
                    job.status = "failed_conversion_error"
                
                db.commit()
            
            db.close()
            
        except Exception as e:
            print(f"Job Worker Error: {e}")
            traceback.print_exc()
        
        time.sleep(5) # Poll every 5 seconds

def start_worker():
    thread = threading.Thread(target=process_jobs, daemon=True)
    thread.start()
