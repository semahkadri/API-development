from typing import Optional
import os
from dotenv import load_dotenv
import nltk
import logging

logger = logging.getLogger(__name__)

load_dotenv()

UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER")
MAX_FILES: int = int(os.getenv("MAX_FILES"))
ALLOWED_PDF_COUNT: int = int(os.getenv("ALLOWED_PDF_COUNT"))
ALLOWED_DOCX_COUNT: int = int(os.getenv("ALLOWED_DOCX_COUNT"))
SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS: bool = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS").lower() == "true"
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
LLM_ANALYSIS_PROMPT: str = os.getenv("LLM_ANALYSIS_PROMPT")
LLM_ANALYSIS_FILENAME: str = os.getenv("LLM_ANALYSIS_FILENAME")
JOB_ID_FOR_SIMILARITY: str = os.getenv("JOB_ID_FOR_SIMILARITY")
CV_ID_FOR_SIMILARITY: str = os.getenv("CV_ID_FOR_SIMILARITY")
JOB_TEXT_FOR_TRANSLATION: str = os.getenv("JOB_TEXT_FOR_TRANSLATION") 

def ensure_upload_folder() -> None:
    """Ensure the upload folder exists.

    Creates the upload folder if it does not already exist.

    Raises:
        ValueError: If UPLOAD_FOLDER is not defined in the .env file.
    """
    if not UPLOAD_FOLDER:
        logger.error("UPLOAD_FOLDER environment variable is not defined")
        raise ValueError("UPLOAD_FOLDER must be defined in the .env file")
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logger.info(f"Created upload folder: {UPLOAD_FOLDER}")

def configure_dependencies() -> None:
    """Configure Tesseract and download NLTK resources.

    Ensures Tesseract and NLTK dependencies are set up for text extraction and analysis.

    Raises:
        ImportError: If required libraries are not installed.
        ValueError: If required environment variables are missing.
    """
    try:
        import pytesseract
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
        logger.debug("Tesseract and NLTK resources configured successfully")
    except ImportError as e:
        logger.error(f"Import error during dependency configuration: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error configuring dependencies: {str(e)}")
        raise

required_vars = {
    "UPLOAD_FOLDER": UPLOAD_FOLDER,
    "MAX_FILES": os.getenv("MAX_FILES"),
    "ALLOWED_PDF_COUNT": os.getenv("ALLOWED_PDF_COUNT"),
    "ALLOWED_DOCX_COUNT": os.getenv("ALLOWED_DOCX_COUNT"),
    "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI,
    "SQLALCHEMY_TRACK_MODIFICATIONS": os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS"),
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "LLM_ANALYSIS_PROMPT": LLM_ANALYSIS_PROMPT,
    "LLM_ANALYSIS_FILENAME": LLM_ANALYSIS_FILENAME,
    "JOB_ID_FOR_SIMILARITY": JOB_ID_FOR_SIMILARITY,
    "CV_ID_FOR_SIMILARITY": CV_ID_FOR_SIMILARITY,
    "JOB_TEXT_FOR_TRANSLATION": JOB_TEXT_FOR_TRANSLATION  
}

for var_name, var_value in required_vars.items():
    if var_value is None:
        logger.error(f"Required environment variable {var_name} is not defined in .env")
        raise ValueError(f"{var_name} must be defined in the .env file")

ensure_upload_folder()
configure_dependencies()