from typing import List, Dict
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import nltk
import logging
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_png_text(file_path: str) -> str:
    """Extract text from a PNG file using Tesseract OCR with preprocessing.

    Args:
        file_path: Path to the PNG file.

    Returns:
        str: Extracted text, empty string if extraction fails.
    """
    try:
        image = Image.open(file_path)
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(2.0)
        sharpened_image = enhanced_image.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(sharpened_image)
        logger.info(f"Extracted PNG text from {file_path}: {text[:50]}...")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PNG text from {file_path}: {str(e)}")
        return ""

def parse_cv_text(text: str) -> Dict[str, List[str]]:
    """Parse CV text to extract qualifications, skills, and experience.

    Args:
        text: Raw text extracted from the CV.

    Returns:
        Dict[str, List[str]]: Dictionary with qualifications, skills, and experience as lists.
    """
    try:
        tokens: List[str] = nltk.word_tokenize(text.lower())
        logger.debug(f"Tokenized CV text: {tokens[:50]}... (total: {len(tokens)})")

        qualifications = [token for token in tokens if token in config.QUALIFICATIONS_KEYWORDS]
        skills = [token for token in tokens if token in config.SKILLS_KEYWORDS]
        experience = [token for token in tokens if token in config.EXPERIENCE_KEYWORDS]

        result = {
            "qualifications": list(set(qualifications)),
            "skills": list(set(skills)),
            "experience": list(set(experience))
        }
        logger.info(f"Parsed CV: {result}")
        return result
    except Exception as e:
        logger.error(f"Error parsing CV text: {str(e)}")
        return {"qualifications": [], "skills": [], "experience": []}