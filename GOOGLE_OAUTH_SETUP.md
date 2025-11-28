# 🔐 Google OAuth Setup Guide for Android

## 📋 Your Project Information

### Android App Details

- **Package Name**: `com.example.app`
- **SHA-1 Fingerprint (Debug)**: `EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2`
- **Application Type**: Android

---

## 🚀 Step-by-Step Setup in Google Cloud Console

### Step 1: Create OAuth Client ID

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project** (or create a new one named "Fraud Sentinel")
3. **Navigate to**: APIs & Services → Credentials
4. **Click**: "Create Credentials" → "OAuth client ID"

### Step 2: Configure Android OAuth Client

Fill in the form with these values:

```
Application type: Android
Name: Fraud Sentinel Android Client
Package name: com.example.app
SHA-1 certificate fingerprint: EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2
```

### Step 3: Enable Required APIs

Before OAuth works, enable these APIs in your project:

1. Go to: **APIs & Services → Library**
2. Search and **Enable**:
   - ✅ **Google+ API** (for profile info)
   - ✅ **People API** (for user data)
   - ✅ **Google Sign-In API**

### Step 4: Configure OAuth Consent Screen

1. Go to: **APIs & Services → OAuth consent screen**
2. Choose: **External** (unless you have Google Workspace)
3. Fill in required fields:
   ```
   App name: Fraud Sentinel
   User support email: your-email@gmail.com
   Developer contact: your-email@gmail.com
   ```
4. **Scopes**: Add these scopes
   - `email`
   - `profile`
   - `openid`
5. **Test users**: Add your Google email for testing
6. Click **Save and Continue**

---

## 📱 Additional OAuth Client IDs Needed

Google OAuth requires **MULTIPLE** client IDs for a complete setup:

### 1. Android Client (Already Creating) ✅

```
Type: Android
Name: Fraud Sentinel Android Client
Package: com.example.app
SHA-1: EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2
```

### 2. Web Client (For Auth Server) ⚠️ **IMPORTANT**

Your Node.js auth server needs a Web OAuth client:

```
Type: Web application
Name: Fraud Sentinel Auth Server
Authorized redirect URIs:
  - http://localhost:3000/auth/google/callback
  - http://localhost:3000/auth/callback
```

**After creating, you'll get:**

- Client ID: `123456789-abcdefghijk.apps.googleusercontent.com`
- Client Secret: `GOCSPX-abc123def456`

**⚠️ Save these! You'll need them for your auth server `.env` file**

---

## 🔧 Configure Your Auth Server

After getting the Web OAuth credentials, update your auth server:

### Create `.env` file in `backend/auth/`

```env
# Google OAuth Credentials (Web Client)
GOOGLE_CLIENT_ID=YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_WEB_CLIENT_SECRET_HERE
GOOGLE_CALLBACK_URL=http://localhost:3000/auth/google/callback

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRY=24h
REFRESH_TOKEN_EXPIRY=30d

# Frontend URL (for redirects after OAuth)
FRONTEND_URL=http://localhost:3000/frontend

# Server Port
PORT=3000
```

### Update `backend/auth/server.js`

Make sure your server uses these environment variables:

```javascript
// Load environment variables
require("dotenv").config();

const googleConfig = {
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: process.env.GOOGLE_CALLBACK_URL,
};
```

---

## 🔑 Configure Flutter App for Google Sign-In

### Step 1: Update `pubspec.yaml`

Already added! ✅ You have `google_sign_in: ^6.1.5`

### Step 2: Update Android Configuration

Create or update `android/app/src/main/res/values/strings.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Fraud Sentinel</string>
    <!-- Replace with your Web Client ID -->
    <string name="default_web_client_id">YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com</string>
</resources>
```

### Step 3: Update AndroidManifest.xml (Optional)

If using Google Sign-In plugin, add meta-data:

```xml
<application>
    <!-- Other configuration -->

    <meta-data
        android:name="com.google.android.gms.version"
        android:value="@integer/google_play_services_version" />
</application>
```

---

## 🧪 Testing Google OAuth

### Test 1: Browser-Based OAuth (Current Method)

```bash
# 1. Start auth server
cd backend/auth
npm start

# 2. Open browser
http://localhost:3000/auth/google

# 3. Sign in with Google
# You'll be redirected with token

# 4. Copy token and use in app
```

