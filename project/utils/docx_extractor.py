from typing import Optional
from docx import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_docx_text(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        str: Extracted text, empty string if extraction fails.
    """
    try:
        doc = Document(file_path)
        text_parts: List[str] = [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]
        extracted = " ".join(text_parts)
        logger.info(f"Extracted DOCX text from {file_path}: {extracted[:50]}...")
        return extracted
    except Exception as e:
        logger.error(f"Error extracting DOCX text from {file_path}: {str(e)}")
        return ""