from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from agent.graph import run_ticket

app = Flask(__name__)

@app.route("/webhook/ticket", methods=["POST"])
def receive_ticket():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    message = data["message"]
    source = data.get("source", "unknown")

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

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "LoopDesk"})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
