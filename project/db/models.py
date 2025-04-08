from flask_sqlalchemy import SQLAlchemy
import config

db = SQLAlchemy()

class JobDescription(db.Model):
    """Database model representing job descriptions.

    Attributes:
        id: Unique identifier for the job description.
        filename: Name of the file from which the job description was extracted.
        text: Full text content of the job description.
    """
    __tablename__ = config.JOB_DESCRIPTIONS_TABLE
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)

class CV(db.Model):
    """Database model representing CVs.

    Attributes:
        id: Unique identifier for the CV.
        filename: Name of the file from which the CV was extracted.
        text: Full text content of the CV.
        qualifications: Comma-separated list of qualifications.
        skills: Comma-separated list of skills.
        experience: Comma-separated list of experience indicators.
    """
    __tablename__ = config.CVS_TABLE
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)
    qualifications = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)