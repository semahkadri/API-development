from typing import List
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import nltk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_png_text(file_path: str) -> str:
    """Extract text from a PNG file using Tesseract OCR with preprocessing."""
    try:
        image = Image.open(file_path)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(image)
        logger.info(f"Extracted PNG text from {file_path}: {text[:50]}...")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PNG text from {file_path}: {str(e)}")
        return ""

def parse_cv_text(text: str) -> dict:
    """Parse CV text to extract qualifications, skills, and experience."""
    tokens: List[str] = nltk.word_tokenize(text.lower())
    logger.info(f"Tokens: {tokens}")

    qualifications_keywords: List[str] = [
        "law", "legal", "jurisprudence", "degree", "master", "bachelor", "llb", "jd"
    ]
    skills_keywords: List[str] = [
        "negotiation", "contract", "research", "analysis", "drafting", "litigation", "compliance"
    ]
    experience_keywords: List[str] = [
        "years", "experience", "worked", "firm", "firms", "practice"
    ]

    qualifications = [token for token in tokens if token in qualifications_keywords]
    skills = [token for token in tokens if token in skills_keywords]
    experience = [token for token in tokens if token in experience_keywords]

    return {
        "qualifications": list(set(qualifications)),
        "skills": list(set(skills)),
        "experience": list(set(experience))
    }