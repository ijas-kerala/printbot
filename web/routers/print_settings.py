from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.database import get_db, SessionLocal
from web.models.models import Job
from core.config import settings as config_settings
from web.services.razorpay_service import razorpay_service
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

@router.get("/print-settings", response_class=HTMLResponse)
async def print_settings_page(request: Request, file_id: str):
    # Retrieve job info (or just pass basic info if DB is partial)
    # Ideally fetch job from DB to get estimated page count
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == file_id).first()
    db.close()
    
    total_pages = job.total_pages if job else 1
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "file_id": file_id,
        "total_pages": total_pages,
        "price_per_page": config_settings.PRICE_PER_PAGE
    })

@router.post("/print-settings")
async def process_settings(
    request: Request,
    file_id: str = Form(...),
    copies: int = Form(...),
    page_range: str = Form(""),
    duplex: str = Form(None), # Checkbox sends 'on' or None
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == file_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Logic to parse page range and count actual pages
    from core.printing.page_utils import parse_page_range
    pages_list = parse_page_range(page_range, job.page_count) # job.page_count (from upload) not total_pages (might be wrong attr name)
    actual_pages = len(pages_list)
    
    is_duplex_bool = True if duplex == 'on' else False
    
    # Calculate sheets
    sheets = actual_pages
    if is_duplex_bool:
        import math
        sheets = math.ceil(actual_pages / 2)
        
    total_sheets = sheets * copies
    amount = total_sheets * config_settings.PRICE_PER_PAGE
    
    # Create Razorpay Order/Link
    order_id = f"order_{uuid.uuid4().hex[:8]}" # Default internal ID
    payment_link_url = None
    qr_code_b64 = None
    
    if razorpay_service.enabled:
        try:
            link_data = razorpay_service.create_payment_link(
                amount=amount,
                description=f"Print Job {file_id}",
                reference_id=order_id
            )
            if link_data:
                payment_link_url = link_data.get('short_url')
                order_id = link_data.get('payment_link_id', order_id) # Use RP ID if available? Or store both?
                # Actually, our DB expects razorpay_order_id to be the link ID for webhooks to work
                # But RP link IDs look like 'plink_...' 
                # Let's use the one RP gives us.
                order_id = link_data.get('payment_link_id')
                qr_code_b64 = link_data.get('qr_code_base64')
        except Exception as e:
            print(f"Razorpay Gen Error: {e}")
            # Fallback to mock logic below if RP fails
            pass
    
    # Update Job
    job.copies = copies
    job.page_range = page_range
    job.is_duplex = is_duplex_bool
    job.total_cost = amount
    job.razorpay_order_id = order_id
    job.status = "payment_pending"
    db.commit()
    
    # Redirect to payment page
    import urllib.parse
    redirect_url = f"/payment/{order_id}"
    if payment_link_url:
        encoded_link = urllib.parse.quote(payment_link_url)
        redirect_url += f"?payment_link={encoded_link}"
    
    return RedirectResponse(url=redirect_url, status_code=303)

@router.get("/payment/{order_id}", response_class=HTMLResponse)
async def payment_page(request: Request, order_id: str, payment_link: str = None, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.razorpay_order_id == order_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Generate Razorpay Link if not already (or use static QR logic)
    # If passed in query param, use it (Real Razorpay or Mock Service)
    final_link = payment_link
    
    if not final_link:
        # Fallback (Old Mock Logic)
        final_link = f"upi://pay?pa=test@upi&pn=PrintBot&am={job.total_cost}&tn=PrintOrder"
    
    return templates.TemplateResponse("payment.html", {
        "request": request,
        "amount": job.total_cost,
        "payment_link": final_link,
        "order_id": order_id,
        "qr_url": None # Template handles generating QR from 'payment_link' via JS
    })

@router.get("/payment-status/{order_id}")
async def check_payment_status(order_id: str, db: Session = Depends(get_db)):
    # This endpoint is polled by HTMX
    job = db.query(Job).filter(Job.razorpay_order_id == order_id).first()
    
    if job and job.status == "paid":
        # HTMX Redirect
        response = HTMLResponse()
        response.headers["HX-Redirect"] = "/success"
        return response
        
    # If using test mode, auto-approve payment after a few seconds?
    # For now, return nothing (keep polling)
    return HTMLResponse("", status_code=200)

@router.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})
