import time
import traceback
from sqlalchemy.orm import Session
from core.database import SessionLocal
from web.models.models import Job
from web.services.printer_service import printer_service

class JobProcessor:
    def process_pending_jobs(self):
        """
        Main loop to find and process paid jobs.
        """
        db: Session = SessionLocal()
        try:
            # Find a single job to process
            job = db.query(Job).filter(Job.status == "paid").first()
            if job:
                self.process_single_job(job.id)
        except Exception as e:
            print(f"Job Scheduler Error: {e}")
        finally:
            db.close()

    def process_single_job(self, job_id: int):
        """
        Process a specific job with robust error handling and retries.
        """
        db: Session = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return

        print(f"Build-Proof Processor: Starting Job #{job.id}")
        
        try:
            # 1. Mark Processing
            job.status = "processing"
            db.commit()

            # 2. Conversion Phase
            print(f" -> Converting: {job.file_path}")
            final_pdf = printer_service.convert_to_pdf(job.file_path)
            
            if not final_pdf:
                raise Exception("Conversion returned None")

            # 3. Printing Phase
            print(f" -> Printing: {final_pdf} | Copies: {job.copies} | Duplex: {job.is_duplex} | Range: {job.page_range}")
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
                job.status = "completed"
                print(f" -> SUCCESS. CUPS Job ID: {cups_job_id}")
            else:
                raise Exception("CUPS submission failed (No Job ID)")

            db.commit()

        except Exception as e:
            print(f" -> FAILURE for Job #{job.id}: {e}")
            traceback.print_exc()
            
            # Simple Retry Logic (could be expanded to a retry_count column)
            # For now, mark as failed so we don't loop infinitely on a bad file
            job.status = "failed" 
            # In a real retry system: if job.retries < 3: job.retries += 1; job.status = "paid"
            
            db.commit()
        finally:
            db.close()

job_processor = JobProcessor()
