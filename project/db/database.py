from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from typing import Optional, List, Dict, Union
import logging
from sqlalchemy.exc import SQLAlchemyError
from .models import db, JobDescription, CV

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database(app: Flask) -> None:
    """Initialize the database with the Flask application.

    Args:
        app: Flask application instance.

    Raises:
        SQLAlchemyError: If database connection or table creation fails.
    """
    db.init_app(app)
    with app.app_context():
        try:
            db.session.execute("SELECT 1")
            logger.info("Database connection established successfully")
            db.create_all()
            logger.info("Database tables initialized")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

def store_job_description(filename: str, text: str) -> Optional[int]:
    """Store a job description in the database.

    Args:
        filename: Name of the file containing the job description.
        text: Text content of the job description.

    Returns:
        Optional[int]: ID of the stored job description, or None if storage fails.
    """
    try:
        job = JobDescription(filename=filename, text=text)
        db.session.add(job)
        db.session.commit()
        logger.debug(f"Stored job description: {filename} with ID {job.id}")
        return job.id
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error storing job description {filename}: {str(e)}")
        return None

def store_cv(filename: str, text: str, qualifications: List[str], skills: List[str], experience: List[str]) -> Optional[int]:
    """Store a CV in the database.

    Args:
        filename: Name of the file containing the CV.
        text: Full text content of the CV.
        qualifications: List of qualifications extracted from the CV.
        skills: List of skills extracted from the CV.
        experience: List of experience indicators extracted from the CV.

    Returns:
        Optional[int]: ID of the stored CV, or None if storage fails.
    """
    try:
        cv = CV(
            filename=filename,
            text=text,
            qualifications=",".join(qualifications),
            skills=",".join(skills),
            experience=",".join(experience)
        )
        db.session.add(cv)
        db.session.commit()
        logger.debug(f"Stored CV: {filename} with ID {cv.id}")
        return cv.id
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error storing CV {filename}: {str(e)}")
        return None

def get_all_jobs() -> List[Dict[str, Union[int, str]]]:
    """Retrieve all job descriptions from the database.

    Returns:
        List[Dict[str, Union[int, str]]]: List of dictionaries containing job description details.
    """
    try:
        jobs = JobDescription.query.all()
        result = [{"id": job.id, "filename": job.filename, "text": job.text} for job in jobs]
        logger.debug(f"Retrieved {len(result)} job descriptions from database")
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving job descriptions: {str(e)}")
        return []

def get_all_cvs() -> List[Dict[str, Union[int, str, List[str]]]]:
    """Retrieve all CVs from the database.

    Returns:
        List[Dict[str, Union[int, str, List[str]]]]: List of dictionaries containing CV details.
    """
    try:
        cvs = CV.query.all()
        result = [
            {
                "id": cv.id,
                "filename": cv.filename,
                "text": cv.text,
                "qualifications": cv.qualifications.split(",") if cv.qualifications else [],
                "skills": cv.skills.split(",") if cv.skills else [],
                "experience": cv.experience.split(",") if cv.experience else []
            }
            for cv in cvs
        ]
        logger.debug(f"Retrieved {len(result)} CVs from database")
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving CVs: {str(e)}")
        return []