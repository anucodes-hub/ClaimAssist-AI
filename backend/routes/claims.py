from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import get_db
from ai_service import analyze_document
import os
import json
import uuid
import random
from datetime import datetime

claims_bp = Blueprint('claims', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_claim_number():
    return f"CLM{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

@claims_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_claim():
    user_id = get_jwt_identity()
    insurance_type = request.form.get('insurance_type', 'health')
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, PDF'}), 400
    
    # Save file
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    
    # Run AI pipeline
    try:
        ai_results = analyze_document(file_path, insurance_type)
    except Exception as e:
        ai_results = {
            "blur_analysis": {"quality": "acceptable"},
            "extracted_data": {},
            "ai_reasons": [],
            "rejection_probability": 0.3,
            "health_score": 70,
            "claim_amount": 0,
            "hitl": {"action": "needs_confirmation", "status": "pending", "message": "AI analysis error, manual review recommended", "requires_human": True}
        }
    
    # Save to DB
    db = get_db()
    try:
        claim_number = generate_claim_number()
        status = ai_results["hitl"]["status"]
        date_approved = datetime.now().isoformat() if status == "approved" else None
        
        db.execute('''
            INSERT INTO claims 
            (user_id, claim_number, insurance_type, status, claim_amount, health_score,
             rejection_probability, ai_reasons, file_path, extracted_data, hitl_action, date_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, claim_number, insurance_type, status,
            ai_results["claim_amount"], ai_results["health_score"],
            ai_results["rejection_probability"],
            json.dumps(ai_results["ai_reasons"]),
            unique_filename,
            json.dumps(ai_results["extracted_data"]),
            ai_results["hitl"]["action"],
            date_approved
        ))
        db.commit()
        
        claim = db.execute('SELECT * FROM claims WHERE claim_number = ?', (claim_number,)).fetchone()
        
        return jsonify({
            "success": True,
            "claim_number": claim_number,
            "status": status,
            "health_score": ai_results["health_score"],
            "rejection_probability": ai_results["rejection_probability"],
            "claim_amount": ai_results["claim_amount"],
            "ai_reasons": ai_results["ai_reasons"],
            "extracted_data": ai_results["extracted_data"],
            "hitl": ai_results["hitl"],
            "blur_analysis": ai_results["blur_analysis"],
        })
    finally:
        db.close()

@claims_bp.route('/digilocker-simulate', methods=['POST'])
@jwt_required()
def digilocker_simulate():
    """Simulated DigiLocker document fetch"""
    user_id = get_jwt_identity()
    data = request.get_json()
    insurance_type = data.get('insurance_type', 'health')
    
    # Simulate DigiLocker response
    simulated_docs = {
        "health": {
            "source": "DigiLocker → PMJAY Health Records",
            "documents": [
                {"name": "Discharge Summary", "type": "discharge_summary", "verified": True},
                {"name": "Aadhaar Card", "type": "id_proof", "verified": True},
                {"name": "Health Card", "type": "health_card", "verified": True},
            ]
        },
        "vehicle": {
            "source": "DigiLocker → MoRTH Records",
            "documents": [
                {"name": "Vehicle RC", "type": "rc_book", "verified": True},
                {"name": "Driving License", "type": "driving_license", "verified": True},
                {"name": "PUC Certificate", "type": "puc", "verified": True},
            ]
        }
    }
    
    doc_data = simulated_docs.get(insurance_type, simulated_docs["health"])
    
    return jsonify({
        "success": True,
        "source": doc_data["source"],
        "documents": doc_data["documents"],
        "message": "Documents successfully fetched from DigiLocker",
        "aadhaar_verified": True,
        "timestamp": datetime.now().isoformat()
    })

@claims_bp.route('/confirm/<claim_number>', methods=['POST'])
@jwt_required()
def confirm_claim(claim_number):
    user_id = get_jwt_identity()
    data = request.get_json()
    action = data.get('action', 'approve')
    
    db = get_db()
    try:
        claim = db.execute('SELECT * FROM claims WHERE claim_number = ? AND user_id = ?',
                          (claim_number, user_id)).fetchone()
        if not claim:
            return jsonify({'error': 'Claim not found'}), 404
        
        if action == 'approve':
            status = 'approved'
            date_approved = datetime.now().isoformat()
        else:
            status = 'rejected'
            date_approved = None
        
        db.execute('UPDATE claims SET status = ?, date_approved = ? WHERE claim_number = ?',
                  (status, date_approved, claim_number))
        db.commit()
        
        return jsonify({'success': True, 'status': status, 'claim_number': claim_number})
    finally:
        db.close()

@claims_bp.route('/all', methods=['GET'])
@jwt_required()
def get_claims():
    user_id = get_jwt_identity()
    db = get_db()
    try:
        claims = db.execute(
            'SELECT * FROM claims WHERE user_id = ? ORDER BY date_requested DESC',
            (user_id,)
        ).fetchall()
        
        result = []
        for c in claims:
            claim_dict = dict(c)
            claim_dict['ai_reasons'] = json.loads(claim_dict.get('ai_reasons', '[]'))
            claim_dict['extracted_data'] = json.loads(claim_dict.get('extracted_data', '{}'))
            result.append(claim_dict)
        
        # Stats
        total = len(result)
        approved = sum(1 for c in result if c['status'] == 'approved')
        pending = sum(1 for c in result if c['status'] in ['pending', 'under_review'])
        rejected = sum(1 for c in result if c['status'] == 'rejected')
        total_amount = sum(c.get('claim_amount', 0) for c in result)
        
        return jsonify({
            "claims": result,
            "stats": {
                "total": total,
                "approved": approved,
                "pending": pending,
                "rejected": rejected,
                "total_amount": round(total_amount, 2)
            }
        })
    finally:
        db.close()