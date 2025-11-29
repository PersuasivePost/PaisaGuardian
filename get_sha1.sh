#!/bin/bash

# Script to get Android Debug Keystore SHA-1 Fingerprint
# This is needed for Google Sign-In on Android

echo "=========================================="
echo "Android Debug Keystore SHA-1 Fingerprint"
echo "=========================================="
echo ""

KEYSTORE_PATH="$HOME/.android/debug.keystore"

if [ ! -f "$KEYSTORE_PATH" ]; then
    echo "❌ Debug keystore not found at: $KEYSTORE_PATH"
    echo ""
    echo "Please run your Flutter app once to generate the debug keystore:"
    echo "  flutter run"
    exit 1
fi

echo "📍 Keystore found at: $KEYSTORE_PATH"
echo ""
echo "🔑 Getting SHA-1 fingerprint..."
echo ""

keytool -list -v -keystore "$KEYSTORE_PATH" -alias androiddebugkey -storepass android -keypass android 2>/dev/null | grep "SHA1:" | head -1

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Copy the SHA-1 fingerprint above"
echo "2. Go to: https://console.cloud.google.com/"
echo "3. Navigate to: APIs & Services > Credentials"
echo "4. Create OAuth 2.0 Client ID for Android"
echo "5. Package name: com.example.app"
echo "6. Paste the SHA-1 fingerprint"
echo "7. Wait 5-10 minutes for changes to propagate"
echo "8. Run: flutter clean && flutter run"
echo ""
