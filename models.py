from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    skills = db.Column(db.String(500))
    
    # Aptitude test data
    aptitude_score = db.Column(db.Integer)
    aptitude_completed = db.Column(db.Boolean, default=False)
    
    # Coding test data
    coding_score = db.Column(db.Integer)
    coding_completed = db.Column(db.Boolean, default=False)
    
    # Behavioral test data
    behavioral_score = db.Column(db.Integer)
    behavioral_completed = db.Column(db.Boolean, default=False)
    behavioral_analysis = db.Column(db.Text)  # Store AI analysis results
    
    # Security tracking
    tab_switches = db.Column(db.Integer, default=0)
    
    # Additional data
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
