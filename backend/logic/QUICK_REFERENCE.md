# 🛡️ Fraud Detection API - Quick Reference

## 🚀 Start in 3 Steps

```bash
# 1. Navigate to folder
cd backend/logic

# 2. Run setup & start
./start.sh

# 3. Test it works
curl http://localhost:8000/health
```

## 📡 API Endpoints (No /api prefix)

```
GET  /                      → API info
GET  /health               → Health check
POST /analyze/url          → URL fraud detection (Auth required)
POST /analyze/sms          → SMS fraud detection (Auth required)
POST /analyze/transaction  → UPI analysis (Auth required)
POST /analyze/url/public   → Public URL test (No auth)
GET  /user/me             → User info (Auth required)
```

## 🎯 What Can It Detect?

### From Chrome Extension
✓ QR codes with fake UPI intents  
✓ Brand new domains (<30 days)  
✓ Fake payment forms (password/OTP fields)  
✓ Suspicious redirect chains  
✓ Invalid SSL certificates  

### From Mobile App
✓ SMS scams (lottery, prizes)  
✓ UPI collect requests (money FROM you)  
✓ SIM card changes (SIM swap fraud)  
✓ Screen sharing apps (AnyDesk, TeamViewer)  
✓ New device usage  

## 🔥 Critical Alerts

| Alert | Meaning | Action |
|-------|---------|--------|
| 🚨 Screen sharing detected | Someone may control your device | Uninstall immediately |
| 🚨 SIM changed recently | Possible account takeover | Contact bank now |
| 🚨 UPI collect request | Money will be taken FROM you | Verify carefully |
| 🚨 Fake OTP form | Phishing attempt | Do not enter details |

## 📊 Example Request

```bash
# Test with QR code + domain info
curl -X POST http://localhost:8000/analyze/url/public \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://payment-site.com",
    "qr_code_data": "upi://collect?pa=9876543210@paytm&am=5000",
    "domain_details": {
      "creation_date": "2025-11-25",
      "ssl_valid": false
    },
    "html_content": {
      "has_otp_fields": true
    }
  }'
```

## 📝 Files You Need to Know

```
main.py                 → FastAPI app (start here)
models.py              → Request/response models
risk_scoring.py        → Fraud detection logic
auth.py                → JWT authentication
check_requirements.py  → Verify dependencies
.env                   → Configuration
SUMMARY.md            → Complete documentation
```

## 🔧 Quick Commands

```bash
# Check if everything is installed
python3 check_requirements.py

# Start server
./start.sh

# Test health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Run tests
python test_examples.py
```

## 🌐 Chrome Extension Integration

```javascript
// Analyze current page
const result = await fetch('http://localhost:8000/analyze/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    url: window.location.href,
    qr_code_data: scannedQRCode,
    domain_details: await checkDomain(),
    html_content: analyzeHTML()
  })
});

if (result.risk_level === 'critical') {
  alert('🚨 FRAUD DETECTED!');
}
```

## 📱 Android App Integration

```kotlin
// Analyze SMS with device check
val response = api.analyzeSMS(
    token = "Bearer $token",
    request = SMSAnalysisRequest(
        message = smsBody,
        sender = smsSender,
        deviceInfo = DeviceInfo(
            simChangedRecently = checkSIMChange(),
            screenSharingAppsDetected = getScreenSharingApps()
        )
    )
)

if (response.simChangeWarning != null) {
    showCriticalAlert(response.simChangeWarning)
}
```

## 🎓 Risk Levels

```
0-24   → Low      (✅ Safe)
25-49  → Medium   (⚠️ Be careful)
50-74  → High     (⚠️ Very suspicious)
75-100 → Critical (🚨 DO NOT PROCEED)
```

## 📚 Documentation

- `README.md` - Main documentation
- `QUICKSTART.md` - Getting started guide
- `ENHANCED_FEATURES.md` - Feature details
- `SUMMARY.md` - Complete overview
- `CHECKLIST.md` - Implementation checklist
- API Docs: http://localhost:8000/docs

## ✅ What's Included

✓ **2,078 lines** of Python code  
✓ **13 fraud types** detected  
✓ **7 API endpoints**  
✓ **6 new detection functions**  
✓ Chrome extension support  
✓ Mobile app support  
✓ JWT authentication  
✓ Complete documentation  

## 🆘 Troubleshooting

**Dependencies missing?**
```bash
python3 check_requirements.py
```

**Port already in use?**
```bash
uvicorn main:app --port 8001
```

**Auth server not found?**
```bash
# Update .env file
AUTH_SERVER_URL=http://localhost:3000
```

## 🎉 You're Ready!

Your fraud detection system is complete. Start protecting users from:
- Phishing websites
- QR code scams
- SMS fraud
- SIM swap attacks
- Screen sharing scams
- Fake payment forms
- And more!

**Documentation:** http://localhost:8000/docs  
**Support:** Check the detailed docs in the folder

---

**Built for fraud prevention** 🛡️
