import os
from dotenv import load_dotenv
from services.ai_service import analyze_document

load_dotenv()

def test_full_pipeline():
    # Make sure you have an image file named 'test_claim.jpg' in your backend folder
    test_image = "testfile.png" 
    
    if not os.path.exists(test_image):
        print(f"❌ Error: Please put an image named '{test_image}' in the backend folder first.")
        return

    print("🚀 Starting AI Pipeline Analysis...")
    results = analyze_document(test_image, "health")
    
    print("\n--- ANALYSIS RESULTS ---")
    print(f"Quality: {results['blur_analysis']['quality']} (Variance: {results['blur_analysis']['variance']})")
    print(f"Health Score: {results['health_score']}/100")
    print(f"Decision: {results['hitl']['message']}")
    print(f"Extracted Amount: ₹{results['claim_amount']}")

if __name__ == "__main__":
    test_full_pipeline()