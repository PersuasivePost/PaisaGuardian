# 🚀 Quick Start - Get Your App Running in 5 Minutes

## ✅ Prerequisites Check

```bash
# 1. Node.js installed?
node --version  # Should be v14+

# 2. Python installed?
python --version  # Should be 3.8+

# 3. Flutter installed?
flutter --version  # Should be 3.10+
```

---

## 🏃 5-Minute Setup

### Step 1: Start Auth Server (30 seconds)

```bash
cd backend/auth
npm install
npm start
```

**✓ Success**: You should see `Server running on port 3000`

### Step 2: Start Backend API (30 seconds)

```bash
# Open NEW terminal
cd backend/logic
pip install -r requirements.txt
python main.py
```

**✓ Success**: You should see `Uvicorn running on http://localhost:8000`

### Step 3: Get Your JWT Token (1 minute)

1. Open browser: **http://localhost:3000/auth/google**
2. Sign in with your Google account
3. You'll be redirected to a URL like:
   ```
   http://localhost:3000/frontend#token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
4. **Copy everything after `#token=`** (the JWT token)

### Step 4: Install Flutter Dependencies (1 minute)

```bash
# Open NEW terminal
cd frontend/app
flutter pub get
```

### Step 5: Run the App (2 minutes)

```bash
flutter run
```

---

## 📱 Using the App

### Login

1. App opens to **Login Screen**
2. Click **"Use Manual Token Login (Testing)"**
3. **Paste your JWT token** (from Step 3)
4. Click **"Login with Token"**
5. ✅ **You're now authenticated!**

### Test Features

- **Dashboard**: View stats, recent alerts
- **URL Analysis**: Check if a URL is malicious
  - Example: `https://suspicious-site.com`
- **SMS Analysis**: Check if a text message is phishing
  - Example: "URGENT! Your account will be locked. Click here: bit.ly/xxx"
- **QR Scanner**: Scan QR codes for safety
  - Grant camera permission when prompted
- **Transaction Analysis**: Check if a payment is fraudulent
  - Example: Payee "Unknown Store", Amount: $500

### Logout

- Tap the **logout icon** (top right)
- Confirm logout
- You're back to login screen

---

## 🔍 Verify Everything Works

### Test 1: URL Analysis

```
1. Open URL Analysis screen
2. Enter: https://google.com
3. Tap "Analyze URL"
4. ✅ Should return risk score (likely low/safe)
```

### Test 2: Check Dashboard Stats

```
1. From dashboard, look at stats cards
2. ✅ Should show: Total Scans, Threats Blocked, etc.
```

### Test 3: Logout & Login

```
1. Tap logout button
2. ✅ Should return to login screen
3. Login again with same token
4. ✅ Should load dashboard
```

---

## 🐛 Troubleshooting

### Problem: "401 Unauthorized"

**Cause**: Token expired or invalid  
**Fix**:

```bash
# Get new token
# 1. Open: http://localhost:3000/auth/google
# 2. Copy new token
# 3. Logout from app
# 4. Login with new token
```

### Problem: "Network Error"

**Cause**: Backend not running  
**Fix**:

```bash
# Check both servers are running
curl http://localhost:3000/health  # Auth server
curl http://localhost:8000/health  # Backend API

# If not, restart them (Step 1 & 2)
```

### Problem: "Token Not Saving"

**Cause**: Secure storage issue  
**Fix**:

```bash
# Uninstall and reinstall app
flutter clean
flutter run
```

### Problem: App Won't Build

**Cause**: Dependencies not installed  
**Fix**:

```bash
cd frontend/app
flutter pub get
flutter clean
flutter run
```

---

## 📊 What to Expect

### First Time Login

```
1. Login Screen appears
2. Click "Use Manual Token Login"
3. Paste token → Click Login
4. Brief loading (1-2 seconds)
5. Dashboard appears with your name
```

### Dashboard View

```
┌─────────────────────────────────┐
│ Welcome, [Your Name]!           │
│                                 │
│ ┌─────┐ ┌─────┐ ┌─────┐        │
│ │  0  │ │  0  │ │  0  │        │
│ │Scans│ │Block│ │Thret│        │
│ └─────┘ └─────┘ └─────┘        │
│                                 │
│ Quick Actions:                  │
│ [URL] [SMS] [QR] [Transaction]  │
│                                 │
│ Recent Alerts:                  │
│ (Empty - No scans yet)          │
└─────────────────────────────────┘
```

### After Running Analysis

```
Dashboard updates with:
- Total Scans: 1 ➜ 2 ➜ 3...
- New alerts appear
- Stats update in real-time
```

---

## ⏱️ Expected Timings

| Action        | Time       |
| ------------- | ---------- |
| Start servers | 1 min      |
| Get JWT token | 30 sec     |
| Install deps  | 1 min      |
| App launch    | 30 sec     |
| Login         | 5 sec      |
| URL analysis  | 2-3 sec    |
| SMS analysis  | 2-3 sec    |
| QR scan       | Instant    |
| **TOTAL**     | **~5 min** |

---

## 🎯 Quick Commands Reference

```bash
# Auth Server
cd backend/auth && npm start

# Backend API
cd backend/logic && python main.py

# Get Token
# Open: http://localhost:3000/auth/google

# Flutter App
cd frontend/app && flutter run

# Clean Build
flutter clean && flutter pub get && flutter run

# Check Errors
flutter analyze
```

---

## 🔑 Sample JWT Token (Structure)

Your token will look like this (shortened):

```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMzQ1Njc4OTAiLCJuYW1lIjoiSm9obiBEb2UiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MTUxNjMyNTQyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Parts**:

- Header: `eyJhbGci...` (algorithm)
- Payload: `eyJpZCI...` (user data)
- Signature: `SflKxw...` (verification)

**Decode** at: https://jwt.io (to see your info)

---

## 🎉 You're Done!

Your app is now **fully functional** with:

- ✅ Authentication
- ✅ Secure token storage
- ✅ All API endpoints working
- ✅ Real-time fraud detection
- ✅ QR scanning
- ✅ Transaction analysis
- ✅ SMS analysis
- ✅ URL analysis

**Enjoy your fraud detection app!** 🎊

---

## 📞 Need Help?

**Token expired too quickly?**

- Tokens last 24 hours
- Just get a new one from browser

**Want automatic OAuth?**

- Check `AUTHENTICATION_SYSTEM.md` for WebView implementation guide

**App crashes?**

- Check `flutter doctor` for issues
- Verify all dependencies installed
- Check Android/iOS permissions

---

## 🚦 Status Indicators

When app is working correctly:

**Login Screen**

- 🟢 Shows Google Sign-In button
- 🟢 Manual token link visible

**After Login**

- 🟢 Dashboard loads
- 🟢 Your name appears
- 🟢 Stats cards show zeros

**After Analysis**

- 🟢 Results appear quickly (2-3 sec)
- 🟢 Alerts saved locally
- 🟢 Stats update

**Logout**

- 🟢 Redirects to login
- 🟢 Token cleared
- 🟢 Can't access dashboard

---

## 📚 Next Steps

1. **Test all features** (URL, SMS, QR, Transaction)
2. **Read** `AUTHENTICATION_SYSTEM.md` for details
3. **Customize** UI colors in `lib/theme/`
4. **Add** more analysis types
5. **Deploy** to real device (not emulator)

---

**That's it! You're ready to detect fraud! 🛡️**
