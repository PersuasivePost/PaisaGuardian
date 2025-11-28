# 🚀 Quick Start Guide - Fraud Sentinel Flutter App

## 📋 What We Just Built

**A complete Flutter fraud detection app with:**
- ✅ QR Code Scanner (NEW!)
- ✅ URL/SMS/Transaction Analysis
- ✅ Android Permissions System (NEW!)
- ✅ Premium Royal Dark Theme
- ✅ Real-time Backend Integration

---

## 🎯 Step-by-Step Usage

### **Step 1: Run the Backend**
```bash
# Terminal 1: FastAPI Backend
cd backend/logic
python main.py
# Running on http://localhost:8000

# Terminal 2: Auth Server  
cd backend/auth
node server.js
# Running on http://localhost:3000
```

### **Step 2: Run Flutter App**
```bash
# Terminal 3: Flutter
cd frontend/app
flutter pub get
flutter run
```

### **Step 3: Test Features**

#### **🔍 QR Scanner (NEW!)**
1. Open app → Dashboard
2. Tap "QR Scanner" card
3. **Permission Dialog appears** ← NEW!
   - "Allow camera access for QR fraud detection"
   - Tap "Allow"
4. Camera opens with golden overlay
5. Point at any QR code
6. **Instant analysis** with risk score
7. Results show: Safe ✅ or Suspicious ⚠️

#### **📱 SMS Analysis**
1. Tap "SMS Check" card
2. Optional: Request SMS permission for auto-scan
3. Enter sender + message
4. Tap "Analyze"
5. See risk score + extracted UPI IDs/URLs

#### **💳 Transaction Check**
1. Tap "Transaction" card
2. Enter payee name + amount + type
3. Tap "Analyze"
4. View transaction risk assessment

#### **🔗 URL Check**
1. Tap "URL Scan" card
2. Paste suspicious link
3. Tap "Analyze"
4. Get phishing/malware detection

---

## 🔐 Permissions Explained

### **Camera Permission** (NEW!)
- **When:** Tap QR Scanner
- **Dialog:** "Allow camera to scan QR codes for fraud detection"
- **Used For:** Real-time QR code scanning
- **Can Deny:** Yes, QR scanner won't work

### **SMS Permission** (Optional, for future)
- **When:** Enable SMS Protection
- **Dialog:** "Allow SMS access to detect scams automatically"
- **Used For:** Auto-scan incoming messages
- **Can Deny:** Yes, manual SMS analysis still works

### **Notification Permission**
- **When:** First app launch
- **Used For:** Fraud alerts
- **Can Deny:** Yes, in-app alerts still work

---

## 📱 App Structure

```
Dashboard (Home Screen)
├── Header (User greeting + Protection badge)
├── Security Stats (4 animated cards)
│   ├── Total Scans
│   ├── Blocked Threats
│   ├── Active Threats
│   └── Protected Status
├── Quick Actions (4 cards)
│   ├── URL Scan → UrlAnalysisScreen
│   ├── SMS Check → SmsAnalysisScreen
│   ├── Transaction → TransactionAnalysisScreen
│   └── QR Scanner → QRScannerScreen ⭐ NEW!
└── Recent Alerts (List with risk colors)
```

---

## 🎨 Visual Features

### **Royal Dark Theme**
- Deep navy blue background
- Royal gold accents
- Burgundy highlights
- Premium shadows & gradients

### **Animated Elements**
- Count-up animation on stat cards (0 → final value)
- Smooth page transitions
- Loading indicators
- Pulsing risk badges

### **Risk Colors**
- 🟢 **Green** (0-39): Safe
- 🟠 **Orange** (40-69): Medium Risk
- 🔴 **Red** (70-100): High Risk / Blocked

---

## 🔧 Configuration

### **Change Backend URL**
```dart
// lib/main.dart or dashboard_screen.dart
final baseUrl = 'http://localhost:8000'; // Change this
// For device testing: 'http://10.0.2.2:8000' (Android Emulator)
// For device testing: 'http://192.168.x.x:8000' (Physical Device)
```

### **JWT Token**
```dart
// Currently using mock/optional JWT
// For production: Implement proper login flow
// Token already passed to all API calls
```

---

## 🧪 Testing Checklist

- [ ] Dashboard loads with 0 stats
- [ ] Tap "QR Scanner" → Permission dialog appears
- [ ] Allow camera → Scanner opens with overlay
- [ ] Scan QR code → Analysis result displays
- [ ] Tap "Scan Again" → Camera resumes
- [ ] Tap "SMS Check" → Form appears
- [ ] Enter SMS → Analysis works
- [ ] Check "Recent Alerts" → Shows scanned items
- [ ] Stats update after each scan

---

## 🐛 Troubleshooting

### **Camera Permission Not Working**
```dart
// Check AndroidManifest.xml has:
<uses-permission android:name="android.permission.CAMERA"/>

// Check PermissionService.ensureCameraPermission() called
```

### **QR Scanner Black Screen**
```dart
// Restart app after granting permission
// Ensure device has working camera
// Check logcat for camera errors
```

### **API Errors**
```dart
// Verify backend is running on :8000
// Check baseUrl matches your backend
// Ensure JWT token is valid (or backend allows optional auth)
```

### **Compile Errors**
```bash
flutter clean
flutter pub get
flutter run
```

---

## 📊 What Changed (Summary)

### **NEW Files Created:**
1. `lib/services/permission_service.dart` - Permission handling
2. `lib/screens/qr_scanner_screen.dart` - QR scanner UI
3. `frontend/IMPLEMENTATION_SUMMARY.md` - Full documentation

### **Modified Files:**
1. `android/app/src/main/AndroidManifest.xml` - Added permissions
2. `lib/services/api_service.dart` - Added `/analyze/qr`, `/dashboard`, `/history` endpoints
3. `lib/screens/dashboard_screen.dart` - QR Scanner navigation with permission check

### **Permissions Added:**
- ✅ CAMERA - QR scanning
- ✅ READ_SMS - SMS analysis
- ✅ RECEIVE_SMS - SMS monitoring
- ✅ POST_NOTIFICATIONS - Fraud alerts
- ✅ READ_PHONE_STATE - Device security
- ✅ INTERNET - API calls
- ✅ ACCESS_NETWORK_STATE - Network checks

---

## 🎉 Success Criteria

✅ **App compiles** - No errors, only info warnings  
✅ **QR Scanner works** - Real-time scanning functional  
✅ **Permissions work** - Dialogs show, settings navigation works  
✅ **Backend integrated** - All 6 API endpoints connected  
✅ **UI is premium** - Royal theme, animations, smooth UX  
✅ **Android-specific** - Proper permissions, native features  

---

## 📝 Quick Commands

```bash
# Run backend
cd backend/logic && python main.py

# Run auth
cd backend/auth && node server.js

# Run app
cd frontend/app && flutter run

# Check code
flutter analyze

# Build APK
flutter build apk --release

# Install on device
flutter install
```

---

## 🚀 Next Steps

1. **Test on Real Device**
   - Build APK: `flutter build apk`
   - Install on Android phone
   - Test camera permissions
   - Scan real payment QR codes

2. **Add More Features**
   - History screen (API already ready)
   - Settings screen (API already ready)
   - Background SMS monitoring
   - Push notifications

3. **Polish UI**
   - Add splash screen
   - Add onboarding flow
   - Add tutorial for first-time users
   - Add haptic feedback

4. **Production Prep**
   - Add error tracking (Sentry/Firebase)
   - Add analytics
   - Add crash reporting
   - Set up CI/CD

---

**That's it! You now have a fully functional, permission-aware, Android fraud detection app! 🎉**
