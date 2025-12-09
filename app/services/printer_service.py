import os
import subprocess
import cups
import fitz  # PyMuPDF
import img2pdf
from PIL import Image
from app.core.config import settings

class PrinterService:
    def __init__(self):
        self.conn = cups.Connection()
        self.printer_name = settings.PRINTER_NAME

    def convert_to_pdf(self, input_path: str) -> str:
        """
        Converts generic file types to PDF.
        Returns the path to the converted PDF.
        """
        base, ext = os.path.splitext(input_path)
        output_pdf = f"{base}.pdf"
        ext = ext.lower()

        try:
            if ext == ".pdf":
                return input_path
            
            elif ext in [".jpg", ".jpeg", ".png"]:
                # Convert Image to PDF
                with open(output_pdf, "wb") as f:
                    f.write(img2pdf.convert(input_path))
                return output_pdf
            
            elif ext in [".docx", ".doc", ".txt"]:
                # Use LibreOffice for doc conversion
                # --headless --convert-to pdf --outdir <dir> <file>
                cmd = [
                    "libreoffice", "--headless", "--convert-to", "pdf",
                    "--outdir", os.path.dirname(input_path),
                    input_path
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return output_pdf
            
            else:
                raise ValueError(f"Unsupported file type: {ext}")
                
        except Exception as e:
            print(f"Conversion failed: {e}")
            return None

    def print_job(self, file_path: str, job_id: int, copies: int = 1, is_duplex: bool = False):
        """
        Sends the PDF to CUPS.
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False

        options = {
            "copies": str(copies),
            "media": "iso_a4_210x297mm", # Default to A4
        }

        if is_duplex:
            options["sides"] = "two-sided-long-edge"
        else:
            options["sides"] = "one-sided"

        job_title = f"PrintBot_Job_{job_id}"

        try:
            # Check if printer exists
            printers = self.conn.getPrinters()
            if self.printer_name not in printers:
                print(f"Printer {self.printer_name} not found. Available: {list(printers.keys())}")
                # Fallback to first available or error?
                # For now, just print to default if mismatch, or fail.
                if not printers:
                    raise Exception("No printers found in CUPS.")
                # self.printer_name = list(printers.keys())[0] # Auto-fallback? User requested Canon specifically.

            print_job_id = self.conn.printFile(self.printer_name, file_path, job_title, options)
            print(f"Sent to CUPS. Job ID: {print_job_id}")
            return print_job_id
        except Exception as e:
            print(f"Printing failed: {e}")
            return None

printer_service = PrinterService()
