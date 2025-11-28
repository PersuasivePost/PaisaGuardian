# 🚀 Quick Start Guide

## What's Been Created

A complete FastAPI fraud detection system with the following files:

```
backend/logic/
├── main.py                 # Main FastAPI application (380+ lines)
├── models.py              # Pydantic models for requests/responses
├── auth.py                # JWT authentication with Node.js server
├── risk_scoring.py        # Fraud detection algorithms and scoring
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── __init__.py           # Package initialization
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── start.sh              # Quick start script (executable)
├── test_examples.py      # Test examples
└── README.md             # Complete documentation
```

## 🎯 Features Implemented

### ✅ Core Components
- FastAPI application with async support
- CORS middleware configured for Chrome extension and web apps
- JWT token verification connecting to Node.js auth server (localhost:3000)
- Comprehensive request/response Pydantic models
- Risk scoring system (0-100) with fraud detection algorithms

### ✅ API Endpoints
1. **Health Check**: `GET /health` - Check API and auth service status
2. **URL Analysis**: `POST /api/analyze/url` - Detect phishing and malicious URLs
3. **SMS Analysis**: `POST /api/analyze/sms` - Identify SMS scams
4. **Transaction Analysis**: `POST /api/analyze/transaction` - Assess UPI transaction risk
5. **Public URL Analysis**: `POST /api/analyze/url/public` - No auth required for testing
6. **User Info**: `GET /api/user/me` - Get authenticated user details

### ✅ Security Features
- JWT token verification via Node.js auth server
- Bearer token authentication
- Secure HTTP-only dependencies
- CORS protection with configurable origins

### ✅ Fraud Detection Capabilities

**URL Analysis:**
- HTTPS verification
- IP address detection
- URL shortener identification
- Suspicious keyword detection
- Domain legitimacy checking
- Subdomain analysis

**SMS Analysis:**
- Fraud keyword detection (lottery, prize, urgent, etc.)
- URL extraction and analysis
- UPI ID extraction
- Phone number extraction
- Sender ID verification
- Personal info request detection

**Transaction Analysis:**
- Amount risk assessment
- UPI ID pattern matching
- Name-UPI mismatch detection
- UPI provider verification
- Transaction note analysis
- Recipient trust scoring

## 🏃 How to Run

### Option 1: Using the start script (recommended)
```bash
cd backend/logic
./start.sh
```

### Option 2: Manual setup
```bash
cd backend/logic

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### Option 3: Using uvicorn directly
```bash
cd backend/logic
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing the API

### 1. Check health
```bash
curl http://localhost:8000/health
```

### 2. Test public URL analysis (no auth)
```bash
curl -X POST http://localhost:8000/api/analyze/url/public \
  -H "Content-Type: application/json" \
  -d '{"url": "http://bit.ly/suspicious-link"}'
```

### 3. Run test examples
```bash
cd backend/logic
source venv/bin/activate
python test_examples.py
```

## 📚 Access Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root**: http://localhost:8000/

## 🔐 Authentication Setup

The API expects a Node.js auth server running on `http://localhost:3000` with a token verification endpoint at `/api/auth/verify`.

**For authenticated requests:**
```bash
curl -X POST http://localhost:8000/api/analyze/url \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"url": "https://example.com"}'
```

## 🎨 Example Responses

### URL Analysis Response
```json
{
  "url": "http://bit.ly/xyz",
  "risk_level": "high",
  "risk_score": 65.0,
  "is_safe": false,
  "fraud_indicators": [
    "Non-HTTPS connection",
    "URL shortener or suspicious domain"
  ],
  "detected_fraud_types": ["phishing", "fake_website"],
  "recommendations": [
    "⚠️ CAUTION: Verify carefully before proceeding",
    "Ensure website uses HTTPS encryption",
    "Avoid clicking shortened URLs from unknown sources"
  ],
  "analysis_timestamp": "2025-11-28T10:30:00Z",
  "details": {
    "domain": "bit.ly",
    "has_https": false,
    "risk_factors": 2
  }
}
```

### SMS Analysis Response
```json
{
  "message": "Congratulations! You won 1 crore...",
  "sender": "VK-REWARD",
  "risk_level": "critical",
  "risk_score": 85.0,
  "is_safe": false,
  "fraud_indicators": [
    "Contains 1 URL(s)",
    "Contains 4 fraud-related keywords",
    "Suspicious sender ID pattern"
  ],
  "detected_fraud_types": ["sms_scam", "phishing"],
  "extracted_urls": ["http://bit.ly/win123"],
  "extracted_upi_ids": [],
  "extracted_phone_numbers": [],
  "recommendations": [
    "🚨 HIGH RISK: Do not proceed with this action",
    "Report this as potential fraud"
  ]
}
```

### Transaction Analysis Response
```json
{
  "transaction": {
    "amount": 50000.0,
    "recipient_upi": "9876543210@paytm",
    "recipient_name": "Unknown",
    "transaction_note": "urgent help"
  },
  "risk_level": "high",
  "risk_score": 70.0,
  "is_safe": false,
  "fraud_indicators": [
    "Large amount: ₹50,000.00",
    "Personal mobile number UPI",
    "Suspicious transaction note"
  ],
  "detected_fraud_types": ["fake_upi"],
  "warnings": [
    "⚠️ WARNING: Suspicious transaction detected",
    "Large transaction amount - verify recipient carefully"
  ],
  "recommendations": [
    "⚠️ CAUTION: Verify carefully before proceeding",
    "Verify recipient identity through alternate channel",
    "Consider using smaller test transaction first"
  ],
  "recipient_trust_score": 30.0
}
```

## 🔧 Configuration

Edit `.env` file to customize:
- Server host and port
- Auth server URL
- CORS origins
- Log level

## 📦 Integration Examples

### Chrome Extension
```javascript
const analyzeURL = async (url) => {
  const token = await chrome.storage.local.get('authToken');
  
  const response = await fetch('http://localhost:8000/api/analyze/url', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token.authToken}`
    },
    body: JSON.stringify({ url })
  });
  
  return await response.json();
};
```

### Android App (Kotlin with Retrofit)
```kotlin
interface FraudDetectionApi {
    @POST("api/analyze/transaction")
    suspend fun analyzeTransaction(
        @Header("Authorization") token: String,
        @Body request: TransactionAnalysisRequest
    ): TransactionAnalysisResponse
}
```

## 🎯 Next Steps

1. ✅ FastAPI backend is complete and ready
2. ⏭️ Start the Node.js auth server on port 3000
3. ⏭️ Integrate with your Chrome extension
4. ⏭️ Integrate with your Android app
5. ⏭️ Add database for fraud report tracking
6. ⏭️ Implement rate limiting
7. ⏭️ Add caching layer (Redis)
8. ⏭️ Set up monitoring and logging

## 📞 Troubleshooting

**Port already in use:**
```bash
# Change port in main.py or run:
uvicorn main:app --port 8001
```

**Auth service unreachable:**
- Ensure Node.js server is running on port 3000
- Check `auth.py` for correct URL configuration

**Import errors:**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## 📄 Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| main.py | FastAPI app with all endpoints | ~380 |
| models.py | Pydantic models | ~180 |
| auth.py | JWT authentication | ~160 |
| risk_scoring.py | Fraud detection logic | ~380 |
| config.py | Configuration management | ~40 |
| test_examples.py | Test suite | ~200 |

**Total**: ~1,400 lines of production-ready code!

## ✨ Everything is ready to use!

Your fraud detection API is complete and ready to integrate with your Chrome extension and Android app. Start the server and begin testing!
