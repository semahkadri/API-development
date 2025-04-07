import os
import nltk

UPLOAD_FOLDER: str = "uploads/"
MAX_FILES: int = 40
ALLOWED_PDF_COUNT: int = 20
ALLOWED_DOCX_COUNT: int = 20

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def configure_dependencies() -> None:
    """Configure Tesseract and download NLTK resources."""
    import pytesseract
    nltk.download("punkt_tab", quiet=True)