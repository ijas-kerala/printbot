from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from web.models.models import Job
from web.services.razorpay_service import razorpay_service
import json

router = APIRouter(prefix="/webhooks", tags=["payment"])

@router.post("/razorpay")
async def razorpay_webhook(
    request: Request, 
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Razorpay Webhooks (payment.captured, payment.failed).
    """
    if not x_razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing Signature")
        
    body_bytes = await request.body()
    
    # Verify Signature
    if not razorpay_service.verify_webhook_signature(body_bytes, x_razorpay_signature):
        # Optional: In dev/mock mode, we might skip signature checks if we want to test manually
        # But generally, we should fail.
        if razorpay_service.enabled:
             raise HTTPException(status_code=400, detail="Invalid Signature")
    
    try:
        payload = json.loads(body_bytes)
        event = payload.get('event')
        
        if event == 'payment_link.paid':
            pl_entity = payload['payload']['payment_link']['entity']
            pl_id = pl_entity['id']
            # payment_id = pl_entity['payments'][-1]['payment_id'] # Extract if needed
            
            # Find job by Razorpay Order ID (Link ID)
            job = db.query(Job).filter(Job.razorpay_order_id == pl_id).first()
            if job:
                job.status = "paid"
                # job.razorpay_payment_id = payment_id 
                db.commit()
                print(f"Webhook: Job {job.id} marked as PAID via Link {pl_id}")
                
        elif event == 'order.paid':
             # If using Orders API instead of Payment Links
             pass
             
    except Exception as e:
        print(f"Webhook Processing Error: {e}")
        # Return 200 to acknowledge receipt even on internal error to prevent retries
        return {"status": "error_but_received"}
        
    return {"status": "ok"}
