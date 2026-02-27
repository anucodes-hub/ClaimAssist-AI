import pytesseract
from PIL import Image
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# If on Windows, uncomment and point to your tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_structured_data(image_path, insurance_type):
    try:
        # 1. Local OCR with Tesseract
        with Image.open(image_path) as img:
            raw_text = pytesseract.image_to_string(img)
        
        if not raw_text.strip():
            return {"error": "No text detected in document"}

        # 2. Use Groq to parse the raw text into JSON (The "Smart" Alternative)
        prompt = f"""
        Extract the following fields from this RAW OCR TEXT from a {insurance_type} document.
        Fields: patient_name, policy_number, claim_amount, admission_date, hospital_gst_number.
        
        RAW TEXT:
        {raw_text}

        Return ONLY a JSON object. If a field is not found, set it to null.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {"error": str(e)}