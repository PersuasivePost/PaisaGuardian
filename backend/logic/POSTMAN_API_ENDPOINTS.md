# 🚀 Fraud Sentinel API - Postman Collection

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require JWT token in Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

Get token from auth server (Node.js on port 3000) first.

---

## 📋 Complete API Endpoints List

### 1. Health & Status (No Auth Required)

#### GET `/health`
Check API health status
```json
Method: GET
URL: http://localhost:8000/health
Headers: None required
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-29T12:00:00",
  "version": "1.0.0",
  "gemini_enabled": true,
  "gemini_model": "gemini-pro"
}
```

---

#### GET `/`
Root endpoint
```json
Method: GET
URL: http://localhost:8000/
Headers: None required
```

---

### 2. Analysis Endpoints (Auth Required)

#### POST `/analyze/url`
🤖 Agentic URL Analysis with Gemini AI
```json
Method: POST
URL: http://localhost:8000/analyze/url
Headers: 
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN

Body (JSON):
{
  "url": "https://phonepe-verifykec.com",
  "qr_code_data": null,
  "domain_details": {
    "creation_date": "2024-01-15",
    "ssl_valid": false,
    "registrar": "Unknown",
    "age_days": 45
  },
  "html_content": {
    "has_payment_forms": true,
    "has_password_fields": true,
    "has_otp_fields": true,
    "has_credit_card_fields": false,
    "suspicious_keywords": ["urgent", "verify", "account blocked"]
  },
  "redirect_chain": {
    "redirects": [
      "https://phonepe-verifykec.com",
      "https://verify-phonepe.com"
    ],
    "final_url": "https://verify-phonepe.com/login"
  },
  "typosquatting_score": 0.85,
  "similar_to_domain": "phonepe.com",
  "enhanced_perception": {
    "certificate_issuer": "Unknown",
    "has_suspicious_keywords": true,
    "page_title": "PhonePe Verification"
  }
}
```

**Response:**
```json
{
  "url": "https://phonepe-verifykec.com",
  "risk_level": "high",
  "risk_score": 85.3,
  "is_safe": false,
  "fraud_indicators": [
    "Domain uses lookalike characters",
    "SSL certificate invalid",
    "🤖 AI: Typosquatting attack mimicking PhonePe",
    "🤖 AI: Fake payment form detected",
    "Recent domain registration (45 days)"
  ],
  "detected_fraud_types": ["phishing", "typosquatting"],
  "recommendations": [
    "🛑 AGENT ACTION: Block this URL immediately",
    "Do not enter any personal or payment information",
    "Verify the official website"
  ],
  "details": {
    "ai_enabled": true,
    "ai_fraud_type": "phishing",
    "ai_confidence": "high",
    "ai_reasoning": "This URL mimics PhonePe using typosquatting..."
  },
  "qr_code_analysis": null,
  "domain_risk_factors": ["new_domain", "ssl_invalid"],
  "html_threats": ["payment_form", "otp_field"],
  "redirect_risk": "high"
}
```

---

#### POST `/analyze/sms`
SMS Analysis with Gemini AI
```json
Method: POST
URL: http://localhost:8000/analyze/sms
Headers: 
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN

Body (JSON):
{
  "message": "Dear customer, your KYC is expired. Update now by clicking bit.ly/kyc-update or your account will be blocked within 24 hours.",
  "sender": "VD-KYCINF",
  "device_info": {
    "is_new_device": false,
    "sim_changed_recently": false,
    "screen_sharing_apps": [],
    "device_id": "device-123"
  },
  "upi_intent": null
}
```

