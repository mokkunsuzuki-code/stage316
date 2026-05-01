🚀 REMEDA Stage315 — Trust Score API with Sigstore Verification

## What is this?

REMEDA Stage315 provides **verifiable trust decisions as an API**.

It evaluates a target system and returns:

- ✅ accept
- ⚠️ pending
- ❌ reject

With a **Trust Score (0.0 - 1.0)** and **cryptographic verification**.

---

## 🔥 Why it matters

Modern systems lack **verifiable trust**.

- Is this system authentic?
- Was it tampered with?
- Can we trust this output?

👉 REMEDA answers these questions programmatically.

---

## 🧠 Core Features

- Trust Score calculation
- Decision engine (accept / pending / reject)
- Sigstore verification (cosign)
- API-key based access
- JSON-based verification model

---

## 🔐 Proof Layer

This system uses:

- Sigstore (cosign)
- Cryptographic signatures
- Verifiable decision outputs

👉 Not just "trust me" — **prove it**

---

## ⚙️ API Example

```bash
curl -X POST http://127.0.0.1:3120/api/verify \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "url": "https://example.com",
    "manifest": {
      "integrity": true,
      "execution": true,
      "identity": true,
      "timestamp": true,
      "workflow": "github-actions"
    }
  }'
Response
{
  "decision": "accept",
  "score": 1.0,
  "sigstore_verified": true,
  "breakdown": {
    "integrity": 1.0,
    "execution": 1.0,
    "identity": 1.0,
    "time": 1.0,
    "sigstore": 1.0
  }
}
💰 Pricing (Planned)
Free
100 requests/day
Limited verification
Pro
Full verification
Sigstore included
History access
Enterprise
Custom policies
Dedicated environment
QSP integration
🚀 Vision

👉 Trust becomes programmable

REMEDA aims to become:

"Stripe for Trust"

📦 Repository

https://github.com/mokkunsuzuki-code/stage315

🛡 License

MIT License