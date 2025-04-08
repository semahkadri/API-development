from typing import Optional
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_file(file: 'werkzeug.datastructures.FileStorage', upload_path: str) -> Optional[str]:
    """Save an uploaded file to disk.

    Args:
        file: File object from Flask request.
        upload_path: Path where the file will be saved.

    Returns:
        Optional[str]: Path where the file was saved, or None if saving fails.
    """
    try:
        file.save(upload_path)
        logger.info(f"Saved file to {upload_path}")
        return upload_path
    except Exception as e:
        logger.warning(f"Failed to save file {file.filename}: {str(e)}")
        return None

def clean_file(file_path: str) -> None:
    """Remove a file from disk after processing.

    Args:
        file_path: Path to the file to be removed.
    """
    try:
        time.sleep(1)  
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed file {file_path}")
    except PermissionError as e:
        logger.warning(f"Could not remove {file_path} due to permission error: {str(e)}")
    except Exception as e:
        logger.error(f"Error cleaning file {file_path}: {str(e)}")