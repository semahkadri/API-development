from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class JobDescription(db.Model):
    """Database model for job descriptions."""
    __tablename__ = "job_descriptions"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)

class CV(db.Model):
    """Database model for CVs."""
    __tablename__ = "cvs"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)
    qualifications = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)