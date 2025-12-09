from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.models import Job, PricingRule
from app.core.config import settings
import datetime

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# Simple Hardcoded credential for now
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123" 

def get_current_user(request: Request):
    user = request.cookies.get("admin_user")
    if not user:
        return None
    return user

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_user", value="admin")
        return response
    else:
        # Redirect back with error? For now just fail.
        return RedirectResponse(url="/admin/login?error=Invalid Credentials", status_code=303)

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_user")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/admin/login")
    
    # Stats
    total_jobs = db.query(Job).count()
    completed_jobs = db.query(Job).filter(Job.status == "completed").count()
    failed_jobs = db.query(Job).filter(Job.status.contains("failed")).count()
    
    # Calculate total revenue from completed/paid jobs
    # Assuming 'paid' jobs also count towards revenue even if they failed printing later, 
    # but strictly 'paid' status is most accurate for money collected.
    # Job doesn't have a 'paid_amount' field directly accessible easily without joining Payment, 
    # but we added total_cost column to Job in Agent 1.
    revenue_query = db.query(func.sum(Job.total_cost)).filter(Job.status.in_(["paid", "processing", "printing", "completed"])).scalar()
    total_revenue = revenue_query if revenue_query else 0.0

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "total_revenue": total_revenue,
        "price_per_page": settings.PRICE_PER_PAGE
    })

@router.get("/api/stats")
def get_stats(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: raise HTTPException(status_code=401)
    
    # Last 7 days chart data
    today = datetime.date.today()
    dates = []
    revenues = []
    
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        # SQLite date handling can be tricky, using simple string match or range if datetime stored correctly.
        # Job.created_at is DateTime.
        # We'll do a rough python-side aggregation for simplicity if SQL is complex.
        # Actually, let's just mock specific day query or do basic.
        
        # Simple/Naive: Fetch all jobs for that day
        start_dt = datetime.datetime.combine(d, datetime.time.min)
        end_dt = datetime.datetime.combine(d, datetime.time.max)
        
        day_rev = db.query(func.sum(Job.total_cost)).filter(
            Job.created_at >= start_dt,
            Job.created_at <= end_dt,
            Job.status.in_(["paid", "processing", "printing", "completed"])
        ).scalar()
        
        dates.append(d.strftime("%Y-%m-%d"))
        revenues.append(day_rev if day_rev else 0.0)
        
    return {"labels": dates, "data": revenues}

@router.post("/api/pricing")
def update_pricing(price: float = Form(...), user: str = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    
    # Update settings
    # Since settings is a pydantic BaseSettings loaded from env, updating it 'live' 
    # only affects memory, not the .env file.
    # For persistence, we should probably check if we have a DB override.
    # For this task, updating memory is "okay" but a restart resets it. 
    # Ideally we'd overwrite .env or use a DB setting.
    # Let's simple update the in-memory settings.
    settings.PRICE_PER_PAGE = price
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@router.get("/api/jobs")
def get_jobs(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: raise HTTPException(status_code=401)
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return jobs
