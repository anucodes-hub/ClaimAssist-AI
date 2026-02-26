from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    db = get_db()
    try:
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            return jsonify({'error': 'Email already registered'}), 409
        
        hashed_pw = generate_password_hash(password)
        db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                   (name, email, hashed_pw))
        db.commit()
        
        user = db.execute('SELECT id, name, email FROM users WHERE email = ?', (email,)).fetchone()
        token = create_access_token(identity=str(user['id']))
        
        return jsonify({
            'message': 'Account created successfully',
            'token': token,
            'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}
        }), 201
    finally:
        db.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    db = get_db()
    try:
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = create_access_token(identity=str(user['id']))
        return jsonify({
            'token': token,
            'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}
        })
    finally:
        db.close()

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        user = db.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': dict(user)})
    finally:
        db.close()




        '''
        
        from flask import Blueprint, request, jsonify
from utils import analyze_document
import os

claim_bp = Blueprint("claims", __name__)

@claim_bp.route("/api/upload", methods=["POST"])
def upload_claim():
    file = request.files["file"]

    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", file.filename)
    file.save(path)

    analysis = analyze_document(path)
    score = int(analysis["confidence"] * 100)

    action = "MANUAL_REVIEW"
    if score > 90:
        action = "AUTO_APPROVED"
    elif score > 70:
        action = "USER_CONFIRMATION_REQUIRED"

    return jsonify({
        "health_score": score,
        "action": action,
        "flags": ["Blurry Image"] if analysis["is_blurry"] else [],
        "extracted": analysis["extracted_data"]
    })
        '''