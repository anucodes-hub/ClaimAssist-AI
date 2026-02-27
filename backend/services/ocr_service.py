import os
import json
from google import genai
from PIL import Image
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize the New GenAI Client
# This replaces both pytesseract and the Groq client for OCR tasks
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_structured_data(image_path, insurance_type):
    """
    Uses Gemini 2.0 Flash to perform multimodal OCR and JSON extraction.
    No local Tesseract installation required.
    """
    try:
        # Load the image for the model
        img = Image.open(image_path)
        
        # 3. Multimodal Prompt (Combines OCR + Parsing)
        prompt = f"""
        Analyze this {insurance_type} insurance document image.
        Extract the following fields and return ONLY a valid JSON object:
        - patient_name
        - policy_number
        - claim_amount (extract only the numeric value)
        - admission_date
        - hospital_gst_number
        
        If a field is not visible, set its value to null.
        """

        # 4. Generate Content with Stable Model Name
        # Using 'gemini-2.0-flash' resolves the 404/NotFound errors
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, img]
        )

        # 5. Parse and Return JSON
        # The new SDK returns a clean response object
        return json.loads(response.text)

    except Exception as e:
        print(f"Extraction Pipeline Error: {e}")
        return {"error": str(e)}