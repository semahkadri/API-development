from flask_sqlalchemy import SQLAlchemy
from typing import Optional, List, Dict, Union
import logging
from .models import db, JobDescription, CV

logger = logging.getLogger(__name__)

def init_db(app) -> None:
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        try:
            db.session.execute("SELECT 1")
            logger.info("Database connection successful")
            db.create_all()
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

def store_job_description(filename: str, text: str) -> Optional[int]:
    """Store a job description in the database."""
    try:
        job = JobDescription(filename=filename, text=text)
        db.session.add(job)
        db.session.commit()
        logger.debug(f"Stored job description: {filename} with ID {job.id}")
        return job.id
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error storing job description {filename}: {str(e)}")
        return None

def store_cv(filename: str, text: str, qualifications: List[str], skills: List[str], experience: List[str]) -> Optional[int]:
    """Store a CV in the database."""
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
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error storing CV {filename}: {str(e)}")
        return None

def get_all_jobs() -> List[Dict[str, Union[int, str]]]:
    """Retrieve all job descriptions from the database."""
    try:
        jobs = JobDescription.query.all()
        result = [{"id": job.id, "filename": job.filename, "text": job.text} for job in jobs]
        logger.debug(f"Retrieved {len(result)} jobs from database")
        return result
    except Exception as e:
        logger.error(f"Error retrieving jobs: {str(e)}")
        return []

def get_all_cvs() -> List[Dict[str, Union[int, str, List[str]]]]:
    """Retrieve all CVs from the database."""
    try:
        cvs = CV.query.all()
        result = [{
            "id": cv.id,
            "filename": cv.filename,
            "text": cv.text,
            "qualifications": cv.qualifications.split(","),
            "skills": cv.skills.split(","),
            "experience": cv.experience.split(",")
        } for cv in cvs]
        logger.debug(f"Retrieved {len(result)} CVs from database")
        return result
    except Exception as e:
        logger.error(f"Error retrieving CVs: {str(e)}")
        return []