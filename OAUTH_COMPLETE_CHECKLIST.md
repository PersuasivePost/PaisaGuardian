# ✅ GOOGLE OAUTH SETUP - COMPLETE CHECKLIST

## 📋 Summary of What You Have

✅ **Android Package Name**: `com.example.app`  
✅ **SHA-1 Fingerprint**: `EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2`  
✅ **Template .env file**: `backend/auth/.env.example`  
✅ **strings.xml created**: `android/app/src/main/res/values/strings.xml`  
✅ **AndroidManifest.xml**: Already configured with permissions

---

## 🎯 YOUR EXACT STEPS (10 Minutes)

### STEP 1: Go to Google Cloud Console (2 min)

1. Open: **https://console.cloud.google.com/**
2. Create new project or select existing:
   - Click **"Select a project"** → **"New Project"**
   - Name: **"Fraud Sentinel"**
   - Click **"Create"**
3. Wait for project to be created

---

### STEP 2: Create Android OAuth Client (2 min)

1. In left sidebar: **APIs & Services** → **Credentials**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. If prompted "Configure consent screen":
   - Click **"Configure Consent Screen"**
   - Choose **"External"** → **"Create"**
   - Fill in:
     - App name: **Fraud Sentinel**
     - User support email: **[your Gmail]**
     - Developer email: **[your Gmail]**
   - Click **"Save and Continue"** → **"Save and Continue"** → **"Save and Continue"**
   - Click **"Back to Dashboard"**
4. Go back to **Credentials** → **"+ Create Credentials"** → **"OAuth client ID"**
5. Fill the form:

```
Application type: Android

Name: Fraud Sentinel Android

Package name: com.example.app

SHA-1 certificate fingerprint: EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2
```

6. Click **"Create"**
7. Click **"OK"** on the popup

---

### STEP 3: Create Web OAuth Client (3 min)

1. Still in **Credentials** page
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Fill the form:

```
Application type: Web application

Name: Fraud Sentinel Auth Server

Authorized JavaScript origins:
  Click "+ Add URI"
  Enter: http://localhost:3000

Authorized redirect URIs:
  Click "+ Add URI"
  Enter: http://localhost:3000/auth/google/callback
  Click "+ Add URI" again
  Enter: http://localhost:3000/auth/callback
```

4. Click **"Create"**
5. **⚠️ IMPORTANT**: You'll see a popup with:

```
Client ID: 123456789-abc123def456.apps.googleusercontent.com
Client Secret: GOCSPX-abc123def456ghi789
```

6. **COPY BOTH** and save them somewhere safe!

---

### STEP 4: Configure OAuth Consent Screen (2 min)

1. Left sidebar: **APIs & Services** → **OAuth consent screen**
2. Click **"Edit App"**
3. **Scopes** section:
   - Click **"Add or Remove Scopes"**
   - Select these 3 checkboxes:
     - ✅ `.../auth/userinfo.email`
     - ✅ `.../auth/userinfo.profile`
     - ✅ `openid`
   - Click **"Update"**
   - Click **"Save and Continue"**
4. **Test users** section:
   - Click **"+ Add Users"**
   - Enter your Gmail address
   - Click **"Add"**
   - Click **"Save and Continue"**

---

### STEP 5: Enable Required APIs (1 min)

1. Left sidebar: **APIs & Services** → **Library**
2. Search and enable these:
   - Search **"Google+ API"** → Click it → Click **"Enable"**
   - Search **"People API"** → Click it → Click **"Enable"**

---

### STEP 6: Configure Your Auth Server (2 min)

1. Open `backend/auth/.env.example` (already created for you)
2. Replace these values with your credentials from STEP 3:

```env
GOOGLE_CLIENT_ID=PASTE_YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=PASTE_YOUR_CLIENT_SECRET_HERE
```

3. **Save file as** `.env` (remove `.example`)

**Full .env file should look like:**

```env
GOOGLE_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456ghi789
GOOGLE_CALLBACK_URL=http://localhost:3000/auth/google/callback
FRONTEND_URL=http://localhost:3000/frontend
JWT_SECRET=my-super-secret-key-change-this
JWT_EXPIRY=24h
REFRESH_TOKEN_EXPIRY=30d
PORT=3000
```

