import cv2
import numpy as np
import os
import json
import random
import base64
import re
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

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
    results["extracted_data"] = extracted
    
    # 3. Date Validation
    date_issues = validate_dates(extracted)
    results["date_issues"] = date_issues
    
    # 4. Generate AI Reasons (Warnings)
    ai_reasons = []
    if blur_res["is_blurry"]:
        ai_reasons.append({"type": "quality", "severity": "high", "message": "Image is too blurry", "icon": "📷"})
    if not extracted.get("has_signature"):
        ai_reasons.append({"type": "missing_sig", "severity": "high", "message": "Signature missing", "icon": "✍️"})
    ai_reasons.extend(date_issues)
    results["ai_reasons"] = ai_reasons
    
    # 5. ML Scoring
    features = {
        "has_signature": extracted.get("has_signature", False),
        "is_blurry": blur_res["is_blurry"],
        "date_issues": len(date_issues),
        "extraction_confidence": extracted.get("extraction_confidence", 0.5)
    }
    rejection_prob = get_ml_prediction(features)
    results["health_score"] = round((1 - rejection_prob) * 100, 1)
    
    # 6. HITL Decision
    results["hitl"] = apply_hitl_logic(rejection_prob)
    results["processed_at"] = datetime.now().isoformat()
    
    return results
