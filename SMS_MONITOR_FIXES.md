# 🔧 SMS Monitor - Fixes & Testing Guide

## ✅ Fixes Applied

### 1. **Backend Endpoint Fix**

- **Issue**: Frontend was calling `/report` but backend expects `/report/fraud`
- **Fix**: Updated `api_service.dart` to use correct endpoint
- **File**: `lib/services/api_service.dart` line 209

### 2. **SMS Monitor Initialization**

- **Issue**: SMS monitor was initializing before user login (no auth token)
- **Fix**: Moved initialization to `DashboardScreen.initState()`
- **File**: `lib/screens/dashboard_screen.dart`

### 3. **Enhanced Logging**

- Added comprehensive debug logging throughout SMS monitor service
- Now you can trace exactly what's happening

### 4. **AndroidManifest Cleanup**

- Removed incorrect SMS receiver configuration
- Telephony package handles it automatically

## 🧪 Testing Steps

### Step 1: Clean Build

```bash
cd frontend/app
flutter clean
flutter pub get
flutter run
```

### Step 2: Watch Logs

Open a **separate terminal** and run:

```bash
adb logcat -s flutter:V | grep -E "SMS|Fraud|Dashboard"
```

You should see:

```
🚀 Dashboard: Initializing SMS Monitor...
🔧 Initializing SMS Monitor Service...
🔧 Base URL: http://10.0.2.2:8000
📱 Requesting SMS permissions...
📱 Permissions granted: true
🔔 Initializing notifications...
👂 Setting up SMS listener...
✅ SMS Monitor Service initialized successfully!
✅ Listening for incoming SMS...
✅ Dashboard: SMS Monitor initialized successfully
```

### Step 3: Check Permissions

```bash
# Check if SMS permissions are granted
adb shell dumpsys package com.example.app | grep -A 5 "requested permissions"
```

You should see:

```
android.permission.READ_SMS: granted=true
android.permission.RECEIVE_SMS: granted=true
```

If NOT granted:

1. Go to Android Settings → Apps → PaisaGuardian
2. Permissions → Enable SMS permissions
3. Restart the app

### Step 4: Send Test SMS

```bash
# Test HIGH RISK
adb emu sms send +919876543210 "URGENT: Your UPI account is blocked. Click here to unblock: http://fake-bank.com"
```

### Step 5: Watch for Logs

You should see in logcat:

```
========================================
📱 SMS RECEIVED!
📱 From: +919876543210
📱 Body: URGENT: Your UPI account is blocked...
========================================
🔍 Starting SMS analysis...
🔍 Running local fraud check...
🔍 Local analysis complete:
   - Suspicious: true
   - Score: 80
   - Patterns: Critical: upi blocked, Contains URL
⚠️ Suspicious SMS detected locally!
🌐 Sending to backend for AI analysis...
📢 Fraud alert sent for SMS from +919876543210
```

### Step 6: Check Notification

- Pull down notification drawer
- Should see: "🚨 HIGH RISK FRAUD DETECTED!"
- Tap to see details

## 🐛 Troubleshooting

### Issue 1: "No logs appear"

**Possible causes:**

1. SMS permissions not granted
2. App not running
3. Wrong logcat filter

**Solutions:**

```bash
# Check if app is running
adb shell ps | grep com.example.app

# Check all logs (no filter)
adb logcat -c  # Clear logs first
adb logcat | grep -i sms

# Force request permissions
adb shell pm grant com.example.app android.permission.READ_SMS
adb shell pm grant com.example.app android.permission.RECEIVE_SMS
```

### Issue 2: "SMS received but no analysis"

**Check:**

1. Is `_handleIncomingSms` being called?

   - Look for "📱 SMS RECEIVED!" in logs

2. Is local check working?

   - Look for "🔍 Starting SMS analysis..."

3. Add test print in code:

