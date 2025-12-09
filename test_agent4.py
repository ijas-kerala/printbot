import sys
import os
import time
from unittest.mock import MagicMock
import shutil

sys.path.append(os.getcwd())

# Mock cups before importing printer_service if possible, 
# but printer_service imports cups at top level.
# We will intercept the class instance in the test.

from app.services.printer_service import printer_service

def test_conversion():
    # create dummy text file
    with open("test.txt", "w") as f:
        f.write("Hello World")
    
    pdf = printer_service.convert_to_pdf("test.txt")
    if pdf and os.path.exists(pdf) and pdf.endswith(".pdf"):
        print("Conversion (TXT->PDF) successful.")
    else:
        print("Conversion failed.")
        sys.exit(1)
        
    os.remove("test.txt")
    if pdf: os.remove(pdf)

def test_mock_print():
    # Mock the CUPS connection
    printer_service.conn = MagicMock()
    printer_service.conn.getPrinters.return_value = {"Canon_LBP122dw": {}}
    printer_service.conn.printFile.return_value = 12345
    
    # Create dummy pdf
    with open("dummy.pdf", "wb") as f:
        f.write(b"%PDF-1.4 mock")
        
    settings = {"copies": 1, "is_duplex": True}
    job_id = printer_service.print_job("dummy.pdf", 1, **settings)
    
    if job_id == 12345:
        print("Print job sent to (Mock) CUPS successfully.")
    else:
        print("Print job failed.")
        sys.exit(1)
        
    printer_service.conn.printFile.assert_called()
    os.remove("dummy.pdf")

if __name__ == "__main__":
    # Wait for dependencies? Assume installed if running this.
    try:
        import cups
        import fitz
    except ImportError:
        print("Missing dependencies (pycups/pymupdf).")
        # sys.exit(1) # Don't fail hard if apt is still running in background
    
    try:
        test_conversion()
        test_mock_print()
        print("Agent 4 Verification Complete.")
    except Exception as e:
        print(f"Agent 4 Verification Failed: {e}")
        sys.exit(1)