**Response:**
```json
{
  "message": "Dear customer, your KYC is expired...",
  "sender": "VD-KYCINF",
  "risk_level": "high",
  "risk_score": 78.5,
  "is_safe": false,
  "fraud_indicators": [
    "Fake KYC update scam detected",
    "Urgency tactics used",
    "Shortened URL used",
    "🤖 AI: Urgency tactics to pressure victim",
    "🤖 AI: Suspicious sender ID",
    "🤖 AI: Shortened URL hides destination"
  ],
  "detected_fraud_types": ["sms_scam", "phishing"],
  "extracted_urls": ["bit.ly/kyc-update"],
  "extracted_upi_ids": [],
  "extracted_phone_numbers": [],
  "recommendations": [
    "Do not click any links",
    "Banks never ask for KYC via SMS",
    "Report this number"
  ],
  "details": {
    "ai_scam_type": "fake_kyc",
    "ai_confidence": "high",
    "ai_reasoning": "Classic fake KYC scam..."
  }
}
```

---

#### POST `/analyze/transaction`
UPI Transaction Analysis with Gemini AI
```json
Method: POST
URL: http://localhost:8000/analyze/transaction
Headers: 
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN

Body (JSON):
{
  "transaction": {
    "amount": 50000,
    "recipient_upi": "9876543210@paytm",
    "recipient_name": "Customer Support",
    "transaction_note": "Urgent refund processing"
  }
}
```

**Response:**
```json
{
  "transaction": {
    "amount": 50000,
    "recipient_upi": "9876543210@paytm",
    "recipient_name": "Customer Support",
    "transaction_note": "Urgent refund processing"
  },
  "risk_level": "high",
  "risk_score": 82.0,
  "is_safe": false,
  "fraud_indicators": [
    "⚠️ NEW PAYEE: First time sending money",
    "🚨 High-risk: Large amount to NEW recipient",
    "Personal mobile UPI (10 digits before @)",
    "🤖 AI: Personal mobile UPI suspicious",
    "🤖 AI: Generic name 'Customer Support'",
    "🤖 AI: Suspicious note with urgency"
  ],
  "detected_fraud_types": ["fake_upi", "unauthorized_transaction"],
  "warnings": [
    "⛔ CRITICAL: High risk of fraud detected"
  ],
  "recommendations": [
    "Do not proceed with this transaction",
    "Verify recipient identity",
    "Contact your bank if suspicious"
  ],
  "similar_fraud_reports": 0,
  "recipient_trust_score": 18.0,
  "details": {
    "is_new_payee": true,
    "ai_recommendation": "block",
    "ai_confidence": "high",
    "ai_reasoning": "Personal UPI + generic name + urgency = scam"
  }
}
```

---

#### POST `/analyze/qr`
QR Code Analysis
```json
Method: POST
URL: http://localhost:8000/analyze/qr
Headers: 
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN

Body (JSON):
{
  "qr_code_data": "upi://pay?pa=scammer@upi&pn=Refund Department&am=5000&mode=02&cu=INR",
  "qr_type": "upi_intent",
  "source": "scanned_physical"
}
```

**Response:**
```json
{
  "qr_code_data": "upi://pay?pa=scammer@upi...",
  "qr_type": "upi_intent",
  "risk_level": "critical",
  "risk_score": 95.0,
  "is_safe": false,
  "fraud_indicators": [
    "🚨 FAKE COLLECT REQUEST: This will take money FROM you",
    "mode=02 detected (collect mode)",
    "Generic merchant name",
    "🤖 AI: Collect request scam"
  ],
  "detected_fraud_types": ["qr_code_fraud", "fake_collect_request"],
  "recommendations": [
    "⛔ DO NOT SCAN THIS QR CODE",
    "This is a collect request that will withdraw money",
    "Report to authorities"
  ],
  "upi_intent_analysis": {
    "mode": "collect",
    "payee": "scammer@upi",
    "amount": 5000
  }
}
```

---

### 3. Public Endpoints (No Auth)

#### POST `/analyze/url/public`
Public URL analysis without authentication
```json
Method: POST
URL: http://localhost:8000/analyze/url/public
Headers: 
  Content-Type: application/json

Body (JSON):
{
  "url": "https://suspicious-site.com"
}
```

---

### 4. User Endpoints (Auth Required)

