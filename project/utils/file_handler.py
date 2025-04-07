from typing import Optional
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_file(file, upload_path: str) -> Optional[str]:
    """Save an uploaded file to disk."""
    try:
        file.save(upload_path)
        logger.info(f"Saved file to {upload_path}")
        return upload_path
    except Exception as e:
        logger.warning(f"Failed to save file {file.filename}: {str(e)}")
        return None

def clean_file(file_path: str) -> None:
    """Remove a file from disk after processing."""
    time.sleep(1)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed file {file_path}")
    except PermissionError as e:
        logger.warning(f"Could not remove {file_path}: {str(e)}")