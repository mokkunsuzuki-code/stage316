from flask import Flask, request, jsonify
from dotenv import load_dotenv
from auth import is_valid_key, get_plan
from plans import PLANS
from rate_limit import check_rate_limit
from billing import create_checkout_session
import subprocess

load_dotenv()

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>REMEDA Stage316</h1>
    <h2>Trust Score SaaS API</h2>
    <p>Stage316 adds monetization, plan-based access, and Stripe Checkout.</p>

    <h3>Plans</h3>
    <ul>
      <li><b>Free</b>: 100 requests/day, limited verification</li>
      <li><b>Pro</b>: 10,000 requests/day, Sigstore verification</li>
      <li><b>Enterprise</b>: custom policy, QSP integration</li>
    </ul>

    <p><a href="/pricing">View Pricing</a></p>
    """


@app.route("/pricing")
def pricing():
    return """
    <h1>Pricing</h1>

    <h2>Free</h2>
    <p>100 requests/day. Limited verification.</p>

    <h2>Pro</h2>
    <p>10,000 requests/day. Sigstore verification included.</p>
    <p><a href="/api/subscribe">Subscribe to Pro</a></p>

    <h2>Enterprise</h2>
    <p>Custom policies, dedicated environment, and QSP integration.</p>
    """


@app.route("/success")
def success():
    return """
    <h1>Subscription Success</h1>
    <p>Your subscription checkout was completed.</p>
    <p>In production, this will activate your Pro API key via Stripe Webhook.</p>
    """


@app.route("/cancel")
def cancel():
    return """
    <h1>Subscription Canceled</h1>
    <p>Your checkout session was canceled.</p>
    """


@app.route("/api/subscribe")
def subscribe():
    checkout_url = create_checkout_session()

    if checkout_url is None:
        return jsonify({
            "error": "stripe_not_configured",
            "message": "Set STRIPE_SECRET_KEY and STRIPE_PRICE_PRO in .env"
        }), 500

    return jsonify({
        "checkout_url": checkout_url
    })


@app.route("/api/verify", methods=["POST"])
def verify():
    api_key = request.headers.get("x-api-key")

    if not is_valid_key(api_key):
        return jsonify({
            "error": "unauthorized",
            "message": "Invalid API Key"
        }), 403

    plan_name = get_plan(api_key)
    plan = PLANS.get(plan_name, PLANS["free"])

    if not check_rate_limit(api_key, plan["limit"]):
        return jsonify({
            "error": "rate_limit_exceeded",
            "plan": plan_name,
            "limit_per_day": plan["limit"]
        }), 429

    result = subprocess.run(
        ["python3", "evaluate.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return jsonify({
            "decision": "error",
            "score": 0.0,
            "message": "Evaluation failed",
            "stderr": result.stderr
        }), 500

    # evaluate.py already returns JSON text.
    # Stage316 adds SaaS metadata around the verified decision.
    response = app.response_class(
        response=result.stdout,
        status=200,
        mimetype="application/json"
    )

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
        "service": "remeda-saas-api",
        "stage": 316,
        "monetization": True,
        "billing": "stripe",
        "plans": list(PLANS.keys())
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3120, debug=True)
