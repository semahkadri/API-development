# API Development

API Development project for extracting text from job descriptions (PDF/DOCX) and CVs (PNG) using Flask.

## Features

- `/upload-jobs`: Extract text from up to 20 PDF and 20 DOCX job description files.
- `/upload-cv`: Extract qualifications, skills, and experience from a juriste's CV in PNG format.
- `/view-data`: Retrieve all stored job descriptions and CVs from the database.


## Prerequisites

- Python 3.10
- Tesseract OCR (ensure it's in your system PATH)
- PostgreSQL (configured and running locally or remotely)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/semahkadri/API-development.git
   cd API-development
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

1. Navigate to the project folder:
   ```bash
   cd project
   ```

2. Run the Flask app:
   ```bash
   python app.py
   ```

3. Access the endpoints:
   - Jobs Form: `http://127.0.0.1:5000/upload-jobs-form`
   - CV Form: `http://127.0.0.1:5000/upload-cv-form`
   - View Data: `GET http://127.0.0.1:5000/view-data`

## Usage

- **Upload Jobs**: Use the form at `/upload-jobs-form` to upload up to 20 PDF and 20 DOCX job description files. Returns a JSON response with extracted text.
- **Upload CV**: Use the form at `/upload-cv-form` to upload a PNG CV. Returns a JSON response with extracted qualifications, skills, and experience.
- **View Data**: Send a GET request to /view-data to retrieve all stored jobs and CVs as JSON.

## Project Structure

- `project/app.py`: Main Flask application entry point.
- `project/config.py`: Configuration settings and dependencies setup.
- `project/routes.py`: API route definitions.
- `project/utils/`: Utility modules for file handling and text extraction.
  - `file_handler.py`: File saving and cleanup logic.
  - `pdf_extractor.py`: PDF text extraction.
  - `docx_extractor.py`: DOCX text extraction.
  - `cv_processor.py`: PNG OCR and CV parsing.
- `project/static/`: HTML forms for job and CV uploads.
- `notebooks/`: Jupyter notebooks for experiments (`PDF_DOCX_Extraction.ipynb`, `CV_Extraction.ipynb`, `PDF_DOCX_Extraction`).

## Requirements
See `requirements.txt`. Key dependencies include:

- `Flask` and `Flask-SQLAlchemy` for the web framework and ORM.
- `psycopg2-binary` for PostgreSQL connectivity.
- `pytesseract`, `pdfplumber`, `python-docx`, `nltk`, and `Pillow` for text extraction and processing.
- `python-dotenv` for loading environment variables from `.env`.

## Notes

- The `uploads/` folder is used temporarily during runtime and is excluded from the repository via `.gitignore`.
- Ensure test files (PDF, DOCX, PNG) contain readable text for accurate extraction.
- Sensitive data (e.g., database URI) is now stored in a `.env` file, making the codebase safe.
