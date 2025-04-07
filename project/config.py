from typing import Optional
import os
from dotenv import load_dotenv
import nltk

load_dotenv()

UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "UPLOAD_FOLDER")
MAX_FILES: int = int(os.getenv("MAX_FILES", "MAX_FILES"))
ALLOWED_PDF_COUNT: int = int(os.getenv("ALLOWED_PDF_COUNT", "ALLOWED_PDF_COUNT"))
ALLOWED_DOCX_COUNT: int = int(os.getenv("ALLOWED_DOCX_COUNT", "ALLOWED_DOCX_COUNT"))
SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS: bool = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "SQLALCHEMY_TRACK_MODIFICATIONS").lower() == "true"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def configure_dependencies() -> None:
    """Configure Tesseract and download NLTK resources.

    This function ensures Tesseract and NLTK dependencies are set up for text extraction.
    """
    import pytesseract
    nltk.download("punkt_tab", quiet=True)