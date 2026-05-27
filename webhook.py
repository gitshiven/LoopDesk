import os
import re as _re
from dotenv import load_dotenv
load_dotenv()

if not os.path.exists("chroma_db"):
    print("Building vector store...")
    from rag.retriever import build_vectorstore
    build_vectorstore()

from flask import Flask, request, jsonify
from flask_cors import CORS
from agent.graph import run_ticket

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=False)

VAGUE_MESSAGES = {'hello', 'hi', 'hey', 'help', 'can you help me', 
                  'i have a problem', 'i need help', 'hello there', 'good morning'}

def is_valid_message(msg):
    if msg.strip().lower() in VAGUE_MESSAGES:
        return False
    words = msg.strip().split()
    real_words = [w for w in words if _re.match(r'[a-zA-Z]{2,}', w)]
    return len(real_words) >= 2

@app.route("/webhook/ticket", methods=["POST"])
def receive_ticket():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        message = data["message"]
        source = data.get("source", "unknown")

        if not is_valid_message(message):
            return jsonify({
                "source": source,
                "message": message,
                "category": "invalid",
                "confidence": 0.0,
                "escalated": False,
                "response": "Please describe your issue clearly so we can help you.",
                "escalation_summary": ""
            })

        print(f"Ticket received from {source}: {message}")
        result = run_ticket(message)

        return jsonify({
            "source": source,
            "message": message,
            "category": result["category"],
            "confidence": result["confidence"],
            "escalated": result["escalated"],
            "response": result["response"],
            "escalation_summary": result.get("escalation_summary", "")
        })
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "LoopDesk"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)