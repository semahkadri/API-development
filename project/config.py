from typing import Optional
import os
from dotenv import load_dotenv
import nltk
import logging

logger = logging.getLogger(__name__)

load_dotenv()

UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "UPLOAD_FOLDER")
MAX_FILES: int = int(os.getenv("MAX_FILES", "MAX_FILES"))
ALLOWED_PDF_COUNT: int = int(os.getenv("ALLOWED_PDF_COUNT", "ALLOWED_PDF_COUNT"))
ALLOWED_DOCX_COUNT: int = int(os.getenv("ALLOWED_DOCX_COUNT", "ALLOWED_DOCX_COUNT"))
SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS: bool = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "SQLALCHEMY_TRACK_MODIFICATIONS").lower() == "true"
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "GEMINI_API_KEY")
LLM_ANALYSIS_PROMPT: str = os.getenv("LLM_ANALYSIS_PROMPT", "LLM_ANALYSIS_PROMPT")
LLM_ANALYSIS_FILENAME: str = os.getenv("LLM_ANALYSIS_FILENAME", "LLM_ANALYSIS_FILENAME")  

def ensure_upload_folder() -> None:
    """Ensure the upload folder exists.

    Creates the upload folder if it does not already exist.
    """
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logger.info(f"Created upload folder: {UPLOAD_FOLDER}")

def configure_dependencies() -> None:
    """Configure Tesseract and download NLTK resources.

    Ensures Tesseract and NLTK dependencies (punkt_tab and stopwords) are set up for text extraction and analysis.

    Raises:
        ImportError: If required libraries are not installed.
    """
    try:
        import pytesseract
        nltk.download("punkt_tab", quiet=True)
        nltk.download("stopwords", quiet=True)
        logger.debug("Tesseract and NLTK resources configured successfully")
    except ImportError as e:
        logger.error(f"Import error during dependency configuration: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error configuring dependencies: {str(e)}")
        raise

ensure_upload_folder()