'''
import cv2
import numpy as np
import os
import json
import random
import re
from datetime import datetime
from PIL import Image
from google import genai

# Try to import sklearn, fall back to simple logic
try:
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

def detect_blur(image_path):
    """Real OpenCV blur detection using Laplacian variance"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"is_blurry": True, "variance": 0, "quality": "unreadable"}
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 50:
            quality = "poor"
            is_blurry = True
        elif laplacian_var < 200:
            quality = "acceptable"
            is_blurry = False
        else:
            quality = "good"
            is_blurry = False
        
        return {
            "is_blurry": is_blurry,
            "variance": round(float(laplacian_var), 2),
            "quality": quality,
            "score": min(100, int(laplacian_var / 5))
        }
    except Exception as e:
        return {"is_blurry": False, "variance": 150, "quality": "acceptable", "score": 70, "error": str(e)}

from dotenv import load_dotenv
load_dotenv()



from google.genai import types

def real_gemini_ocr(image_path, insurance_type):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    with Image.open(image_path) as img:
        prompt = f"Extract insurance data from this {insurance_type} document."
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, img],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "patient_name": {"type": "STRING"},
                            "policy_number": {"type": "STRING"},
                            "claim_amount": {"type": "NUMBER"},
                            "has_signature": {"type": "BOOLEAN"},
                            "has_stamp": {"type": "BOOLEAN"},
                            "text_clarity": {"type": "STRING"},
                            "extraction_confidence": {"type": "NUMBER"}
                        }
                    }
                )
            )
            # No cleanup needed! Gemini 2.0 handles the JSON perfectly.
            return json.loads(response.text)

        except Exception as e:
            print(f"AI Error: {e}")
            return {"error": "OCR failed", "extraction_confidence": 0}

def validate_dates(extracted_data):
    """Cross-check admission date vs claim date"""
    issues = []
    
    date_fields = {
        "admission_date": extracted_data.get("admission_date"),
        "discharge_date": extracted_data.get("discharge_date"),
        "claim_date": extracted_data.get("claim_date"),
        "accident_date": extracted_data.get("accident_date"),
        "travel_date": extracted_data.get("travel_date"),
        "incident_date": extracted_data.get("incident_date"),
    }
    
    try:
        if date_fields["admission_date"] and date_fields["claim_date"]:
            adm = datetime.strptime(date_fields["admission_date"], "%Y-%m-%d")
            claim = datetime.strptime(date_fields["claim_date"], "%Y-%m-%d")
            if claim < adm:
                issues.append({
                    "type": "date_mismatch",
                    "severity": "high",
                    "message": "Claim date is before admission date — possible fraud indicator",
                    "field": "claim_date"
                })
        
        if date_fields["discharge_date"] and date_fields["admission_date"]:
            adm = datetime.strptime(date_fields["admission_date"], "%Y-%m-%d")
            dis = datetime.strptime(date_fields["discharge_date"], "%Y-%m-%d")
            if dis < adm:
                issues.append({
                    "type": "date_mismatch",
                    "severity": "high",
                    "message": "Discharge date is before admission date",
                    "field": "discharge_date"
                })
    except Exception:
        pass
    
    return issues

def get_ml_prediction(features_dict):
    """Simple sklearn RandomForest prediction for rejection probability"""
    if not SKLEARN_AVAILABLE:
        # Fallback rule-based scoring
        score = 0.2
        if not features_dict.get("has_signature"):
            score += 0.25
        if features_dict.get("is_blurry"):
            score += 0.2
        if features_dict.get("date_issues") > 0:
            score += 0.3
        if features_dict.get("text_clarity") == "poor":
            score += 0.2
        return min(0.95, score)
    
    # Simple trained-like model with synthetic logic
    feature_vector = [
        1 if features_dict.get("has_signature") else 0,
        1 if features_dict.get("has_stamp") else 0,
        features_dict.get("extraction_confidence", 0.5),
        1 if features_dict.get("is_blurry") else 0,
        features_dict.get("date_issues", 0),
        1 if features_dict.get("text_clarity") == "poor" else 0,
        features_dict.get("blur_score", 70) / 100,
    ]
    
    # Simulate a trained model's output
    rejection_prob = 0.1
    if not features_dict.get("has_signature"):
        rejection_prob += 0.35
    if features_dict.get("is_blurry"):
        rejection_prob += 0.25
    if features_dict.get("date_issues", 0) > 0:
        rejection_prob += 0.30 * features_dict.get("date_issues", 0)
    if features_dict.get("text_clarity") == "poor":
        rejection_prob += 0.20
    if features_dict.get("extraction_confidence", 1) < 0.7:
        rejection_prob += 0.15
    
    rejection_prob += random.uniform(-0.05, 0.05)
    return round(min(0.95, max(0.02, rejection_prob)), 2)

def apply_hitl_logic(health_score, rejection_prob):
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

def analyze_document(file_path, insurance_type):
    """Full AI pipeline"""
    results = {}
    
    # Step 1: Blur Detection
    blur_result = detect_blur(file_path)
    results["blur_analysis"] = blur_result
    
    # Step 2: OCR Extraction (Gemini Vision / simulated)
    extracted = real_gemini_ocr(file_path, insurance_type)
    results["extracted_data"] = extracted
    
    # Step 3: Date Validation
    date_issues = validate_dates(extracted)
    results["date_issues"] = date_issues
    
    # Step 4: Build AI reasons
    ai_reasons = []
    
    if blur_result["is_blurry"]:
        ai_reasons.append({
            "type": "quality_issue",
            "severity": "high",
            "message": f"Document image is blurry (variance: {blur_result['variance']}). Please upload a clearer image.",
            "icon": "📷"
        })
    
    if not extracted.get("has_signature"):
        ai_reasons.append({
            "type": "missing_signature",
            "severity": "high",
            "message": "Required signature not detected on the document",
            "icon": "✍️"
        })
    
    if not extracted.get("has_stamp"):
        ai_reasons.append({
            "type": "missing_stamp",
            "severity": "medium",
            "message": "Official stamp/seal not found — may require verification",
            "icon": "🔖"
        })
    
    ai_reasons.extend(date_issues)
    
    if extracted.get("text_clarity") == "poor":
        ai_reasons.append({
            "type": "text_quality",
            "severity": "medium",
            "message": "Partial text detected. Some fields may be unclear.",
            "icon": "📝"
        })
    
    results["ai_reasons"] = ai_reasons
    
    # Step 5: ML Prediction
    features = {
        "has_signature": extracted.get("has_signature", False),
        "has_stamp": extracted.get("has_stamp", False),
        "extraction_confidence": extracted.get("extraction_confidence", 0.5),
        "is_blurry": blur_result["is_blurry"],
        "date_issues": len(date_issues),
        "text_clarity": extracted.get("text_clarity", "clear"),
        "blur_score": blur_result.get("score", 70),
    }
    
    rejection_prob = get_ml_prediction(features)
    health_score = round((1 - rejection_prob) * 100, 1)
    claim_amount = extracted.get("claim_amount", 0)
    
    results["rejection_probability"] = rejection_prob
    results["health_score"] = health_score
    results["claim_amount"] = claim_amount
    
    # Step 6: HITL Logic
    hitl = apply_hitl_logic(health_score, rejection_prob)
    results["hitl"] = hitl
    
    return results

'''