# 🎯 Google OAuth - Quick Fill Form

Copy and paste these values directly into Google Cloud Console forms:

---

## 📱 FORM 1: Android OAuth Client ID

```
Application type: Android

Name: Fraud Sentinel Android

Package name: com.example.app

SHA-1 certificate fingerprint: EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2
```

**Click**: Create

---

## 🌐 FORM 2: Web OAuth Client ID

```
Application type: Web application

Name: Fraud Sentinel Auth Server

Authorized JavaScript origins:
  http://localhost:3000

Authorized redirect URIs:
  http://localhost:3000/auth/google/callback
  http://localhost:3000/auth/callback
```

**Click**: Create

**IMPORTANT**: After clicking create, you'll see:

```
Client ID: 123456789-xxxxxxxxxxxxx.apps.googleusercontent.com
Client Secret: GOCSPX-xxxxxxxxxxxxxxxxx
```

**Copy both** and save them! You'll need them for your `.env` file.

---

## 🔒 FORM 3: OAuth Consent Screen

### App Information

```
App name: Fraud Sentinel

User support email: [your-email@gmail.com]

App logo: [Optional - skip for now]
```

### App Domain (Optional for testing)

```
Application home page: http://localhost:3000
Application privacy policy link: [skip for now]
Application terms of service link: [skip for now]
```

### Developer Contact Information

```
Email addresses: [your-email@gmail.com]
```

**Click**: Save and Continue

### Scopes

**Click**: Add or Remove Scopes

**Select these**:

- ✅ `.../auth/userinfo.email` - See your primary Google Account email address
- ✅ `.../auth/userinfo.profile` - See your personal info, including any personal info you've made publicly available
- ✅ `openid` - Associate you with your personal info on Google

**Click**: Update → Save and Continue

### Test Users

**Click**: Add Users

**Enter your email**: your-email@gmail.com

**Click**: Add → Save and Continue

---

## ✅ After Setup Checklist

1. **Copy your Web Client ID and Secret**
2. **Open**: `backend/auth/.env.example`
3. **Replace**:
   - `YOUR_WEB_CLIENT_ID_HERE` with your actual Client ID
   - `YOUR_WEB_CLIENT_SECRET_HERE` with your actual Client Secret
4. **Save as**: `backend/auth/.env` (remove .example)
5. **Open**: `frontend/app/android/app/src/main/res/values/strings.xml`
6. **Replace**: `YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com` with your Web Client ID
7. **Restart auth server**: `cd backend/auth && npm start`
8. **Test**: Open http://localhost:3000/auth/google

---

## 🎉 Quick Test

After setup, test your OAuth:

```bash
# Terminal 1: Start auth server
cd backend/auth
npm start

# Browser: Test OAuth
# Open: http://localhost:3000/auth/google
# Sign in with Google
# You should be redirected with a token!
```

If you see a token in the URL like:

```
http://localhost:3000/frontend#token=eyJhbGciOiJSUzI1NiIsInR5cCI6...
```

**✅ SUCCESS!** Your OAuth is working!

---

## 🚨 Common Issues

### "Error 400: redirect_uri_mismatch"

**Fix**: Make sure you added `http://localhost:3000/auth/google/callback` to authorized redirect URIs

### "Error 403: access_denied"

**Fix**: Add your Gmail account to Test Users in OAuth consent screen

### "Error: invalid_client"

**Fix**: Double-check Client ID and Secret in `.env` file match Google Console exactly

---

## 📋 Files to Update

After getting credentials from Google Console:

1. **`backend/auth/.env`** ← Add Client ID & Secret
2. **`frontend/app/android/app/src/main/res/values/strings.xml`** ← Add Web Client ID

---

**That's it!** Follow this guide to complete your Google OAuth setup in under 10 minutes. 🚀
