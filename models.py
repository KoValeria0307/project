from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    salary = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  
    created_at = db.Column(db.DateTime, default=db.func.now())