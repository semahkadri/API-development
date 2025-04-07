from typing import Optional
import os
from dotenv import load_dotenv
import nltk

load_dotenv()

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "UPLOAD_FOLDER")
MAX_FILES = int(os.getenv("MAX_FILES", "MAX_FILES"))
ALLOWED_PDF_COUNT = int(os.getenv("ALLOWED_PDF_COUNT", "ALLOWED_PDF_COUNT"))
ALLOWED_DOCX_COUNT = int(os.getenv("ALLOWED_DOCX_COUNT", "ALLOWED_DOCX_COUNT"))
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "SQLALCHEMY_TRACK_MODIFICATIONS").lower() == "true"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def configure_dependencies():
    """Configure Tesseract and download NLTK resources.

    This function ensures Tesseract and NLTK dependencies (punkt_tab and stopwords) are set up for text extraction and analysis.

    Raises:
        ImportError: If required libraries are not installed.
    """
    import pytesseract
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)