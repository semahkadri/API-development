from typing import Optional
import pdfplumber
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF file using pdfplumber.

    Args:
        file_path: Path to the PDF file.

    Returns:
        str: Extracted text, empty string if extraction fails.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            text_parts: List[str] = [page.extract_text() or "" for page in pdf.pages]
            extracted = " ".join(filter(None, text_parts)).strip()
            logger.info(f"Extracted PDF text from {file_path}: {extracted[:50]}...")
            return extracted
    except Exception as e:
        logger.error(f"Error extracting PDF text from {file_path}: {str(e)}")
        return ""