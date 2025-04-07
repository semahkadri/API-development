from docx import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_docx_text(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + " "
        extracted = text.strip()
        logger.info(f"Extracted DOCX text from {file_path}: {extracted[:50]}...")
        return extracted
    except Exception as e:
        logger.error(f"Error extracting DOCX text from {file_path}: {str(e)}")
        return ""