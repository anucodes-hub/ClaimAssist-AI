import os
import cv2
import json
import base64
import random
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from groq import Groq

load_dotenv()

# ==============================
# 🔑 CLIENT INITIALIZATION
# ==============================

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ==============================
# 📷 IMAGE QUALITY CHECK
# ==============================

def detect_blur(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"is_blurry": True, "variance": 0, "quality": "unreadable", "score": 0}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()

        is_blurry = variance < 70
        quality = "poor" if variance < 70 else ("acceptable" if variance < 200 else "good")

        return {
            "is_blurry": is_blurry,
            "variance": round(float(variance), 2),
            "quality": quality,
            "score": min(100, int(variance / 5))
        }
    except Exception as e:
        return {"is_blurry": True, "variance": 0, "quality": "error", "score": 0}


# ==============================
# 🧠 GEMINI OCR (Extraction Only)
# ==============================

def gemini_ocr(image_path, insurance_type):

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"""
You are a strict OCR extraction engine.

Extract insurance data from this {insurance_type} document.

DO NOT guess.
If a field is not visible, return empty string.

Return valid JSON only:

{{
  "patient_name": "",
  "policy_number": "",
  "claim_amount": 0,
  "has_signature": false,
  "has_stamp": false,
  "text_clarity": "",
  "admission_date": "",
  "claim_date": "",
  "extraction_confidence": 0
}}
"""
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64.b64encode(image_bytes).decode("utf-8")
                        }
                    }
                ]
            }
        ]
    )

    raw = response.text.strip()

    if "```" in raw:
        raw = raw.split("```")[1]

    json_start = raw.find("{")
    json_end = raw.rfind("}") + 1

    if json_start != -1 and json_end != -1:
        raw = raw[json_start:json_end]

    try:
        return json.loads(raw)
    except Exception as e:
        print("\n⚠️ Gemini returned invalid JSON:")
        print(raw)
        return {
            "error": "Invalid JSON from Gemini",
            "extraction_confidence": 0
        }


# ==============================
# 📅 DATE VALIDATION
# ==============================

def validate_dates(extracted_data):
    issues = []

    try:
        adm = extracted_data.get("admission_date")
        claim = extracted_data.get("claim_date")

        if adm and claim:
            adm_date = datetime.strptime(adm, "%Y-%m-%d")
            claim_date = datetime.strptime(claim, "%Y-%m-%d")

            if claim_date < adm_date:
                issues.append({
                    "type": "date_mismatch",
                    "severity": "high",
                    "message": "Claim date is before admission date"
                })
    except:
        pass

    return issues


# ==============================
# 🤖 ML SCORING (Risk Engine)
# ==============================

def get_ml_prediction(features):

    rejection_prob = 0.1

    if not features.get("has_signature"):
        rejection_prob += 0.35

    if features.get("is_blurry"):
        rejection_prob += 0.25

    if features.get("date_issues") > 0:
        rejection_prob += 0.30

    if features.get("extraction_confidence", 1) < 0.7:
        rejection_prob += 0.15

    rejection_prob += random.uniform(-0.02, 0.02)

    return round(min(0.95, max(0.02, rejection_prob)), 2)


# ==============================
# 👩‍⚖️ HUMAN-IN-THE-LOOP
# ==============================

def apply_hitl_logic(rejection_prob):

    confidence = 1 - rejection_prob

    if confidence >= 0.90:
        return {
            "action": "auto_approve",
            "status": "approved",
            "requires_human": False
        }

    elif confidence >= 0.70:
        return {
            "action": "needs_confirmation",
            "status": "pending",
            "requires_human": True
        }

    else:
        return {
            "action": "manual_review",
            "status": "under_review",
            "requires_human": True
        }


# ==============================
# 🚀 MAIN PIPELINE
# ==============================

def analyze_document(file_path, insurance_type):

    results = {}

    # 1️⃣ Blur Detection
    blur_result = detect_blur(file_path)
    results["blur_analysis"] = blur_result

    # 2️⃣ Gemini OCR Extraction
    extracted = gemini_ocr(file_path, insurance_type)
    results["extracted_data"] = extracted

    # 3️⃣ Date Validation
    date_issues = validate_dates(extracted)
    results["date_issues"] = date_issues

    # 4️⃣ ML Features
    features = {
        "has_signature": extracted.get("has_signature", False),
        "is_blurry": blur_result["is_blurry"],
        "date_issues": len(date_issues),
        "extraction_confidence": extracted.get("extraction_confidence", 0.5)
    }

    rejection_prob = get_ml_prediction(features)

    results["rejection_probability"] = rejection_prob
    results["health_score"] = round((1 - rejection_prob) * 100, 1)

    # 5️⃣ HITL Decision
    results["hitl"] = apply_hitl_logic(rejection_prob)
    results["processed_at"] = datetime.now().isoformat()

    return results


# ==============================
# 💬 GROQ CHATBOT (Chat Only)
# ==============================

def chat_with_ai(user_message):

    system_prompt = """
You are ClaimAssist AI Support.

Explain claim status clearly.
Help users understand missing documents.
Be professional and simple.
"""

    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content