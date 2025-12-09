from fastapi import APIRouter, File, UploadFile, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from app.core.database import get_db
from app.models.models import Job
from sqlalchemy.orm import Session
import shutil
import os
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_upload_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    if file.content_type not in allowed_types:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid file type"})

    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create Job record (Basic stub for page count)
    # TODO: Implement real page counting logic in Agent 4
    mock_page_count = 1 
    
    new_job = Job(
        filename=file.filename,
        file_path=file_path,
        page_count=mock_page_count,
        status="uploaded"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # Redirect to settings page (return HTMX snippet/redirect)
    from app.routers.print_settings import render_settings
    return render_settings(request, new_job.id, db)

