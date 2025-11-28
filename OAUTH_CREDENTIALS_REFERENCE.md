# 📋 Google OAuth Credentials - Copy/Paste Reference

## 🎯 Your Information (Ready to Use)

### Package Name

```
com.example.app
```

### SHA-1 Fingerprint (Debug Keystore)

```
EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2
```

### Authorized Redirect URIs (for Web OAuth)

```
http://localhost:3000/auth/google/callback
http://localhost:3000/auth/callback
```

### Authorized JavaScript Origins (for Web OAuth)

```
http://localhost:3000
```

---

## 📝 What to Do in Google Cloud Console

### 1️⃣ Create Android OAuth Client

- **Type**: Android
- **Name**: Fraud Sentinel Android
- **Package**: `com.example.app`
- **SHA-1**: `EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2`

### 2️⃣ Create Web OAuth Client

- **Type**: Web application
- **Name**: Fraud Sentinel Auth Server
- **Redirect URIs**: `http://localhost:3000/auth/google/callback`
- **JavaScript Origins**: `http://localhost:3000`

**SAVE THESE** after creating:

- Client ID: `___________________________________.apps.googleusercontent.com`
- Client Secret: `___________________________________`

### 3️⃣ Configure OAuth Consent Screen

- **App name**: Fraud Sentinel
- **Support email**: Your Gmail
- **Scopes**: email, profile, openid
- **Test users**: Your Gmail

### 4️⃣ Enable APIs

- Google+ API
- People API
- Google Sign-In API

---

## 🔧 After Getting Credentials

### Update `backend/auth/.env`

```env
GOOGLE_CLIENT_ID=PASTE_YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=PASTE_YOUR_WEB_CLIENT_SECRET_HERE
GOOGLE_CALLBACK_URL=http://localhost:3000/auth/google/callback
FRONTEND_URL=http://localhost:3000/frontend
JWT_SECRET=generate-a-random-secret-key-here
PORT=3000
```

### Update `frontend/app/android/app/src/main/res/values/strings.xml`

```xml
<string name="default_web_client_id">PASTE_YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com</string>
```

---

## ✅ Test Your Setup

```bash
# 1. Start auth server
cd backend/auth
npm start

# 2. Open browser
http://localhost:3000/auth/google

# 3. Sign in with Google
# You should get redirected with token in URL
```

**Success looks like:**

```
http://localhost:3000/frontend#token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🚀 Links

- **Google Cloud Console**: https://console.cloud.google.com/
- **Credentials**: https://console.cloud.google.com/apis/credentials
- **OAuth Consent**: https://console.cloud.google.com/apis/credentials/consent
- **API Library**: https://console.cloud.google.com/apis/library

---

## 📞 Need the SHA-1 Again?

```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android | grep SHA1
```

**Result**: `EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2`

---

**Keep this file handy while setting up Google OAuth!** 📌
