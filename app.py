# app.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS

# --- Flask App Setup ---
app = Flask(__name__)
# Enable CORS for requests from your React app's origin (e.g., http://localhost:3000)
# In production, you might want to restrict this to your actual frontend domain.
CORS(app, resources={r"/chat": {"origins": "https://sage-frontend-mwiy.vercel.app/"}})

# --- Gemini API Configuration ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Make sure GOOGLE_API_KEY is set in your .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # Or 'gemini-1.5-pro'

# System Prompt (Defines Personality)
system_prompt = """You are Sage, a fun, friendly AI assistant. Respond in a conversational and engaging way.
Keep responses natural and casual, like a friend chatting.
If asked personal things, remind the user you're an AI and can't remember past conversations.
Keep your responses relatively concise for a chat interface."""

# --- API Endpoint ---
@app.route('/chat', methods=['POST'])
def chat_handler():
    """Handles incoming chat messages."""
    try:
        # Get message from the POST request's JSON body
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in request body"}), 400

        user_input = data['message']

        if not user_input.strip():
             return jsonify({"error": "Message cannot be empty"}), 400

        # Generate response using Gemini
        # Combine system prompt and user input for context
        full_prompt = system_prompt + "\nUser: " + user_input
        response = model.generate_content(full_prompt)

        # Return the response text in the expected format
        return jsonify({"response": response.text})

    except Exception as e:
        print(f"Error during chat generation: {e}") # Log the error server-side
        # Return a generic error to the client
        return jsonify({"error": "Failed to get response from AI"}), 500

# --- Run Flask App ---
if __name__ == '__main__':
    # Flask runs on port 5000 by default, which matches your React fetch URL
    app.run(debug=True) # debug=True is helpful for development, disable for production
