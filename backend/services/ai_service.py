import cv2 
import numpy as np
import os
import json
import random
import base64
from datetime import datetime
from google import genai  # NEW: Using the production SDK
from PIL import Image     # Required for Gemini input
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

# 1. Initialize Clients
# Replaces Groq with the new Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Load YOLOv8 model for visual verification
yolo_model = YOLO("yolov8n.pt") 

# --- UTILITY FUNCTIONS ---

def detect_signatures_seals(image_path):
    """Returns a JSON of detected signatures and seals with bounding boxes."""
    if not os.path.exists(image_path):
        return {"error": "File not found"}
    results = yolo_model.predict(image_path)
    detections = []
    for result in results:
        for box in result.boxes:
            detections.append({
                "bbox": box.xyxy.tolist()[0],
                "confidence": float(box.conf),
                "class_id": int(box.cls),
                "label": yolo_model.names[int(box.cls)]
            })
    return {"detections": detections}

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
    except Exception:
        return {"is_blurry": False, "variance": 150, "quality": "acceptable", "score": 70}

# --- NEW: GEMINI OCR LOGIC ---

def real_gemini_ocr(image_path, insurance_type):
    """Uses Gemini 2.0 Flash for high-accuracy OCR and Data Extraction"""
    try:
        img = Image.open(image_path)
        
        # Multimodal Prompt
        prompt = f"""
        Extract insurance data from this {insurance_type} document image. 
        Return ONLY a JSON object with: 
        patient_name (string), 
        policy_number (string), 
        claim_amount (number), 
        admission_date (YYYY-MM-DD), 
        claim_date (YYYY-MM-DD),
        extraction_confidence (float 0-1)
        
        If a field is missing, set it to null.
        """

        # Using stable gemini-2.0-flash to avoid 404/NotFound errors
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, img]
        )
        
        # Clean response and parse JSON
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
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
                    "message": "Claim date is before admission date — fraud indicator",
                    "icon": "📅"
                })
    except: pass
    return issues

def get_ml_prediction(features):
    """Rejection probability based on document features"""
    rejection_prob = 0.1
    if not features.get("has_signature"): rejection_prob += 0.35
    if features.get("is_blurry"): rejection_prob += 0.25
    if features.get("date_issues", 0) > 0: rejection_prob += 0.30
    rejection_prob += random.uniform(-0.02, 0.02)
    return round(min(0.95, max(0.02, rejection_prob)), 2)

def apply_hitl_logic(rejection_prob):
    """Phase 3: Autonomous HITL decision logic"""
    confidence = 1 - rejection_prob
    if confidence >= 0.90:
        return {"action": "auto_approve", "status": "approved", "requires_human": False}
    elif confidence >= 0.70:
        return {"action": "needs_confirmation", "status": "pending", "requires_human": True}
    else:
        return {"action": "manual_review", "status": "under_review", "requires_human": True}

# --- MAIN PIPELINE ---

def analyze_document(file_path, insurance_type):
    """The complete ClaimAssist AI pipeline updated for Phase 3"""
    results = {}
    
    # 1. Visual Quality Check (Blur)
    blur_res = detect_blur(file_path)
    results["blur_analysis"] = blur_res

    # 2. Gemini OCR Extraction (Replaced Groq)
    extracted = real_gemini_ocr(file_path, insurance_type)
    
    # 3. YOLO detection for visual verification
    yolo_result = detect_signatures_seals(file_path)
    results["yolo_detections"] = yolo_result

    # Sync AI text flags with YOLO visual findings
    extracted["has_signature"] = any(d["label"] == "signature" for d in yolo_result.get("detections", []))
    extracted["has_stamp"] = any(d["label"] == "seal" for d in yolo_result.get("detections", []))
    results["extracted_data"] = extracted
    
    # 4. Fraud/Date Validation
    date_issues = validate_dates(extracted)
    results["date_issues"] = date_issues
    
    # 5. AI Reasoning
    ai_reasons = []
    if blur_res["is_blurry"]:
        ai_reasons.append({"type": "quality", "severity": "high", "message": "Image blurry", "icon": "📷"})
    if not extracted.get("has_signature"):
        ai_reasons.append({"type": "missing_sig", "severity": "high", "message": "No signature", "icon": "✍️"})
    ai_reasons.extend(date_issues)
    results["ai_reasons"] = ai_reasons
    
    # 6. Scoring & Decision
    features = {
        "has_signature": extracted.get("has_signature", False),
        "is_blurry": blur_res["is_blurry"],
        "date_issues": len(date_issues)
    }
    rejection_prob = get_ml_prediction(features)
    results["health_score"] = round((1 - rejection_prob) * 100, 1)
    results["hitl"] = apply_hitl_logic(rejection_prob)
    results["processed_at"] = datetime.now().isoformat()
    
    return results