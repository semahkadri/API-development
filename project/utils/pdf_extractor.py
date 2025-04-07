import pdfplumber
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
            extracted = text.strip()
            logger.info(f"Extracted PDF text from {file_path}: {extracted[:50]}...")
            return extracted
    except Exception as e:
        logger.error(f"Error extracting PDF text from {file_path}: {str(e)}")
        return ""