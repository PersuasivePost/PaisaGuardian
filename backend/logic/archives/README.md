# Fraud Detection API - FastAPI Backend

A comprehensive fraud detection system built with FastAPI that analyzes URLs, SMS messages, and UPI transactions to detect potential fraud.

## 🚀 Features

- **URL Analysis**: Detect phishing websites, malicious links, and suspicious domains
- **SMS Analysis**: Identify scam messages, extract UPI IDs, URLs, and phone numbers
- **Transaction Analysis**: Assess UPI transaction risk and verify recipient details
- **JWT Authentication**: Secure API with JWT token verification via Node.js auth server
- **Risk Scoring**: Comprehensive risk scoring system (0-100) with detailed indicators
- **CORS Enabled**: Ready for Chrome extension and web app integration

## 📁 Project Structure

```
backend/logic/
├── main.py              # FastAPI application with all endpoints
├── models.py            # Pydantic request/response models
├── auth.py              # JWT authentication dependency
├── risk_scoring.py      # Risk scoring and fraud detection algorithms
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- Node.js auth server running on `http://localhost:3000`

### Setup

1. **Navigate to the logic directory**:
```bash
cd backend/logic
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 🚀 Running the Application

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

The token is verified with the Node.js auth server at `http://localhost:3000/api/auth/verify`.

## 📡 API Endpoints

### Health Check

- `GET /health` - Check API and service health
- `GET /` - Root endpoint with API info

### Analysis Endpoints (Authenticated)

#### URL Analysis
```http
POST /api/analyze/url
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://example.com/suspicious",
  "user_id": "user123",
  "context": "SMS"
}
```

Response:
```json
{
  "url": "https://example.com/suspicious",
  "risk_level": "medium",
  "risk_score": 55.0,
  "is_safe": false,
  "fraud_indicators": ["Non-HTTPS connection", "Suspicious keywords"],
  "detected_fraud_types": ["phishing"],
  "recommendations": ["⚠️ CAUTION: Verify carefully before proceeding"],
  "analysis_timestamp": "2025-11-28T10:30:00Z",
  "details": {}
}
```

#### SMS Analysis
```http
POST /api/analyze/sms
Content-Type: application/json
Authorization: Bearer <token>

{
  "message": "Congratulations! You won 1 crore. Click: bit.ly/xyz",
  "sender": "VK-REWARD",
  "user_id": "user123"
}
```

#### Transaction Analysis
```http
POST /api/analyze/transaction
Content-Type: application/json
Authorization: Bearer <token>

{
  "transaction": {
    "amount": 5000.0,
    "recipient_upi": "merchant@paytm",
    "recipient_name": "Online Store",
    "transaction_note": "Payment for order",
    "app_name": "Google Pay"
  },
  "user_id": "user123"
}
```

### Public Endpoints (No Authentication)

- `POST /api/analyze/url/public` - Public URL analysis for testing

### User Endpoints

- `GET /api/user/me` - Get current user info (requires auth)

## 🎯 Risk Levels

- **Low** (0-24): Minimal risk, appears safe
- **Medium** (25-49): Some suspicious indicators, proceed with caution
- **High** (50-74): Significant risk, verify carefully
- **Critical** (75-100): Extreme risk, do not proceed

## 🔍 Fraud Detection Features

### URL Analysis
- HTTPS verification
- IP address detection
- URL shortener identification
- Suspicious keyword detection
- Domain legitimacy check
- Subdomain analysis

### SMS Analysis
- Fraud keyword detection
- URL extraction and analysis
- UPI ID extraction
- Phone number extraction
- Sender ID verification
- Urgency pattern detection

### Transaction Analysis
- Amount risk assessment
- UPI ID pattern matching
- Name-UPI mismatch detection
- UPI provider verification
- Transaction note analysis
- Recipient trust scoring

## 🔧 Configuration

### Auth Server Configuration

Edit `auth.py` to change the auth server URL:

```python
AUTH_SERVER_URL = "http://localhost:3000"
TOKEN_VERIFY_ENDPOINT = f"{AUTH_SERVER_URL}/api/auth/verify"
```

### CORS Configuration

Edit `main.py` to modify allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "chrome-extension://*",
        # Add your origins here
    ],
    ...
)
```

## 🧪 Testing

### Test the API with curl:

```bash
# Health check
curl http://localhost:8000/health

# Public URL analysis (no auth)
curl -X POST http://localhost:8000/api/analyze/url/public \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Authenticated endpoint
curl -X POST http://localhost:8000/api/analyze/url \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"url": "https://example.com"}'
```

### Test with Python:

```python
import requests

# Get token from your auth server
token = "your-jwt-token"

# Analyze URL
response = requests.post(
    "http://localhost:8000/api/analyze/url",
    headers={"Authorization": f"Bearer {token}"},
    json={"url": "https://suspicious-site.com"}
)

print(response.json())
```

## 📝 Development

### Adding New Fraud Detection Rules

Edit `risk_scoring.py` to add new patterns:

```python
# Add to SUSPICIOUS_URL_PATTERNS
SUSPICIOUS_URL_PATTERNS = [
    r'your-pattern-here',
    # ...
]

# Add to SMS_FRAUD_KEYWORDS
SMS_FRAUD_KEYWORDS = [
    'your-keyword',
    # ...
]
```

### Adding New Endpoints

Add new routes in `main.py`:

```python
@app.post("/api/your-endpoint")
async def your_endpoint(user: TokenData = Depends(get_current_user)):
    # Your logic here
    pass
```

## 🐛 Troubleshooting

### Auth Service Not Reachable

If you see warnings about auth service:
1. Ensure Node.js auth server is running on port 3000
2. Check the auth server URL in `auth.py`
3. Verify network connectivity

### Import Errors

If you get import errors:
1. Ensure you're in the virtual environment
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version (3.9+)

### CORS Issues

If browser requests are blocked:
1. Add your origin to CORS allowed origins in `main.py`
2. Ensure credentials are enabled if needed
3. Check browser console for specific CORS errors

## 📦 Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **httpx**: Async HTTP client for auth verification

## 🤝 Integration

### Chrome Extension Integration

```javascript
// In your Chrome extension
const analyzeURL = async (url) => {
  const token = await getAuthToken(); // Your token retrieval logic
  
  const response = await fetch('http://localhost:8000/api/analyze/url', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ url })
  });
  
  return await response.json();
};
```

### Android App Integration

Use Retrofit or similar HTTP client to communicate with the API.

## 📄 License

See LICENSE file in the project root.

## 🚀 Next Steps

1. Set up the Node.js auth server
2. Configure your Chrome extension to use this API
3. Integrate with your Android app
4. Add database for fraud report tracking
5. Implement machine learning models for improved detection
6. Add rate limiting and caching
7. Set up monitoring and analytics

## 📞 Support

For issues and questions, please check the main project repository.
