import razorpay
import qrcode
import io
import base64
from app.core.config import settings

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_payment_link(self, amount: float, description: str, reference_id: str, customer_email: str = "guest@printbot.local", customer_contact: str = "9999999999"):
        """
        Creates a Razorpay Payment Link and returns the short URL and a base64 QR code.
        Amount is in INR, will be converted to paise.
        """
        amount_paise = int(amount * 100)
        
        data = {
            "amount": amount_paise,
            "currency": settings.RAZORPAY_CURRENCY,
            "accept_partial": False,
            "description": description,
            "reference_id": reference_id,
            "customer": {
                "name": "PrintBot User",
                "email": customer_email,
                "contact": customer_contact
            },
            "notify": {
                "sms": False,
                "email": False
            },
            "reminder_enable": False,
            "notes": {
                "source": "PrintBot Kiosk"
            }
        }
        
        try:
            payment_link = self.client.payment_link.create(data)
            short_url = payment_link.get('short_url')
            payment_link_id = payment_link.get('id')
            
            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(short_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "short_url": short_url,
                "payment_link_id": payment_link_id,
                "qr_code_base64": img_str,
                "status": payment_link.get('status')
            }
            
        except Exception as e:
            print(f"Error creating Razorpay link: {e}")
            return None

    def fetch_payment_link_status(self, payment_link_id: str):
        try:
            return self.client.payment_link.fetch(payment_link_id)
        except Exception as e:
            print(f"Error fetching payment link: {e}")
            return None

razorpay_service = RazorpayService()
