from typing import Optional
from deep_translator import GoogleTranslator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_to_english(text: str, source_lang: str = "auto") -> Optional[str]:
    """Translate the given text to English using Google Translate.

    Args:
        text: The text to translate.
        source_lang: The source language code (default 'auto' for auto-detection).

    Returns:
        Optional[str]: Translated text in English, or None if translation fails.
    """
    try:
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for translation")
            return None

        translator = GoogleTranslator(source=source_lang, target="en")
        translated_text = translator.translate(text)
        logger.debug(f"Translated text from '{source_lang}' to English: {translated_text[:200]}...")
        return translated_text
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        return None