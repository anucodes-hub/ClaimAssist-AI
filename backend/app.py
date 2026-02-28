import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from groq import Groq
from models.database import db

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

HEAD

# 3. Flask Configuration

# 3. Flask & Database Configuration
origin/main
app.config['JWT_SECRET_KEY'] = 'claimassist-hackathon-secret-2024'
# Ensure upload folder points to the correct root 'uploads' directory
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

# --- NEW: SQLALCHEMY CONFIGURATION ---
# Using absolute path for the SQLite database ensures consistency
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'claimassist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 4. Initialize Database and Middleware
db.init_app(app) 
# Allow all origins for local development. 
# For production, you would restrict this to your frontend's domain.
# The "null" origin is for when you open index.html directly as a file.
CORS(app, origins=["http://localhost:5173", "null"])
jwt = JWTManager(app)

# Ensure the upload directory exists before the server starts
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 5. Chatbot Route
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        if not user_message:
            return jsonify({"reply": "Please enter a message!"}), 400

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You are ClaimAssist AI, a helpful insurance assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"reply": "Technical glitch. Please try again!"}), 500

# 6. Register Blueprints
# These must be imported after db.init_app(app) to avoid circular imports
from routes.auth import auth_bp
from routes.claims import claims_bp
from routes.insurance import insurance_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(claims_bp, url_prefix='/api/claims')
app.register_blueprint(insurance_bp, url_prefix='/api/insurance')
print(app.url_map)

# 7. Start Server & Create Tables
if __name__ == '__main__':
    with app.app_context():
        # This will create tables for Claim and Document models automatically
        db.create_all()  
    app.run(debug=True, port=5000)