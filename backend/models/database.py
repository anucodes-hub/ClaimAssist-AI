from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.Integer, primary_key=True)
    claim_uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    insurance_type = db.Column(db.String(20))
    status = db.Column(db.String(20), default='draft') # draft, pending, approved, rejected
    health_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Autonomous Tracking: One Claim -> Multiple Documents
    documents = db.relationship('Document', backref='claim', lazy=True, cascade="all, delete-orphan")

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
    filename = db.Column(db.String(100))
    doc_type = db.Column(db.String(50)) # e.g., 'Hospital Bill'
    is_verified = db.Column(db.Boolean, default=False)
    yolo_data = db.Column(db.Text) # Store JSON string of detections (seals/signatures)