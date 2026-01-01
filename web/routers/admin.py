from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from web.models.models import Job, PricingRule
from core.config import settings
import datetime

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="web/templates")

templates = Jinja2Templates(directory="web/templates")

@router.get("/", include_in_schema=False)
def admin_root_redirect():
    return RedirectResponse(url="/admin/login") 
# "Z" shape: 1->2->3 -> 5 -> 7->8->9 
# Wait, standard keypad:
# 1 2 3
# 4 5 6
# 7 8 9
# Z pattern: 1->2->3 -> 5 -> 7->8->9
ADMIN_PATTERN = "1235789" 
ADMIN_PIN = "1234"

def get_current_user(request: Request):
    user = request.cookies.get("admin_user")
    if not user:
        return None
    return user

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/login/pattern")
def login_pattern(response: Response, pattern: str = Form(...)):
    if pattern == ADMIN_PATTERN:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_user", value="admin")
        return response
    else:
        return RedirectResponse(url="/admin/login?error=Invalid Pattern", status_code=303)

@router.post("/login")
def login(response: Response, password: str = Form(...)): # PIN input usually named password
    if password == ADMIN_PIN:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_user", value="admin")
        return response
    else:
        return RedirectResponse(url="/admin/login?error=Invalid PIN", status_code=303)

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

    # Recent Jobs
    recent_jobs = db.query(Job).order_by(Job.created_at.desc()).limit(10).all()
    pricing_rules = db.query(PricingRule).order_by(PricingRule.min_pages.asc()).all()

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "total_revenue": total_revenue,
        "price_per_page": settings.PRICE_PER_PAGE,
        "recent_jobs": recent_jobs,
        "pricing_rules": pricing_rules
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

@router.post("/api/pricing-rule/delete")
def delete_pricing_rule(rule_id: int = Form(...), user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: raise HTTPException(status_code=401)
    db.query(PricingRule).filter(PricingRule.id == rule_id).delete()
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@router.post("/api/pricing-rule/add")
def add_pricing_rule(
    min_pages: int = Form(...),
    max_pages: str = Form(None), # Accepts empty string
    is_duplex: str = Form(None), # Checkbox
    price: float = Form(...),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user: raise HTTPException(status_code=401)
    
    # Clean max_pages
    max_p = None
    if max_pages and max_pages.strip():
        max_p = int(max_pages)
        
    is_duplex_bool = True if is_duplex == 'on' else False
    
    new_rule = PricingRule(
        min_pages=min_pages,
        max_pages=max_p,
        is_duplex=is_duplex_bool,
        price_per_page=price
    )
    db.add(new_rule)
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)

# Deprecated simple price updater, kept or removed? 
# The UI will replace it, so we can remove or keep for legacy. 
# Let's remove it to avoid confusion.


@router.get("/api/jobs")
def get_jobs(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: raise HTTPException(status_code=401)
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return jobs
