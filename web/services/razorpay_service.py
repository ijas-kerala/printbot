import razorpay
import qrcode
import io
import base64
from core.config import settings

class RazorpayService:
    def __init__(self):
        self.enabled = False
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET and settings.RAZORPAY_KEY_ID != "your_key_id_here":
            try:
                self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                self.enabled = True
            except Exception as e:
                print(f"Razorpay Client Init Failed: {e}")
        else:
            print("⚠ Razorpay Keys missing or default. Payment Service running in MOCK mode.")

    def create_payment_link(self, amount: float, description: str, reference_id: str, customer_email: str = "guest@printbot.local", customer_contact: str = "9999999999"):
        """
        Creates a Razorpay Payment Link and returns the short URL and a base64 QR code.
        If disabled, returns a MOCK link.
        """
        # MOCK MODE
        if not self.enabled:
            print("Creating MOCK Payment Link")
            try:
                # Generate a dummy QR encoding the mock link
                mock_url = f"http://mock-payment?ref={reference_id}&amt={amount}"
                qr = qrcode.QRCode(box_size=10, border=4)
                qr.add_data(mock_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return {
                    "short_url": mock_url,
                    "payment_link_id": f"plink_mock_{reference_id}",
                    "qr_code_base64": img_str,
                    "status": "created"
                } 
            except Exception as e:
                print(f"Mock QR Gen Error: {e}")
                return None

        # REAL MODE
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
            },
            # "callback_url": "https://your-domain.com/payment-success", # Optional
            # "callback_method": "get"
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