4. Open `frontend/app/android/app/src/main/res/values/strings.xml`
5. Replace:

```xml
<string name="default_web_client_id">YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com</string>
```

With:

```xml
<string name="default_web_client_id">123456789-abc123def456.apps.googleusercontent.com</string>
```

(Use your actual Client ID from STEP 3)

---

## 🧪 TEST YOUR SETUP

### Test 1: Browser OAuth Flow

```bash
# Terminal 1: Start auth server
cd backend/auth
npm install  # If not installed yet
npm start

# Terminal 2: Open browser
# Go to: http://localhost:3000/auth/google
# Sign in with your Google account
# You should be redirected with a token!
```

**Success looks like:**

```
URL: http://localhost:3000/frontend#token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMzQ1...

✅ If you see this, OAuth is working!
```

### Test 2: Flutter App

```bash
# Terminal 3: Run Flutter app
cd frontend/app
flutter pub get
flutter run

# In app:
# 1. Click "Use Manual Token Login"
# 2. Paste the token from Test 1
# 3. Click "Login"
# 4. ✅ You should see the Dashboard!
```

---

## 🐛 Troubleshooting

### ❌ "Error 400: redirect_uri_mismatch"

**Problem**: Redirect URI doesn't match Google Console

**Fix**:

1. Go back to Google Console → Credentials → Your Web Client
2. Edit "Authorized redirect URIs"
3. Make sure you have exactly: `http://localhost:3000/auth/google/callback`
4. Save and wait 5 minutes

### ❌ "Error 403: access_denied"

**Problem**: Your account isn't added as test user

**Fix**:

1. Go to Google Console → OAuth consent screen
2. Scroll to "Test users"
3. Click "+ Add Users"
4. Add your Gmail address
5. Save

### ❌ "Error: invalid_client"

**Problem**: Client ID or Secret is wrong

**Fix**:

1. Go to Google Console → Credentials
2. Click on your Web client name
3. Copy the Client ID and Secret again
4. Update `backend/auth/.env`
5. Restart auth server

### ❌ Can't find .env file

**Solution**: Create it manually

```bash
cd backend/auth
cp .env.example .env
# Then edit .env with your credentials
```

---

## 📊 What You Should Have Now

### In Google Cloud Console:

- [x] Project created: "Fraud Sentinel"
- [x] Android OAuth client created
- [x] Web OAuth client created
- [x] OAuth consent screen configured
- [x] Test users added
- [x] APIs enabled (Google+, People)

### In Your Code:

- [x] `backend/auth/.env` with Client ID & Secret
- [x] `frontend/app/android/.../strings.xml` with Client ID
- [x] AndroidManifest.xml with permissions ✅
- [x] pubspec.yaml with google_sign_in ✅

---

## 🎉 Final Checklist

Before testing, verify:

- [ ] Created both Android AND Web OAuth clients
- [ ] Copied Web Client ID and Secret
- [ ] Created `backend/auth/.env` file (not .env.example)
- [ ] Added credentials to `.env`
- [ ] Updated `strings.xml` with Web Client ID
- [ ] Added your Gmail to test users
- [ ] Enabled Google+ API and People API
- [ ] Restarted auth server after .env changes

---

## 📞 Quick Links

- **Google Console**: https://console.cloud.google.com/
- **Credentials Page**: https://console.cloud.google.com/apis/credentials
- **OAuth Consent**: https://console.cloud.google.com/apis/credentials/consent
- **API Library**: https://console.cloud.google.com/apis/library

---

## 🚀 You're Ready!

After completing all steps:

1. ✅ OAuth works in browser
2. ✅ You can get JWT tokens
3. ✅ Flutter app can login
4. ✅ All API calls work

**Total Time**: ~10 minutes  
**Difficulty**: Easy (just copy/paste)

**Need help?** Check the troubleshooting section above or the detailed guides:

- `GOOGLE_OAUTH_SETUP.md` - Full technical guide
- `GOOGLE_OAUTH_QUICK_GUIDE.md` - Visual form guide
- `OAUTH_CREDENTIALS_REFERENCE.md` - Quick reference

---

**Good luck! You got this! 🎯**
