from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
HEAD
from models.database import get_db
from ai_service import analyze_document
=======
from models.database import db, Claim, Document
from services.ai_service import analyze_document
origin/main
import os
import json
import uuid
import random
from datetime import datetime

# Initialize the blueprint
claims_bp = Blueprint('claims', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_claim_number():
    return f"CLM{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

# 1. Initiate Claim Session (Autonomous Tracking Start)
@claims_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_claim():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    new_claim = Claim(
        user_id=user_id,
        claim_number=generate_claim_number(),
        insurance_type=data.get('type', 'health'),
        status='draft' # Set to draft until all files are uploaded
    )
    db.session.add(new_claim)
    db.session.commit()
    
    return jsonify({
        "success": True, 
        "claim_uuid": new_claim.claim_uuid, 
        "claim_number": new_claim.claim_number
    })

# 2. Upload and Validate Individual Documents (N-file Support)
@claims_bp.route('/upload-doc', methods=['POST'])
@jwt_required()
def upload_doc():
    user_id = get_jwt_identity()
    claim_uuid = request.form.get('claim_uuid')
    doc_type = request.form.get('doc_type') # e.g., 'Hospital Bill'
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Use PNG, JPG, or PDF'}), 400

    # Find the current claim session
    claim = Claim.query.filter_by(claim_uuid=claim_uuid, user_id=user_id).first()
    if not claim:
        return jsonify({'error': 'Claim session not found'}), 404

    # Save physical file
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{claim_uuid}_{uuid.uuid4().hex[:5]}.{ext}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # 3. Run AI Pipeline (YOLO for Seals, Groq for OCR)
    try:
        ai_results = analyze_document(file_path, claim.insurance_type)
    except Exception as e:
        current_app.logger.error(f"AI Pipeline Error: {e}")
        return jsonify({'error': 'AI Processing failed'}), 500

    # 4. Save individual document to the database for tracking
    new_doc = Document(
        claim_id=claim.id,
        filename=filename,
        doc_type=doc_type,
        is_verified=not ai_results.get("blur_analysis", {}).get("is_blurry", False),
        yolo_data=json.dumps(ai_results.get("yolo_detections", {}))
    )
    db.session.add(new_doc)
    
    # Update claim-level data if AI returned scoring info
    if ai_results.get("health_score"):
        claim.health_score = ai_results["health_score"]
        claim.claim_amount = ai_results.get("claim_amount", 0)
        claim.ai_reasons = json.dumps(ai_results.get("ai_reasons", []))
        # Optional: update status if AI provides immediate guidance
        if ai_results.get("hitl", {}).get("status"):
             # We keep it as draft until final_submit is called, 
             # but we can store the suggested status
             pass

    db.session.commit()

    return jsonify({
        "success": True,
        "status": "verified",
        "doc_type": doc_type,
        "analysis": ai_results
    })

# 3. Final Submit (Triggers the switch from 'draft' to 'pending')
@claims_bp.route('/submit/<uuid>', methods=['POST'])
@jwt_required()
def final_submit(uuid):
    user_id = get_jwt_identity()
    claim = Claim.query.filter_by(claim_uuid=uuid, user_id=user_id).first()
    
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404

    # Verification: Ensure at least one document exists
    if not claim.documents:
        return jsonify({'error': 'Cannot submit a claim without documents'}), 400

    claim.status = 'pending'
    db.session.commit()

    return jsonify({
        "success": True, 
        "message": "Claim submitted successfully!", 
        "status": claim.status
    })

# 4. Dashboard Endpoint (Autonomous Tracker View)
@claims_bp.route('/all', methods=['GET'])
@jwt_required()
def get_claims():
    user_id = get_jwt_identity()
    claims = Claim.query.filter_by(user_id=user_id).order_by(Claim.created_at.desc()).all()
    
    result = []
    for c in claims:
        result.append({
            "id": c.id,
            "claim_number": c.claim_number,
            "claim_uuid": c.claim_uuid,
            "insurance_type": c.insurance_type,
            "status": c.status,
            "health_score": c.health_score,
            "claim_amount": c.claim_amount,
            "created_at": c.created_at.isoformat(),
            "ai_reasons": json.loads(c.ai_reasons or '[]'),
            "document_count": len(c.documents)
        })

    stats = {
        "total": len(result),
        "approved": sum(1 for c in result if c['status'] == 'approved'),
        "pending": sum(1 for c in result if c['status'] == 'pending'),
        "rejected": sum(1 for c in result if c['status'] == 'rejected'),
        "total_amount": round(sum(c['claim_amount'] for c in result), 2)
    }

    return jsonify({"claims": result, "stats": stats})


# Add this to the end of your claims.py file
@claims_bp.route('/status/<uuid>', methods=['GET'])
@jwt_required()
def check_status(uuid):
    user_id = get_jwt_identity()
    claim = Claim.query.filter_by(claim_uuid=uuid, user_id=user_id).first()
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
        
    return jsonify({
        "status": claim.status,
        "health_score": claim.health_score,
        "updated_at": claim.updated_at.isoformat()
    })