# Google Sign-In Setup Guide

## Current Configuration

### SHA-1 Fingerprint (Debug)

```
EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2
```

### Web Client ID (for serverClientId)

```
783551040760-t5jvr87j1haef13j748ttoilce8n5er3.apps.googleusercontent.com
```

## Setup Steps

### 1. Google Cloud Console Configuration

1. Go to https://console.cloud.google.com/apis/credentials
2. Select your project (or create one)

### 2. Create Android OAuth Client ID

1. Click "Create Credentials" > "OAuth client ID"
2. Select "Android" as the application type
3. Name: "Paisa Guardian Android"
4. Package name: `com.example.app`
5. SHA-1 certificate fingerprint: `EE:85:89:EC:D4:98:2C:1B:62:DD:3B:E2:68:27:05:54:F3:C9:7E:C2`
6. Click "Create"

### 3. Verify Web Client ID

Make sure you have a Web Client ID configured:

- Type: Web application
- Authorized JavaScript origins: `http://localhost:3000`
- Authorized redirect URIs: `http://localhost:3000/auth/google/callback`

### 4. Update google-services.json (Optional)

If using Firebase, download `google-services.json` from Firebase Console and place it in:

```
frontend/app/android/app/google-services.json
```

## Testing

1. Start auth server: `cd backend/auth && node server.js`
2. Start logic server: `cd backend/logic && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
3. Run Flutter app: `cd frontend/app && flutter run`

## Troubleshooting

### "Sign in with Google" button not visible

- Fixed: Changed text color from `primaryColor` (white) to `textPrimaryColor` (dark)

### PlatformException(sign_in_failed)

- Verify SHA-1 fingerprint matches your debug keystore
- Verify Android Client ID exists in Google Cloud Console
- Make sure package name matches (`com.example.app`)

### ID Token is null

- This happens if Android Client ID is not properly configured
- App will fall back to temporary authentication mode

### Network errors connecting to auth server

- Emulator uses `10.0.2.2` to reach host's localhost
- Physical device needs your computer's actual IP address
