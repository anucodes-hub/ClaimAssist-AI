from services.ocr_service import extract_structured_data
import os

# Put a sample insurance image in your backend folder and rename it to 'sample.jpg'
image_path = "sample.png" 

if os.path.exists(image_path):
    print("🚀 Running Real Extraction Test...")
    result = extract_structured_data(image_path, "health")
    print("\n--- EXTRACTION RESULT ---")
    print(result)
else:
    print(f"❌ Please place a file named '{image_path}' in the backend folder first.")