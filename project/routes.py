from typing import Dict, Union, List, Optional, Tuple
from flask import Blueprint, jsonify, current_app, request, send_file
import os
import uuid
import config
from utils.file_handler import save_file, clean_file
from utils.pdf_extractor import extract_pdf_text
from utils.docx_extractor import extract_docx_text
from utils.cv_processor import extract_png_text, parse_cv_text
from utils.data_analyzer import analyze_text, generate_word_frequency_plot
from utils.llm_analyzer import analyze_with_llm
from utils.similarity_calculator import calculate_similarities
from utils.translator import translate_to_english
from db.database import store_job_description, store_cv, get_all_jobs, get_all_cvs
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

@api_bp.route("/upload-jobs", methods=["POST"])
def upload_jobs() -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """Extract text from job description files (PDF/DOCX) and store them in the database.

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

    max_files = config.MAX_FILES
    if len(files) > max_files:
        logger.error(f"Too many files uploaded. Maximum allowed: {max_files}")
        return jsonify({"error": f"Too many files. Max {max_files} files allowed."}), 400

    extracted_texts = []
    pdf_count = 0
    docx_count = 0
    allowed_pdf_count = config.ALLOWED_PDF_COUNT
    allowed_docx_count = config.ALLOWED_DOCX_COUNT

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

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)

        saved_path = save_file(file, file_path)
        if not saved_path:
            logger.warning(f"Failed to save file: {file.filename}")
            continue

        try:
            text = extract_pdf_text(saved_path) if file.filename.endswith(".pdf") else extract_docx_text(saved_path)
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

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)

    saved_path = save_file(file, file_path)
    if not saved_path:
        logger.error(f"Failed to save CV file: {file.filename}")
        return jsonify({"error": f"Failed to process {file.filename}"}), 500

    try:
        text = extract_png_text(saved_path)
        if not text:
            logger.error(f"No text extracted from CV: {file.filename}")
            clean_file(saved_path)
            return jsonify({"error": "No text extracted from CV"}), 400

        parsed_data = parse_cv_text(text)
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

    Returns:
        Dict[str, Union[str, List[int], int]]: JSON response with stored IDs or error message.
    """
    logger.debug("Received store-data request")
    data = request.get_json()
    if not data or "job_texts" not in data or "cv_data" not in data:
        logger.error("Missing job_texts or cv_data in request")
        return jsonify({"error": "Missing job_texts or cv_data"}), 400

    job_texts = data["job_texts"]
    cv_data = data["cv_data"]
    logger.debug(f"Processing job_texts: {job_texts}")
    logger.debug(f"Processing cv_data: {cv_data}")

    try:
        job_ids = []
        for job in job_texts:
            job_id = store_job_description(job["filename"], job["text"])
            if job_id:
                job_ids.append(job_id)
            else:
                logger.error(f"Failed to store job: {job['filename']}")

        cv_id = store_cv(
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

    Returns:
        Dict[str, Union[List[Dict[str, Union[int, str]]], List[Dict[str, Union[int, str, List[str]]]]]]: JSON response with jobs and CVs data or error message.
    """
    try:
        jobs = get_all_jobs()
        cvs = get_all_cvs()
        logger.info(f"Retrieved {len(jobs)} jobs and {len(cvs)} CVs from database")
        return jsonify({"jobs": jobs, "cvs": cvs})
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return jsonify({"error": f"Error retrieving data: {str(e)}"}), 500

@api_bp.route("/analyze-jobs", methods=["GET"])
def analyze_jobs() -> Dict[str, Union[str, List[Tuple[str, int]], str, Dict[str, float]]]:
    """Analyze job descriptions and generate a word frequency visualization.

    Returns:
        Dict[str, Union[str, List[Tuple[str, int]], str, Dict[str, float]]]: JSON response with analysis results or error message.
    """
    try:
        jobs = get_all_jobs()
        if not jobs:
            logger.warning("No job descriptions found in the database")
            return jsonify({"error": "No job descriptions available for analysis"}), 404

        job_texts = [job["text"] for job in jobs]
        analysis_result = analyze_text(job_texts)
        top_words = analysis_result["top_words"]
        stats = analysis_result["stats"]
        plot_path = generate_word_frequency_plot(top_words)

        logger.info("Job description analysis completed successfully")
        return jsonify({
            "message": "Analysis completed",
            "top_words": top_words,
            "statistics": stats,
            "visualization_path": plot_path
        })
    except Exception as e:
        logger.error(f"Error analyzing job descriptions: {str(e)}")
        return jsonify({"error": f"Error analyzing job descriptions: {str(e)}"}), 500

@api_bp.route("/analyze-llm", methods=["GET"])
def analyze_llm() -> Dict[str, Union[str, Dict[str, List[str]]]]:
    """Analyze a specific CV using a pre-trained LLM.

    Returns:
        Dict[str, Union[str, Dict[str, List[str]]]]: JSON response with extracted data or error message.
    """
    try:
        filename = config.LLM_ANALYSIS_FILENAME
        if not filename or filename == "LLM_ANALYSIS_FILENAME":
            logger.error("No valid filename defined in LLM_ANALYSIS_FILENAME in .env")
            return jsonify({"error": "No valid filename defined in LLM_ANALYSIS_FILENAME in .env"}), 400

        cvs = get_all_cvs()
        target_cv = next((cv for cv in cvs if cv["filename"] == filename), None)
        if not target_cv:
            logger.warning(f"No CV found with filename: {filename}")
            return jsonify({"error": f"No CV found with filename: {filename}"}), 404

        cv_text = [target_cv["text"]]
        extracted_data = analyze_with_llm(cv_text)

        logger.info(f"LLM analysis completed successfully for CV: {filename}")
        return jsonify({
            "message": "LLM analysis completed",
            "filename": filename,
            "extracted_data": extracted_data
        })
    except Exception as e:
        logger.error(f"Error during LLM analysis: {str(e)}")
        return jsonify({"error": f"Error during LLM analysis: {str(e)}"}), 500

@api_bp.route("/calculate-similarities", methods=["GET"])
def calculate_similarities_endpoint() -> Dict[str, Union[str, Dict[str, float]]]:
    """Calculate Cosine Similarity, Levenshtein Distance, and Jaccard Index between a job description and CV.

    Returns:
        Dict[str, Union[str, Dict[str, float]]]: JSON response with similarity metrics or error message.
    """
    try:
        job_id = request.args.get('job_id', config.JOB_ID_FOR_SIMILARITY)
        cv_id = request.args.get('cv_id', config.CV_ID_FOR_SIMILARITY)

        if not job_id or not cv_id:
            logger.error("No job or CV ID provided in query or environment")
            return jsonify({"error": "Job ID and CV ID must be provided via query parameters (?job_id=X&cv_id=Y) or .env"}), 400

        jobs = get_all_jobs()
        cvs = get_all_cvs()

        if not jobs or not cvs:
            logger.error("No job descriptions or CVs found in the database")
            return jsonify({"error": "No job descriptions or CVs available for comparison"}), 404

        job = next((j for j in jobs if str(j["id"]) == str(job_id)), None)
        cv = next((c for c in cvs if str(c["id"]) == str(cv_id)), None)

        if not job or not cv:
            logger.error(f"No job or CV found with IDs: job_id={job_id}, cv_id={cv_id}")
            return jsonify({"error": f"No job or CV found with IDs: job_id={job_id}, cv_id={cv_id}"}), 404

        logger.debug(f"Raw job text: {job['text'][:200]}...")
        logger.debug(f"Raw CV text: {cv['text'][:200]}...")

        similarities = calculate_similarities(job["text"], cv["text"])

        logger.info(f"Similarity calculations completed for job_id={job_id} and cv_id={cv_id}")
        return jsonify({
            "message": "Similarity metrics calculated",
            "job_id": job_id,
            "cv_id": cv_id,
            "similarities": similarities
        })
    except Exception as e:
        logger.error(f"Error calculating similarities: {str(e)}")
        return jsonify({"error": f"Error calculating similarities: {str(e)}"}), 500

@api_bp.route("/translate-to-english", methods=["GET"])
def translate_to_english_endpoint() -> Dict[str, Union[str, Optional[str]]]:
    """Translate a job description to English, prioritizing text from .env or falling back to database by ID.

    Returns:
        Dict[str, Union[str, Optional[str]]]: JSON response with translated text or error message.
    """
    try:
        job_id = request.args.get("job_id")
        job_text = config.JOB_TEXT_FOR_TRANSLATION

        if not job_text and not job_id:
            logger.error("No job text provided in JOB_TEXT_FOR_TRANSLATION (.env) or job_id (query parameter)")
            return jsonify({"error": "Job text must be provided via JOB_TEXT_FOR_TRANSLATION in .env or job_id via query (?job_id=X)"}), 400

        if not job_text:
            jobs = get_all_jobs()
            if not jobs:
                logger.error("No job descriptions found in the database")
                return jsonify({"error": "No job descriptions available for translation"}), 404

            job = next((j for j in jobs if str(j["id"]) == str(job_id)), None)
            if not job:
                logger.error(f"No job found with ID: {job_id}")
                return jsonify({"error": f"No job found with ID: {job_id}"}), 404

            job_text = job["text"]
            logger.debug(f"Using job text from database for job_id={job_id}: {job_text[:200]}...")
        else:
            logger.debug(f"Using job text from .env: {job_text[:200]}...")

        translated_text = translate_to_english(job_text)

        if translated_text is None:
            logger.warning("Translation failed")
            return jsonify({"error": "Failed to translate job description"}), 500

        response = {
            "message": "Translation completed",
            "translated_text": translated_text
        }
        if job_id:
            response["job_id"] = job_id

        logger.info("Translation completed successfully")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error translating job description: {str(e)}")
        return jsonify({"error": f"Error translating job description: {str(e)}"}), 500

@api_bp.route("/view-analysis", methods=["GET"])
def view_analysis() -> str:
    """Serve the word frequency visualization HTML file.

    Returns:
        str: HTML content or JSON error message.
    """
    try:
        plot_path = os.path.join(config.UPLOAD_FOLDER, "word_frequency.html")
        if not os.path.exists(plot_path):
            logger.error("Word frequency visualization file not found")
            return jsonify({"error": "Visualization file not found. Run /analyze-jobs first."}), 400
        
        logger.info("Serving word frequency visualization")
        return send_file(plot_path)
    except Exception as e:
        logger.error(f"Error serving visualization: {str(e)}")
        return jsonify({"error": f"Error serving visualization: {str(e)}"}), 500

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