from fastapi import APIRouter, UploadFile, File, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.database import get_db
from web.models.models import Job
import shutil
import os
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_upload_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

import fitz  # PyMuPDF

@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # 1. Validate file type
        allowed_types = ["application/pdf", "image/jpeg", "image/png", 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        
        if file.content_type not in allowed_types:
             return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid file type. Only PDF, JPG, PNG, DOCX allowed."})

        # 2. Validate Size (90MB Limit)
        MAX_SIZE = 90 * 1024 * 1024
        # Check size if content-length header is present (fast fail)
        if request.headers.get('content-length') and int(request.headers.get('content-length')) > MAX_SIZE:
             return templates.TemplateResponse("index.html", {"request": request, "error": "File too large (Max 90MB)"})
        
        # 3. Save file safely
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Read and write chunks to avoid memory spikes, and check size while writing
        size = 0
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024) # 1MB chunks
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_SIZE:
                    os.remove(file_path) # Clean up partial
                    return templates.TemplateResponse("index.html", {"request": request, "error": "File too large (Max 90MB)"})
                buffer.write(chunk)
            
        # 4. Accurate Page Counting
        page_count = 1
        try:
            if file_ext == ".pdf":
                doc = fitz.open(file_path)
                page_count = doc.page_count
                doc.close()
            # Images and DOCX default to 1 for now (DOCX calculated after conversion)
        except Exception as e:
            print(f"Page count error: {e}")
            # Fallback to 1, don't fail upload just for this
            page_count = 1

        new_job = Job(
            id=str(uuid.uuid4()),
            filename=file.filename,
            file_path=file_path,
            page_count=page_count,
            status="uploaded"
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # Redirect to settings page
        return RedirectResponse(
            url=f"/print-settings?file_id={new_job.id}", 
            status_code=303
        )

    except Exception as e:
        print(f"Upload Error: {e}")
        return templates.TemplateResponse("index.html", {"request": request, "error": "System Error during upload. Please try again."})

