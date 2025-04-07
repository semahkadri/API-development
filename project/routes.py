from typing import Dict, Union, List
from flask import Blueprint, request, jsonify
import os
import uuid
import config
from utils.file_handler import save_file, clean_file
from utils.pdf_extractor import extract_pdf_text
from utils.docx_extractor import extract_docx_text
from utils.cv_processor import extract_png_text, parse_cv_text

api_bp = Blueprint("api", __name__)

@api_bp.route("/upload-jobs", methods=["POST"])
def upload_jobs() -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """Extract text from up to 20 PDF and 20 DOCX files containing job descriptions."""
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No valid files provided"}), 400
    if len(files) > config.MAX_FILES:
        return jsonify({"error": f"Too many files. Max {config.MAX_FILES} files allowed."}), 400

    extracted_texts: List[Dict[str, str]] = []
    pdf_count: int = 0
    docx_count: int = 0

    for file in files:
        if not file.filename:
            continue

        if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
            return jsonify({"error": f"Unsupported file type: {file.filename}. Use PDF or DOCX."}), 400

        if file.filename.endswith(".pdf") and pdf_count >= config.ALLOWED_PDF_COUNT:
            return jsonify({"error": "Exceeded limit of 20 PDF files"}), 400
        if file.filename.endswith(".docx") and docx_count >= config.ALLOWED_DOCX_COUNT:
            return jsonify({"error": "Exceeded limit of 20 DOCX files"}), 400

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)

        saved_path = save_file(file, file_path)
        if not saved_path:
            continue

        try:
            if file.filename.endswith(".pdf"):
                text = extract_pdf_text(saved_path)
                pdf_count += 1
            else:
                text = extract_docx_text(saved_path)
                docx_count += 1

            extracted_texts.append({"filename": file.filename, "text": text})

        except Exception as e:
            clean_file(saved_path)
            return jsonify({"error": f"Error processing {file.filename}: {str(e)}"}), 500

        clean_file(saved_path)

    return jsonify({"extracted_texts": extracted_texts})


@api_bp.route("/upload-cv", methods=["POST"])
def upload_cv() -> Dict[str, Union[str, List[str]]]:
    """Extract qualifications, skills, and experience from a juriste's CV in PNG format."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No filename provided"}), 400

    if not file.filename.endswith(".png"):
        return jsonify({"error": "Unsupported file type. Please upload a PNG file."}), 400

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)

    saved_path = save_file(file, file_path)
    if not saved_path:
        return jsonify({"error": f"Failed to process {file.filename}"}), 500

    try:
        text = extract_png_text(saved_path)
        if not text:
            clean_file(saved_path)
            return jsonify({"error": "No text extracted from CV"}), 400

        parsed_data = parse_cv_text(text)
        clean_file(saved_path)
        return jsonify({
            "filename": file.filename,
            "qualifications": parsed_data["qualifications"],
            "skills": parsed_data["skills"],
            "experience": parsed_data["experience"]
        })

    except Exception as e:
        clean_file(saved_path)
        return jsonify({"error": f"Error processing CV: {str(e)}"}), 500


@api_bp.route("/upload-jobs-form", methods=["GET"])
def serve_upload_jobs_form() -> str:
    """Serve the upload form for job description files."""
    from flask import current_app
    return current_app.send_static_file("upload_jobs.html")


@api_bp.route("/upload-cv-form", methods=["GET"])
def serve_upload_cv_form() -> str:
    """Serve the upload form for CV files."""
    from flask import current_app
    return current_app.send_static_file("upload_cv.html")