#### GET `/user/me`
Get current user info
```json
Method: GET
URL: http://localhost:8000/user/me
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "user_id": "user123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

---

### 5. Learning & Feedback (Auth Required)

#### POST `/feedback`
Submit user feedback for learning
```json
Method: POST
URL: http://localhost:8000/feedback
Headers: 
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN

Body (JSON):
{
  "entity_id": "https://example.com",
  "entity_type": "url",
  "is_fraud": false,
  "feedback_type": "false_positive",
  "comments": "This is a legitimate website"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback recorded successfully",
  "action_taken": "Added to whitelist",
  "new_risk_score": 15.0
}
```

---

#### GET `/learning/metrics`
Get learning engine metrics
```json
Method: GET
URL: http://localhost:8000/learning/metrics
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "metrics": {
    "total_feedbacks": 150,
    "accuracy": 0.89,
    "false_positive_rate": 0.06,
    "false_negative_rate": 0.05
  },
  "weight_adjustments": {
    "url_risk": 1.05,
    "sms_risk": 0.95
  },
  "whitelist_size": 25,
  "blacklist_size": 42
}
```

---

#### GET `/learning/feedback-history`
Get feedback history
```json
Method: GET
URL: http://localhost:8000/learning/feedback-history?limit=50&entity_type=url
Headers: 
  Authorization: Bearer YOUR_TOKEN

Query Parameters:
  - limit: 50 (optional, default 100)
  - entity_type: url (optional, filter by type)
```

---

### 6. Agent Status (Auth Required)

#### GET `/agent/status`
Get agent status and 5-layer metrics
```json
Method: GET
URL: http://localhost:8000/agent/status
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "status": "operational",
  "goal": "Prevent users from losing money to fraud",
  "layers": {
    "policy": {
      "active_policies": ["block_high_risk", "warn_medium_risk"]
    },
    "perception": {
      "signals_processed": 1250
    },
    "reasoning": {
      "ml_models_active": true,
      "gemini_enabled": true
    },
    "action": {
      "blocks_today": 45,
      "warnings_today": 120
    },
    "learning": {
      "feedbacks_processed": 150,
      "accuracy": 0.89
    }
  }
}
```

---

### 7. Fraud Reporting (Auth Required)

#### POST `/report/fraud`
Report a fraud incident
```json
Method: POST
URL: http://localhost:8000/report/fraud
Headers: 
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN

Body (JSON):
{
  "fraud_type": "phishing",
  "entity": "https://fake-bank.com",
  "description": "Received phishing email with this link",
  "amount_lost": 0,
  "date_occurred": "2025-11-29",
  "additional_info": {
    "source": "email",
    "sender": "fake@bank.com"
  }
}
```

**Response:**
```json
{
  "report_id": "FR-2025-11-29-001",
  "status": "submitted",
  "message": "Fraud report submitted successfully",
  "next_steps": [
    "Your report will be reviewed",
    "Entity added to watchlist",
    "Contact bank if money was lost"
  ]
}
```

---

#### GET `/report/history`
Get fraud report history
```json
Method: GET
URL: http://localhost:8000/report/history?limit=20
Headers: 
  Authorization: Bearer YOUR_TOKEN

Query Parameters:
  - limit: 20 (optional)
```

---

#### GET `/report/statistics`
Get fraud statistics
```json
Method: GET
URL: http://localhost:8000/report/statistics
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "total_reports": 45,
  "by_type": {
    "phishing": 20,
    "sms_scam": 15,
    "upi_fraud": 10
  },
  "total_amount_lost": 125000,
  "reports_this_month": 12
}
```

---

### 8. Dashboard (Auth Required)

#### GET `/dashboard`
Get dashboard statistics
```json
Method: GET
URL: http://localhost:8000/dashboard
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "total_analyses": 1250,
  "high_risk_detected": 45,
  "medium_risk_detected": 120,
  "low_risk_detected": 1085,
  "fraud_prevented": 42,
  "money_saved": 2500000,
  "accuracy": 0.89,
  "last_analysis": "2025-11-29T12:00:00"
}
```

---

### 9. History (Auth Required)

#### GET `/history`
Get analysis history
```json
Method: GET
URL: http://localhost:8000/history?limit=50&analysis_type=url
Headers: 
  Authorization: Bearer YOUR_TOKEN

