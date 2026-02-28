from ai_service import analyze_document, chat_with_ai

# Change this to your actual image file
file_path = "test.png"  
insurance_type = "health"

# ---- Test Document Analysis ----
result = analyze_document(file_path, insurance_type)

print("\n===== DOCUMENT ANALYSIS RESULT =====")
print(result)


# ---- Test Chatbot ----
chat_response = chat_with_ai("Why was my claim flagged?")

print("\n===== CHAT RESPONSE =====")
print(chat_response)