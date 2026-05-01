from flask import Flask, request, jsonify
from dotenv import load_dotenv
from auth import is_valid_key, get_plan
from plans import PLANS
from rate_limit import check_rate_limit
from billing import create_checkout_session
import subprocess
import json

load_dotenv()

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>REMEDA Stage316</h1>
    <h2>Trust Score SaaS API</h2>
    """


@app.route("/api/subscribe")
def subscribe():
    checkout_url = create_checkout_session()

    if checkout_url is None:
        return jsonify({
            "error": "stripe_not_configured"
        }), 500

    return jsonify({
        "checkout_url": checkout_url
    })


@app.route("/api/verify", methods=["POST"])
def verify():
    api_key = request.headers.get("x-api-key")

    if not is_valid_key(api_key):
        return jsonify({
            "error": "unauthorized"
        }), 403

    plan_name = get_plan(api_key)
    plan = PLANS.get(plan_name, PLANS["free"])

    if not check_rate_limit(api_key, plan["limit"]):
        return jsonify({
            "error": "rate_limit_exceeded"
        }), 429

    result = subprocess.run(
        ["python3", "evaluate.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return jsonify({
            "error": "execution_failed",
            "stderr": result.stderr
        }), 500

    if not result.stdout:
        return jsonify({
            "error": "empty_output",
            "stderr": result.stderr
        }), 500

    try:
        data = json.loads(result.stdout)
    except Exception:
        return jsonify({
            "error": "invalid_json",
            "raw_output": result.stdout
        }), 500

    # 🔥 プラン制御（ここが重要）
    if not plan["sigstore"]:
        data["sigstore_verified"] = False

        if "breakdown" in data:
            data["breakdown"]["sigstore"] = 0.0

        scores = data.get("breakdown", {})
        if scores:
            data["score"] = sum(scores.values()) / len(scores)

    response = jsonify(data)

    response.headers["X-REMEDA-Stage"] = "316"
    response.headers["X-REMEDA-Plan"] = plan_name
    response.headers["X-REMEDA-Plan-Name"] = plan["name"]
    response.headers["X-REMEDA-Daily-Limit"] = str(plan["limit"])
    response.headers["X-REMEDA-Sigstore-Enabled"] = str(plan["sigstore"]).lower()

    return response


@app.route("/api/health")
def health():
    return jsonify({
        "ok": True,
        "stage": 316,
        "monetization": True
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3120, debug=True)
