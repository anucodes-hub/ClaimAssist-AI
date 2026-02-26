import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from groq import Groq  # Updated to Groq

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Groq Client
# Ensure GROQ_API_KEY is in your .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

# 3. Flask Configuration
app.config['JWT_SECRET_KEY'] = 'claimassist-hackathon-secret-2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# 4. Middleware Setup
CORS(app, origins=["http://localhost:5173"])
jwt = JWTManager(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 5. Chatbot Route
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({"reply": "Please enter a message!"}), 400

        # Llama 3 via Groq is free, fast, and reliable
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You are ClaimAssist AI, a helpful insurance assistant. Provide clear, professional advice regarding insurance claims."},
                {"role": "user", "content": user_message}
            ]
        )

        return jsonify({"reply": completion.choices[0].message.content})
        
    except Exception as e:
        # Check your terminal/console to see the actual error
        print(f"Server Error: {e}")
        return jsonify({"reply": "I'm having a technical glitch. Please try again!"}), 500

# 6. Register Blueprints
from routes.auth import auth_bp
from routes.claims import claims_bp
from routes.insurance import insurance_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(claims_bp, url_prefix='/api/claims')
app.register_blueprint(insurance_bp, url_prefix='/api/insurance')

# 7. Start Server
if __name__ == '__main__':
    from models.database import init_db
    init_db()
    app.run(debug=True, port=5000)