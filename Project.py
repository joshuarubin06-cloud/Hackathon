from google import genai
from dotenv import load_dotenv
import os
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS   # ← NEW: fixes browser cross-origin errors

load_dotenv()

# ── Load dataset once at startup ───────────────────────────────────────────
file_path = 'healthcare_real_time_dataset.csv'
df = pd.read_csv(file_path)
dataset_context = df.head(15).to_string()


def make_client():
    """Create a Gemini client using the API_KEY from .env"""
    api_key = os.getenv("API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# ── Flask app ──────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)   # ← Allows the HTML file to call this backend from any origin


@app.route('/')
def index():
    """Serve the frontend HTML."""
    if os.path.exists('project.html'):
        return send_from_directory('.', 'project.html')
    return send_from_directory('.', 'website.html')


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """
    Accepts JSON body:
      { "symptoms": "headache and runny nose" }
      OR
      { "prompt": "Any custom question" }

    Returns:
      { "text": "AI response..." }
    """
    client = make_client()
    if client is None:
        return jsonify({
            "error": "API_KEY not found. Add it to your .env file as: API_KEY=your_key_here"
        }), 500

    data = request.get_json() or {}
    user_prompt = data.get('prompt')
    symptoms    = data.get('symptoms')

    # Build a prompt if only symptoms were sent
    if not user_prompt and symptoms:
        user_prompt = (
            f"A user has the following symptoms: {symptoms}. "
            "List possible medical conditions and briefly explain each. "
            "Keep it concise and factual."
        )

    if not user_prompt:
        return jsonify({"error": "No prompt or symptoms provided"}), 400

    full_prompt = (
        f"Use this healthcare dataset as background context:\n{dataset_context}\n\n"
        f"User Question: {user_prompt}\n"
        "Respond concisely and straight to the point."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    text = getattr(response, 'text', None)
    if text is None:
        try:
            return jsonify(response)
        except Exception:
            return jsonify({"result": str(response)})

    return jsonify({"text": text})


# ── Run ────────────────────────────────────────────────────────────────────:
# debug=True is fine locally; turn it off before deploying
app.run(host='127.0.0.1', port=5000, debug=False)