from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.core.database import get_db
from app.models.models import Job
from sqlalchemy.orm import Session
from app.core.config import settings as config_settings
from app.services.razorpay_service import razorpay_service
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def calculate_cost(pages: int, copies: int, is_duplex: bool, price_per_page: float) -> float:
    # Basic logic: simple multiplication
    # Duplex logic: usually duplex saves paper but we might charge same per 'side' or discount
    # For now, let's assume price is per 'impression' (side).
    # If duplex and 2 pages, that is 1 sheet but 2 sides -> 2 * price (simple)
    return pages * copies * price_per_page

@router.get("/settings/{job_id}", response_class=HTMLResponse)
def render_settings(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Calculate initial cost
    total_cost = calculate_cost(job.page_count, job.copies, job.is_duplex, config_settings.PRICE_PER_PAGE)
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "job": job,
        "price_per_page": config_settings.PRICE_PER_PAGE,
        "total_cost": total_cost
    })

@router.post("/update-settings/{job_id}", response_class=HTMLResponse)
async def update_settings(
    request: Request, 
    job_id: int, 
    copies: int = Form(...), 
    is_duplex: bool = Form(False),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.copies = copies
    job.is_duplex = is_duplex
    
    total_cost = calculate_cost(job.page_count, job.copies, job.is_duplex, config_settings.PRICE_PER_PAGE)
    job.total_cost = total_cost
    
    db.commit()
    
    # Return updated price summary partial
    return f"""
    <div id="price-summary" class="bg-gray-50 p-4 rounded-lg border border-gray-200 mt-4">
        <div class="flex justify-between items-center text-sm text-gray-600">
            <span>Pages: {job.page_count}</span>
            <span>x {job.copies} copies</span>
        </div>
        <div class="flex justify-between items-center font-bold text-xl text-blue-600 mt-2">
            <span>Total</span>
            <span>₹{total_cost:.2f}</span>
        </div>
    </div>
    """

@router.post("/confirm-order/{job_id}", response_class=HTMLResponse)
async def confirm_order(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Generate Razorpay Link
    reference_id = f"JOB-{job.id}-{uuid.uuid4().hex[:6]}"
    payment_data = razorpay_service.create_payment_link(
        amount=job.total_cost,
        description=f"Print Job #{job.id}",
        reference_id=reference_id
    )
    
    if not payment_data:
        return "Error creating payment link"
        
    job.razorpay_order_id = payment_data['payment_link_id']
    job.status = "payment_pending"
    db.commit()
    
    return templates.TemplateResponse("pay.html", {
        "request": request,
        "job": job,
        "qr_code": payment_data['qr_code_base64'],
        "payment_url": payment_data['short_url']
    })

@router.get("/check-payment/{job_id}")
async def check_payment(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.razorpay_order_id:
        return {"status": "error"}
        
    status_data = razorpay_service.fetch_payment_link_status(job.razorpay_order_id)
    
    if status_data and status_data.get('status') == 'paid':
        job.status = "paid"
        # In a real app, we would capture the payment ID here too
        db.commit()
        return "PAID"
    
    return "PENDING"