### Test 2: Flutter Google Sign-In (Future Implementation)

Once configured, you can use the `google_sign_in` package:

```dart
import 'package:google_sign_in/google_sign_in.dart';

final GoogleSignIn _googleSignIn = GoogleSignIn(
  scopes: ['email', 'profile'],
  // Add your web client ID here
  clientId: 'YOUR_WEB_CLIENT_ID.apps.googleusercontent.com',
);

// Sign in
final GoogleSignInAccount? account = await _googleSignIn.signIn();
if (account != null) {
  // Get auth token and send to your backend
  final GoogleSignInAuthentication auth = await account.authentication;
  print('ID Token: ${auth.idToken}');
}
```

---

## 📊 Summary: Client IDs You Need

| Client Type      | Purpose                    | Where to Use          |
| ---------------- | -------------------------- | --------------------- |
| **Android**      | Flutter app authentication | Google Sign-In plugin |
| **Web**          | Auth server OAuth flow     | backend/auth/.env     |
| _(Optional) iOS_ | If deploying to iOS        | iOS configuration     |

---

## 🔒 Security Notes

### For Development (localhost)

- Use `http://localhost:3000` URLs
- Use debug keystore SHA-1 (already provided above)
- Add test users in OAuth consent screen

### For Production

1. **Get Release SHA-1**:
   ```bash
   keytool -list -v -keystore /path/to/release-keystore.jks -alias release
   ```
2. **Create new OAuth client** with release SHA-1
3. **Use HTTPS** URLs (not HTTP)
4. **Secure your secrets** (use environment variables)
5. **Add production domain** to authorized redirect URIs

---

## 🐛 Troubleshooting

### Error: "redirect_uri_mismatch"

**Fix**: Add the exact callback URL to authorized redirect URIs in Google Console

### Error: "invalid_client"

**Fix**: Check that Client ID and Secret in `.env` match Google Console

### Error: "access_denied"

**Fix**: Add your email to Test Users in OAuth consent screen

### Error: "PlatformException(sign_in_failed)"

**Fix**: Verify SHA-1 matches exactly in Google Console

### Can't find debug keystore?

**Default locations**:

- Windows: `C:\Users\YOUR_USERNAME\.android\debug.keystore`
- Mac/Linux: `~/.android/debug.keystore`

---

## ✅ Checklist

- [ ] Created Google Cloud Project
- [ ] Created **Android** OAuth client ID
  - [ ] Package: `com.example.app`
  - [ ] SHA-1: `EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2`
- [ ] Created **Web** OAuth client ID
  - [ ] Added callback URL: `http://localhost:3000/auth/google/callback`
  - [ ] Saved Client ID and Secret
- [ ] Configured OAuth consent screen
  - [ ] Added app name, email
  - [ ] Added required scopes
  - [ ] Added test users
- [ ] Enabled required Google APIs
  - [ ] Google+ API
  - [ ] People API
- [ ] Created `backend/auth/.env` with credentials
- [ ] Created `android/app/src/main/res/values/strings.xml`
- [ ] Tested OAuth flow in browser
- [ ] Tested in Flutter app

---

## 📝 Quick Reference

### Your Current SHA-1 (Debug)

```
EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2
```

### Get SHA-1 Again (if needed)

```bash
# Debug keystore
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android

# Or shorter
cd ~ && keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android | grep SHA1
```

### Get Release SHA-1 (for production)

```bash
# You'll need this when building release APK
keytool -list -v -keystore /path/to/your-release-key.jks -alias your-key-alias
```

---

## 🎯 Next Steps

1. **Complete Google Console Setup** (use info above)
2. **Get your Web Client ID and Secret**
3. **Create `backend/auth/.env`** with credentials
4. **Restart auth server**: `cd backend/auth && npm start`
5. **Test OAuth flow**: Open `http://localhost:3000/auth/google`
6. **Verify** you can sign in with Google
7. **Copy token** and test in Flutter app

---

## 📞 Need Help?

**Google Console**: https://console.cloud.google.com/
**OAuth Documentation**: https://developers.google.com/identity/protocols/oauth2
**Flutter Google Sign-In**: https://pub.dev/packages/google_sign_in

**Common Issue**: If OAuth doesn't work immediately after setup, wait 5-10 minutes for Google's servers to propagate changes.

---

**You're all set!** Follow the steps above to complete your Google OAuth setup. 🚀