Query Parameters:
  - limit: 50 (optional)
  - analysis_type: url|sms|transaction (optional)
```

**Response:**
```json
{
  "total": 1250,
  "analyses": [
    {
      "analysis_id": "a123",
      "analysis_type": "url",
      "entity": "https://example.com",
      "risk_level": "low",
      "risk_score": 15.0,
      "timestamp": "2025-11-29T12:00:00",
      "is_safe": true
    }
  ]
}
```

---

### 10. Settings (Auth Required)

#### GET `/settings`
Get user settings
```json
Method: GET
URL: http://localhost:8000/settings
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "auto_block_high_risk": true,
  "notification_level": "all",
  "language": "en",
  "theme": "dark"
}
```

---

#### PUT `/settings`
Update user settings
```json
Method: PUT
URL: http://localhost:8000/settings
Headers: 
  Content-Type: application/json
  Authorization: Bearer YOUR_TOKEN

Body (JSON):
{
  "auto_block_high_risk": true,
  "notification_level": "critical_only",
  "language": "en"
}
```

---

### 11. Payee Management (Auth Required)

#### GET `/payee/info/{payee_upi}`
Get payee information and transaction history
```json
Method: GET
URL: http://localhost:8000/payee/info/9876543210@paytm
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "payee_upi": "9876543210@paytm",
  "transaction_count": 5,
  "average_amount": 2500.0,
  "total_amount": 12500.0,
  "first_transaction": "2025-10-15T10:00:00",
  "last_transaction": "2025-11-28T15:30:00",
  "is_trusted": false,
  "risk_level": "medium"
}
```

---

#### POST `/payee/trust/{payee_upi}`
Mark payee as trusted
```json
Method: POST
URL: http://localhost:8000/payee/trust/9876543210@paytm
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "success": true,
  "message": "Payee marked as trusted",
  "payee_upi": "9876543210@paytm",
  "risk_reduction": -15
}
```

---

#### GET `/payee/transactions`
Get all payee transactions
```json
Method: GET
URL: http://localhost:8000/payee/transactions?limit=50
Headers: 
  Authorization: Bearer YOUR_TOKEN

Query Parameters:
  - limit: 50 (optional)
  - payee_upi: 9876543210@paytm (optional, filter by payee)
```

**Response:**
```json
{
  "total": 125,
  "transactions": [
    {
      "transaction_id": "tx123",
      "payee_upi": "9876543210@paytm",
      "amount": 2500.0,
      "timestamp": "2025-11-28T15:30:00",
      "risk_score": 25.0,
      "was_blocked": false
    }
  ]
}
```

---

#### GET `/payee/statistics`
Get user's payee statistics
```json
Method: GET
URL: http://localhost:8000/payee/statistics
Headers: 
  Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "total_payees": 25,
  "trusted_payees": 10,
  "new_payees_this_month": 3,
  "total_transactions": 125,
  "average_transaction_amount": 3500.0,
  "highest_risk_payee": "unknown@upi"
}
```

---

## 📦 Import into Postman

### Option 1: Manual Setup
1. Create new collection named "Fraud Sentinel API"
2. Set collection variable `base_url` = `http://localhost:8000`
3. Set collection variable `token` = `YOUR_JWT_TOKEN`
4. Add each endpoint from above

### Option 2: Use Collection Variable
Add this to collection:
```json
{
  "info": {
    "name": "Fraud Sentinel API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "token",
      "value": "YOUR_JWT_TOKEN_HERE"
    }
  ]
}
```

Then use `{{base_url}}` and `{{token}}` in requests.

---

## 🧪 Testing Flow

