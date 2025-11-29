# 📱 APK Build Complete!

## ✅ APK Location

Your APK has been successfully generated at:

```
frontend/app/build/app/outputs/flutter-apk/app-release.apk
```

**Full Path:**

```
C:\Users\Ashvatth\OneDrive\Desktop\AshWorks\clones\fraud-sentinel-agent\frontend\app\build\app\outputs\flutter-apk\app-release.apk
```

**Size:** 62.0 MB

---

## 📲 How to Install on Your Phone

### Option 1: USB Transfer (Recommended)

1. Connect your phone to PC via USB
2. Run this command:
   ```bash
   adb install frontend/app/build/app/outputs/flutter-apk/app-release.apk
   ```

### Option 2: File Transfer

1. Copy the APK file to your phone via:

   - USB file transfer
   - Google Drive
   - Email
   - WhatsApp to yourself
   - Bluetooth

2. On your phone:
   - Open the APK file
   - Allow "Install from Unknown Sources" if prompted
   - Tap "Install"

---

## ⚠️ Important: Before Using the App

The app needs to connect to your backend servers. You have 2 options:

### Option A: Run Servers on Your PC (Same WiFi Required)

1. **Find your PC's IP address:**

   - Open Command Prompt
   - Run: `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. **Update the app's API URLs:**

   Edit `frontend/app/lib/services/auth_service.dart`:

   ```dart
   static const String _authServerUrl = 'http://YOUR_PC_IP:3000';
   ```

   Edit `frontend/app/lib/services/api_service.dart`:

   ```dart
   // Update baseUrl to use your PC's IP
   ```

3. **Rebuild the APK:**

   ```bash
   flutter build apk --release
   ```

4. **Start your servers:**

   ```bash
   # Terminal 1
   cd backend/auth
   npm run dev

   # Terminal 2
   cd backend/logic
   python main.py
   ```

5. Make sure your phone and PC are on the **same WiFi network**

### Option B: Deploy Servers to Cloud

- Deploy auth server to Heroku, Railway, or Render
- Deploy logic server to Python hosting
- Update API URLs in app and rebuild

---

## 🔧 Quick Rebuild Script

If you need to rebuild after changing API URLs:

```bash
cd frontend/app
flutter clean
flutter build apk --release
```

The new APK will be at the same location.

---

## 📝 Current APK Details

- **Package Name:** `com.example.app`
- **Version:** `1.0.0+1`
- **Build Type:** Release
- **Size:** 62.0 MB
- **Min Android:** API 21 (Android 5.0+)
- **Target Android:** API 34

---

## 🧪 Testing the APK

1. Install the APK on your phone
2. Make sure servers are running
3. Make sure phone is on same WiFi as PC
4. Open the app
5. Try logging in with Google
6. Test fraud detection features

---

## 🚀 Next Steps

1. **Test the APK** on your phone
2. **Update API URLs** to your PC's IP (if needed)
3. **Rebuild** if you made changes
4. **Share** the APK with others for testing

---

## 💡 Pro Tips

- **Smaller APK:** Build with `flutter build apk --split-per-abi` to create separate APKs for different processor types
- **Debug Build:** Use `flutter build apk --debug` if you need to debug on device
- **Profile Build:** Use `flutter build apk --profile` for performance testing

---

**APK is ready to install! 🎉**

**Location:** `frontend\app\build\app\outputs\flutter-apk\app-release.apk`
