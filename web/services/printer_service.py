import os
import subprocess
import cups
import fitz  # PyMuPDF
import img2pdf
from PIL import Image
from core.config import settings

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

    def print_job(self, file_path: str, job_id: int, copies: int = 1, is_duplex: bool = False, page_range: str = None):
        """
        Sends the PDF to CUPS (or Mocks it).
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        # 1. Apply Page Slicing
        to_print_path = self.apply_page_range(file_path, page_range)

        # 2. Mock Mode
        if self.mock_mode:
            print(f" [MOCK PRINT] File: {to_print_path} | Copies: {copies} | Duplex: {is_duplex}")
            return 123456 # Fake Job ID

        # 3. Real CUPS Mode
        options = {
            "copies": str(copies),
            "media": "iso_a4_210x297mm", # Default to A4
            # "fit-to-page": "True"
        }

        if is_duplex:
            options["sides"] = "two-sided-long-edge"
        else:
            options["sides"] = "one-sided"

        job_title = f"PrintBot_Job_{job_id}"

        try:
            # Check if printer exists
            printers = self.conn.getPrinters()
            printer_target = self.printer_name
            
            if printer_target not in printers:
                print(f"Printer {self.printer_name} not found. Available: {list(printers.keys())}")
                if printers:
                    printer_target = list(printers.keys())[0] # Fallback
                else:
                    raise Exception("No printers found in CUPS.")

            print_job_id = self.conn.printFile(printer_target, to_print_path, job_title, options)
            print(f"Sent to CUPS ({printer_target}). Job ID: {print_job_id}")
            return print_job_id
        except Exception as e:
            print(f"Printing failed: {e}")
            return None

printer_service = PrinterService()