### 1. Get Authentication Token
First, get JWT token from auth server:
```bash
POST http://localhost:3000/auth/login
Body: {"email": "user@example.com", "password": "password"}
```

Copy the `access_token` from response.

### 2. Test Health Check
```bash
GET http://localhost:8000/health
```

### 3. Test URL Analysis
```bash
POST http://localhost:8000/analyze/url
Authorization: Bearer YOUR_TOKEN
Body: {"url": "https://example.com"}
```

### 4. Test SMS Analysis
```bash
POST http://localhost:8000/analyze/sms
Authorization: Bearer YOUR_TOKEN
Body: {"message": "Test SMS", "sender": "BANK"}
```

### 5. Submit Feedback
```bash
POST http://localhost:8000/feedback
Authorization: Bearer YOUR_TOKEN
Body: {"entity_id": "https://example.com", "entity_type": "url", "is_fraud": false}
```

---

## 🔑 Quick Reference

### Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | ❌ | Health check |
| GET | `/` | ❌ | Root endpoint |
| POST | `/analyze/url` | ✅ | URL analysis with AI |
| POST | `/analyze/sms` | ✅ | SMS analysis with AI |
| POST | `/analyze/transaction` | ✅ | Transaction analysis with AI |
| POST | `/analyze/qr` | ✅ | QR code analysis |
| POST | `/analyze/url/public` | ❌ | Public URL analysis |
| GET | `/user/me` | ✅ | Get current user |
| POST | `/feedback` | ✅ | Submit feedback |
| GET | `/learning/metrics` | ✅ | Learning metrics |
| GET | `/learning/feedback-history` | ✅ | Feedback history |
| GET | `/agent/status` | ✅ | Agent status |
| POST | `/report/fraud` | ✅ | Report fraud |
| GET | `/report/history` | ✅ | Fraud reports |
| GET | `/report/statistics` | ✅ | Fraud stats |
| GET | `/dashboard` | ✅ | Dashboard stats |
| GET | `/history` | ✅ | Analysis history |
| GET | `/settings` | ✅ | Get settings |
| PUT | `/settings` | ✅ | Update settings |
| GET | `/payee/info/{upi}` | ✅ | Payee info |
| POST | `/payee/trust/{upi}` | ✅ | Trust payee |
| GET | `/payee/transactions` | ✅ | Payee transactions |
| GET | `/payee/statistics` | ✅ | Payee stats |

**Total:** 23 endpoints

---

## 🎯 Common Test Scenarios

### Scenario 1: Phishing URL Detection
```bash
POST /analyze/url
{
  "url": "https://phonepe-verify123.com",
  "domain_details": {"ssl_valid": false}
}
Expected: risk_score > 70, fraud_indicators include AI detection
```

### Scenario 2: Fake KYC SMS
```bash
POST /analyze/sms
{
  "message": "Your KYC expired. Update now or account blocked",
  "sender": "VD-BANK"
}
Expected: risk_score > 60, detected_fraud_types include "sms_scam"
```

### Scenario 3: New Payee Transaction
```bash
POST /analyze/transaction
{
  "transaction": {
    "amount": 50000,
    "recipient_upi": "9999999999@paytm",
    "recipient_name": "Unknown"
  }
}
Expected: indicators include "NEW PAYEE", risk_score > 50
```

### Scenario 4: Fake Collect Request QR
```bash
POST /analyze/qr
{
  "qr_code_data": "upi://pay?mode=02&pa=scammer@upi&am=5000"
}
Expected: risk_score > 80, detected "FAKE COLLECT REQUEST"
```

---

## 💡 Tips

1. **Authentication**: Get token from auth server first (port 3000)
2. **Gemini AI**: Works automatically if `GEMINI_ENABLED=true` in .env
3. **Rate Limiting**: Free tier = 60 Gemini requests/minute
4. **Error Handling**: All endpoints return proper error messages
5. **Logging**: Check `logs/app.log` for detailed logs

---

**Ready to test! Start with `/health` then move to analysis endpoints.** 🚀
