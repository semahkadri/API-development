from typing import Dict, Union, List, Optional
from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import config
from utils.file_handler import save_file, clean_file
from utils.pdf_extractor import extract_pdf_text
from utils.docx_extractor import extract_docx_text
from utils.cv_processor import extract_png_text, parse_cv_text
from db.database import store_job_description, store_cv, get_all_jobs, get_all_cvs
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Define Blueprint for API routes
api_bp = Blueprint("api", __name__)

@api_bp.route("/upload-jobs", methods=["POST"])
def upload_jobs() -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """Extract text from job description files (PDF/DOCX) and store them in the database.

    This endpoint accepts up to a configured maximum number of PDF and DOCX files,
    extracts their text, and stores it in the database.

    Returns:
        Dict[str, Union[str, List[Dict[str, str]]]]: JSON response with extracted texts or error message.
    """
    if "files" not in request.files:
        logger.error("No files provided in request")
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    if not files:
        logger.error("No valid files provided")
        return jsonify({"error": "No valid files provided"}), 400

    max_files: int = config.MAX_FILES
    if len(files) > max_files:
        logger.error(f"Too many files uploaded. Maximum allowed: {max_files}")
        return jsonify({"error": f"Too many files. Max {max_files} files allowed."}), 400

    extracted_texts: List[Dict[str, str]] = []
    pdf_count: int = 0
    docx_count: int = 0
    allowed_pdf_count: int = config.ALLOWED_PDF_COUNT
    allowed_docx_count: int = config.ALLOWED_DOCX_COUNT

    for file in files:
        if not file.filename:
            logger.warning("Skipping file with no filename")
            continue

        if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
            logger.error(f"Unsupported file type: {file.filename}")
            return jsonify({"error": f"Unsupported file type: {file.filename}. Use PDF or DOCX."}), 400

        if file.filename.endswith(".pdf") and pdf_count >= allowed_pdf_count:
            logger.error(f"Exceeded limit of {allowed_pdf_count} PDF files")
            return jsonify({"error": f"Exceeded limit of {allowed_pdf_count} PDF files"}), 400
        if file.filename.endswith(".docx") and docx_count >= allowed_docx_count:
            logger.error(f"Exceeded limit of {allowed_docx_count} DOCX files")
            return jsonify({"error": f"Exceeded limit of {allowed_docx_count} DOCX files"}), 400

        unique_filename: str = f"{uuid.uuid4()}_{file.filename}"
        file_path: str = os.path.join(config.UPLOAD_FOLDER, unique_filename)

        saved_path: Optional[str] = save_file(file, file_path)
        if not saved_path:
            logger.warning(f"Failed to save file: {file.filename}")
            continue

        try:
            text: str = extract_pdf_text(saved_path) if file.filename.endswith(".pdf") else extract_docx_text(saved_path)
            if file.filename.endswith(".pdf"):
                pdf_count += 1
            else:
                docx_count += 1

            extracted_texts.append({"filename": file.filename, "text": text})
            store_job_description(file.filename, text)
            logger.info(f"Successfully processed and stored job file: {file.filename}")
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            clean_file(saved_path)
            return jsonify({"error": f"Error processing {file.filename}: {str(e)}"}), 500
        finally:
            clean_file(saved_path)

    logger.info(f"Processed {len(extracted_texts)} job files successfully")
    return jsonify({"extracted_texts": extracted_texts})

@api_bp.route("/upload-cv", methods=["POST"])
def upload_cv() -> Dict[str, Union[str, List[str]]]:
    """Extract qualifications, skills, and experience from a juriste's CV (PNG) and store in the database.

    This endpoint processes a single PNG file, extracts text using OCR, parses it,
    and stores the data in the database.

    Returns:
        Dict[str, Union[str, List[str]]]: JSON response with extracted CV data or error message.
    """
    if "file" not in request.files:
        logger.error("No file provided in request")
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        logger.error("No filename provided in request")
        return jsonify({"error": "No filename provided"}), 400

    if not file.filename.endswith(".png"):
        logger.error(f"Unsupported file type: {file.filename}. Expected PNG")
        return jsonify({"error": "Unsupported file type. Please upload a PNG file."}), 400

    unique_filename: str = f"{uuid.uuid4()}_{file.filename}"
    file_path: str = os.path.join(config.UPLOAD_FOLDER, unique_filename)

    saved_path: Optional[str] = save_file(file, file_path)
    if not saved_path:
        logger.error(f"Failed to save CV file: {file.filename}")
        return jsonify({"error": f"Failed to process {file.filename}"}), 500

    try:
        text: str = extract_png_text(saved_path)
        if not text:
            logger.error(f"No text extracted from CV: {file.filename}")
            clean_file(saved_path)
            return jsonify({"error": "No text extracted from CV"}), 400

        parsed_data: Dict[str, List[str]] = parse_cv_text(text)
        store_cv(
            file.filename,
            text,
            parsed_data["qualifications"],
            parsed_data["skills"],
            parsed_data["experience"]
        )
        logger.info(f"Successfully processed and stored CV: {file.filename}")
        return jsonify({
            "filename": file.filename,
            "qualifications": parsed_data["qualifications"],
            "skills": parsed_data["skills"],
            "experience": parsed_data["experience"]
        })
    except Exception as e:
        logger.error(f"Error processing CV {file.filename}: {str(e)}")
        return jsonify({"error": f"Error processing CV: {str(e)}"}), 500
    finally:
        clean_file(saved_path)

