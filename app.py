from flask import Flask, request, jsonify
from auth import is_valid_key
import subprocess

app = Flask(__name__)

@app.route("/api/verify", methods=["POST"])
def verify():
    api_key = request.headers.get("x-api-key")

    if not is_valid_key(api_key):
        return jsonify({
            "error": "unauthorized",
            "message": "Invalid API Key"
        }), 403

    result = subprocess.run(
        ["python3", "evaluate.py"],
        capture_output=True,
        text=True
    )

    return result.stdout

@app.route("/api/health")
def health():
    return jsonify({
        "ok": True,
        "stage": 315,
        "service": "remeda-saas-api"
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3120, debug=True)
