import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the new Client
# The SDK automatically picks up GEMINI_API_KEY from your .env
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def read_folder(folder_path):
    files_content = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".py", ".html", ".js")):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    files_content[path] = f.read()
    return files_content

backend_files = read_folder("backend")
frontend_files = read_folder("frontend")

prompt = f"""
You are an expert QA engineer. 
Backend files: {backend_files}
Frontend files: {frontend_files}
Perform a full QA check on the project structure and logic.
"""

# Use the stable model name 'gemini-2.0-flash' or 'gemini-1.5-flash'
response = client.models.generate_content(
    model="gemini-2.0-flash", 
    contents=prompt
)

print(response.text)