@api_bp.route("/store-data", methods=["POST"])
def store_data() -> Dict[str, Union[str, List[int], int]]:
    """Store extracted job descriptions and CV data in the PostgreSQL database.

    This endpoint accepts JSON data containing job descriptions and CV details,
    stores them, and returns the IDs of the stored records.

    Returns:
        Dict[str, Union[str, List[int], int]]: JSON response with stored IDs or error message.
    """
    logger.debug("Received store-data request")
    data = request.get_json()
    if not data or "job_texts" not in data or "cv_data" not in data:
        logger.error("Missing job_texts or cv_data in request")
        return jsonify({"error": "Missing job_texts or cv_data"}), 400

    job_texts: List[Dict[str, str]] = data["job_texts"]
    cv_data: Dict[str, Union[str, List[str]]] = data["cv_data"]
    logger.debug(f"Processing job_texts: {job_texts}")
    logger.debug(f"Processing cv_data: {cv_data}")

    try:
        job_ids: List[int] = []
        for job in job_texts:
            job_id: Optional[int] = store_job_description(job["filename"], job["text"])
            if job_id:
                job_ids.append(job_id)
            else:
                logger.error(f"Failed to store job: {job['filename']}")

        cv_id: Optional[int] = store_cv(
            cv_data["filename"],
            cv_data.get("text", ""),
            cv_data["qualifications"],
            cv_data["skills"],
            cv_data["experience"]
        )

        if not job_ids or not cv_id:
            logger.error("Failed to store some data")
            return jsonify({"error": "Failed to store some data"}), 500

        logger.info(f"Stored data successfully: job_ids={job_ids}, cv_id={cv_id}")
        return jsonify({"message": "Data stored successfully", "job_ids": job_ids, "cv_id": cv_id})
    except Exception as e:
        logger.error(f"Error storing data: {str(e)}")
        return jsonify({"error": f"Error storing data: {str(e)}"}), 500

@api_bp.route("/view-data", methods=["GET"])
def view_data() -> Dict[str, Union[List[Dict[str, Union[int, str]]], List[Dict[str, Union[int, str, List[str]]]]]]:
    """Retrieve all stored job descriptions and CVs from the PostgreSQL database.

    This endpoint fetches all stored job descriptions and CVs and returns them as JSON.

    Returns:
        Dict[str, Union[List[Dict[str, Union[int, str]]], List[Dict[str, Union[int, str, List[str]]]]]]: JSON response with jobs and CVs data or error.
    """
    try:
        jobs: List[Dict[str, Union[int, str]]] = get_all_jobs()
        cvs: List[Dict[str, Union[int, str, List[str]]]] = get_all_cvs()
        logger.info(f"Retrieved {len(jobs)} jobs and {len(cvs)} CVs from database")
        return jsonify({"jobs": jobs, "cvs": cvs})
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return jsonify({"error": f"Error retrieving data: {str(e)}"}), 500

@api_bp.route("/upload-jobs-form", methods=["GET"])
def serve_upload_jobs_form() -> str:
    """Serve the HTML upload form for job description files.

    Returns:
        str: HTML content of the job upload form.
    """
    logger.info("Serving upload jobs form")
    return current_app.send_static_file("upload_jobs.html")

@api_bp.route("/upload-cv-form", methods=["GET"])
def serve_upload_cv_form() -> str:
    """Serve the HTML upload form for CV files.

    Returns:
        str: HTML content of the CV upload form.
    """
    logger.info("Serving upload CV form")
    return current_app.send_static_file("upload_cv.html")