```dart
Future<void> _handleIncomingSms(SmsMessage message) async {
  print("🔥 HANDLER CALLED!"); // Add this
  debugPrint('📱 SMS RECEIVED!');
  // ...rest of code
}
```

### Issue 3: "Notification doesn't appear"

**Check:**

1. Notification permissions

```bash
adb shell dumpsys notification | grep com.example.app
```

2. Notification channel

```bash
adb shell dumpsys notification_listener
```

3. Test notification manually:

```dart
// Add this test function
Future<void> _testNotification() async {
  await _sendFraudAlert(
    sender: "TEST",
    message: "Test message",
    riskScore: 90.0,
    fraudIndicators: ["Test indicator"],
  );
}
```

### Issue 4: "Backend not responding"

**Check:**

1. Is Python backend running?

```bash
# Check if port 8000 is listening
netstat -an | grep 8000
```

2. Can emulator reach backend?

```bash
# Test from emulator
adb shell curl http://10.0.2.2:8000/health
```

3. Check backend logs:

```bash
cd backend/logic
python main.py
# Watch for incoming requests
```

### Issue 5: "Report Scam gives 404"

**Verify endpoint:**

```bash
# Test endpoint directly
curl -X POST http://localhost:8000/report/fraud \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "+919876543210",
    "entity_type": "phone_numbers",
    "fraud_category": "sms_scam"
  }'
```

Should return:

```json
{
  "success": true,
  "entity_id": "+919876543210",
  "report_count": 1,
  "blacklisted": false,
  "message": "Report recorded successfully"
}
```

## 📱 Manual Testing Checklist

- [ ] App starts successfully
- [ ] SMS permissions requested on first dashboard visit
- [ ] SMS permissions granted
- [ ] Logs show "SMS Monitor Service initialized"
- [ ] Send HIGH RISK SMS → See logs
- [ ] Notification appears
- [ ] Tap notification → Opens details
- [ ] Dashboard shows analysis in Recent Activity
- [ ] Open "Report Scam" → No 404 error
- [ ] Submit report → Success message
- [ ] Report count increments

## 🔬 Advanced Debugging

### Enable ALL Debug Logs

Add this to beginning of main.dart:

```dart
void main() async {
  debugPrint = (String? message, {int? wrapWidth}) {
    print('[DEBUG] $message');
  };

  // Rest of main...
}
```

### Capture All Telephony Events

Modify sms_monitor_service.dart:

```dart
Future<bool> initialize(String baseUrl) async {
  // ... existing code ...

  // Add this
  telephony.listenIncomingSms(
    onNewMessage: (SmsMessage message) {
      print("🔥🔥🔥 TELEPHONY CALLBACK FIRED! 🔥🔥🔥");
      _handleIncomingSms(message);
    },
    listenInBackground: true, // IMPORTANT!
  );

  return true;
}
```

### Test Without Backend

Modify `_backendAnalysis` to skip API call:

```dart
Future<void> _backendAnalysis(...) async {
  // Comment out API call, just send notification
  await _sendFraudAlert(
    sender: sender,
    message: message,
    riskScore: 90.0,
    fraudIndicators: ['Test'],
  );
}
```

## 🎯 Success Criteria

After fixes, you should see:

1. ✅ Initialization logs on dashboard load
2. ✅ SMS received logs when sending via ADB
3. ✅ Local analysis logs with suspicion score
4. ✅ Notification appears with correct details
5. ✅ Report Scam works (no 404)
6. ✅ Backend logs show `/report/fraud` request

## 📞 Need More Help?

If still not working:

1. Share full logcat output: `adb logcat > logs.txt`
2. Share backend logs
3. Share exact error messages
4. Confirm Android SDK version: `adb shell getprop ro.build.version.sdk`

---

**Quick Test Command:**

```bash
# All-in-one test
flutter clean && flutter pub get && flutter run &
sleep 10 &&
adb emu sms send +919876543210 "UPI blocked click here" &&
adb logcat -s flutter:V | head -50
```
