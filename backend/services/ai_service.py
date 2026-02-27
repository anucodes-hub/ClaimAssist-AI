import cv2 
import numpy as np
import os
import json
import random
import base64
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from ultralytics import YOLO

# Load YOLOv8 model (tiny version, or your trained signature/seal model)
yolo_model = YOLO("yolov8n.pt")  # replace with your trained weights if you have one

def detect_signatures_seals(image_path):
    """Returns a JSON of detected signatures and seals with bounding boxes."""
    if not os.path.exists(image_path):
        return {"error": "File not found"}

    results = yolo_model.predict(image_path)

    detections = []
    for result in results:
        for box in result.boxes:
            detections.append({
                "bbox": box.xyxy.tolist(),  # [x1, y1, x2, y2]
                "confidence": float(box.conf),
                "class_id": int(box.cls),
                "label": yolo_model.names[int(box.cls)]
            })
    return {"detections": detections}

# Try to import sklearn, fall back to simple logic if not installed
try:
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- UTILITY FUNCTIONS ---

def encode_image(image_path):
    """Converts image to base64 for Groq Vision API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def detect_blur(image_path):
    """OpenCV blur detection using Laplacian variance"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"is_blurry": True, "variance": 0, "quality": "unreadable"}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        is_blurry = laplacian_var < 70 
        quality = "poor" if is_blurry else ("acceptable" if laplacian_var < 200 else "good")
        
        return {
            "is_blurry": is_blurry,
            "variance": round(float(laplacian_var), 2),
            "quality": quality,
            "score": min(100, int(laplacian_var / 5))
        }
    except Exception as e:
        return {"is_blurry": False, "variance": 150, "quality": "acceptable", "score": 70, "error": str(e)}

# --- AI & OCR LOGIC ---

def real_groq_ocr(image_path, insurance_type):
    """Uses Groq Llama 4 Scout for OCR and Data Extraction"""
    try:
        base64_image = encode_image(image_path)
        model_id = "meta-llama/llama-4-scout-17b-16e-instruct"

        prompt = f"""Extract insurance data from this {insurance_type} document. 
        Return a JSON object with: patient_name, policy_number, claim_amount (number), 
        has_signature (bool), has_stamp (bool), text_clarity (string), 
        admission_date (YYYY-MM-DD), claim_date (YYYY-MM-DD), extraction_confidence (0-1)."""

        response = client.chat.completions.create(
            model=model_id,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            response_format={"type": "json_object"} 
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return {"error": "OCR failed", "extraction_confidence": 0}

# --- INSURANCE ANALYSIS LOGIC ---

def validate_dates(extracted_data):
    """Cross-check dates for fraud indicators"""
    issues = []
    try:
        adm_str = extracted_data.get("admission_date")
        claim_str = extracted_data.get("claim_date")
        
        if adm_str and claim_str:
            adm = datetime.strptime(adm_str, "%Y-%m-%d")
            claim = datetime.strptime(claim_str, "%Y-%m-%d")
            if claim < adm:
                issues.append({
                    "type": "date_mismatch",
                    "severity": "high",
                    "message": "Claim date is before admission date — possible fraud indicator",
                    "field": "claim_date"
                })
    except: pass
    return issues

def get_ml_prediction(features):
    """Predicts rejection probability based on document features"""
    rejection_prob = 0.1
    if not features.get("has_signature"): rejection_prob += 0.35
    if features.get("is_blurry"): rejection_prob += 0.25
    if features.get("date_issues", 0) > 0: rejection_prob += 0.30
    if features.get("extraction_confidence", 1) < 0.7: rejection_prob += 0.15
    
    rejection_prob += random.uniform(-0.02, 0.02)
    return round(min(0.95, max(0.02, rejection_prob)), 2)

def apply_hitl_logic(rejection_prob):
    """Human-in-the-loop decision logic"""
    confidence = 1 - rejection_prob
    
    if confidence >= 0.90:
        return {
            "action": "auto_approve",
            "status": "approved",
            "message": "Auto-approved: High confidence score",
            "requires_human": False
        }
    elif confidence >= 0.70:
        return {
            "action": "needs_confirmation",
            "status": "pending",
            "message": "Requires your confirmation before processing",
            "requires_human": True
        }
    else:
        return {
            "action": "manual_review",
            "status": "under_review",
            "message": "Flagged for manual review by claims officer",
            "requires_human": True
        }

# --- MAIN PIPELINE ---

def analyze_document(file_path, insurance_type):
    """The complete ClaimAssist AI pipeline"""
    results = {}
    
    # 1. Blur Analysis
    blur_res = detect_blur(file_path)
    results["blur_analysis"] = blur_res

    # 2. OCR Extraction
    extracted = real_groq_ocr(file_path, insurance_type)
    
    # 3. YOLO detection for visual verification (update extracted flags)
    yolo_result = detect_signatures_seals(file_path)
    results["yolo_detections"] = yolo_result

    extracted["has_signature"] = any(d["label"] == "signature" for d in yolo_result.get("detections", []))
    extracted["has_stamp"] = any(d["label"] == "seal" for d in yolo_result.get("detections", []))
    
    results["extracted_data"] = extracted
    
    # 4. Date Validation
    date_issues = validate_dates(extracted)
    results["date_issues"] = date_issues
    
    # 5. Generate AI Reasons (Warnings)
    ai_reasons = []
    if blur_res["is_blurry"]:
        ai_reasons.append({"type": "quality", "severity": "high", "message": "Image is too blurry", "icon": "📷"})
    if not extracted.get("has_signature"):
        ai_reasons.append({"type": "missing_sig", "severity": "high", "message": "Signature missing", "icon": "✍️"})
    ai_reasons.extend(date_issues)
    results["ai_reasons"] = ai_reasons
    
    # 6. ML Scoring
    features = {
        "has_signature": extracted.get("has_signature", False),
        "is_blurry": blur_res["is_blurry"],
        "date_issues": len(date_issues),
        "extraction_confidence": extracted.get("extraction_confidence", 0.5)
    }
    rejection_prob = get_ml_prediction(features)
    results["health_score"] = round((1 - rejection_prob) * 100, 1)
    
    # 7. HITL Decision
    results["hitl"] = apply_hitl_logic(rejection_prob)
    results["processed_at"] = datetime.now().isoformat()
    
    return results