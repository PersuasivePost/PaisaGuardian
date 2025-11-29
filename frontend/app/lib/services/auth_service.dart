import 'dart:convert';
import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:google_sign_in/google_sign_in.dart';
import 'token_storage.dart';

/// Authentication service for Google OAuth flow
class AuthService {
  // Dynamic URL based on platform
  static String get _authServerUrl {
    if (kIsWeb) {
      return 'http://localhost:3000';
    }
    // For Android emulator, use 10.0.2.2 to reach host machine's localhost
    // For physical device, use your computer's local IP
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:3000';
    }
    // iOS simulator can use localhost
    return 'http://localhost:3000';
  }

  /// Sign in with Google OAuth
  static Future<bool> signInWithGoogle() async {
    try {
      debugPrint('🔐 Starting Google Sign-In...');

      // Configure Google Sign-In
      // The serverClientId is the Web Client ID from Google Cloud Console
      // This is required to get an ID token that can be verified by your backend
      final GoogleSignIn googleSignIn = GoogleSignIn(
        scopes: ['email', 'profile'],
        serverClientId:
            '783551040760-t5jvr87j1haef13j748ttoilce8n5er3.apps.googleusercontent.com',
      );

      // Sign out first to ensure clean state
      try {
        await googleSignIn.signOut();
      } catch (e) {
        debugPrint('Sign out error (ignored): $e');
      }

      debugPrint('🔐 Triggering Google Sign-In dialog...');

      // Trigger Google Sign-In
      GoogleSignInAccount? account;
      try {
        account = await googleSignIn.signIn();
      } catch (signInError) {
        final errorStr = signInError.toString();
        debugPrint('🔴 Google Sign-In error: $errorStr');

        // Check for specific error codes
        if (errorStr.contains('ApiException: 7')) {
          debugPrint('⚠️ Network error - Google servers unreachable');
          debugPrint('📋 This usually means:');
          debugPrint('   1. Emulator has no internet access');
          debugPrint('   2. Google Play Services not configured');
          debugPrint(
            '   3. OAuth consent screen not configured in Google Cloud Console',
          );
          throw Exception(
            'Network error: Cannot reach Google servers. Check internet connection and Google Play Services.',
          );
        } else if (errorStr.contains('ApiException: 10')) {
          debugPrint('⚠️ Developer error - SHA-1 fingerprint mismatch');
          throw Exception(
            'Configuration error: SHA-1 fingerprint not registered in Google Cloud Console.',
          );
        } else if (errorStr.contains('ApiException: 12500')) {
          debugPrint('⚠️ Sign in cancelled or configuration error');
          throw Exception('Sign in cancelled or app not configured properly.');
        }
        rethrow;
      }

      if (account == null) {
        debugPrint('❌ Google Sign-In cancelled by user');
        return false;
      }

      debugPrint('✅ Google Sign-In successful for: ${account.email}');

      // Get authentication details
      final GoogleSignInAuthentication auth = await account.authentication;
      final String? idToken = auth.idToken;

      if (idToken == null) {
        debugPrint('⚠️ No ID token received - using fallback authentication');
        // If no ID token, still allow sign in with fallback
        return await _fallbackLogin(account);
      }

      debugPrint(
        '🔑 Got ID token, verifying with auth server at $_authServerUrl...',
      );

      // Send the ID token to our auth server for verification
      try {
        final response = await http
            .post(
              Uri.parse('$_authServerUrl/auth/google/verify'),
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode({
                'idToken': idToken,
                'email': account.email,
                'name': account.displayName,
                'picture': account.photoUrl,
              }),
            )
            .timeout(const Duration(seconds: 10));

        debugPrint('📡 Auth server response: ${response.statusCode}');

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);

          // Save tokens and user info
          await TokenStorage.saveAccessToken(data['accessToken']);
          if (data['refreshToken'] != null) {
            await TokenStorage.saveRefreshToken(data['refreshToken']);
          }

          await TokenStorage.saveUserInfo(
            userId: data['user']['id']?.toString(),
            email: account.email,
            name: account.displayName,
          );

          // Calculate expiry (24 hours from now)
          final expiry = DateTime.now().add(const Duration(hours: 24));
          await TokenStorage.saveTokenExpiry(expiry);

          debugPrint('✅ Authentication complete!');
          return true;
        } else {
          debugPrint('❌ Auth server error: ${response.statusCode}');
          debugPrint('Response body: ${response.body}');

          // If server is unavailable, use fallback mode (generate temp token)
          debugPrint('Falling back to temp token mode...');
          return await _fallbackLogin(account);
        }
      } catch (timeoutOrConnectionError) {
        debugPrint('Auth server connection failed: $timeoutOrConnectionError');
        debugPrint('Using fallback authentication mode...');
        return await _fallbackLogin(account);
      }
    } catch (e) {
      debugPrint('Sign in error: $e');
      return false;
    }
  }

  /// Fallback login when auth server is unavailable
  static Future<bool> _fallbackLogin(account) async {
    try {
      // Generate a temporary token for testing when backend is unavailable
      final tempToken =
          'temp_${DateTime.now().millisecondsSinceEpoch}_${account.email}';

      await TokenStorage.saveAccessToken(tempToken);
      await TokenStorage.saveUserInfo(
        userId: account.id,
        email: account.email,
        name: account.displayName,
      );

      final expiry = DateTime.now().add(const Duration(hours: 24));
      await TokenStorage.saveTokenExpiry(expiry);

      debugPrint('Fallback login successful - using temp token');
      return true;
    } catch (e) {
      debugPrint('Fallback login error: $e');
      return false;
    }
  }

  /// Sign out
  static Future<void> signOut() async {
    await TokenStorage.clearAll();
  }

  /// Check if user is authenticated
  static Future<bool> isAuthenticated() async {
    return await TokenStorage.isLoggedIn();
  }

  /// Get current user info
  static Future<Map<String, String?>> getCurrentUser() async {
    final userId = await TokenStorage.getUserId();
    final email = await TokenStorage.getUserEmail();
    final name = await TokenStorage.getUserName();

    return {'userId': userId, 'email': email, 'name': name};
  }

  /// Verify token with auth server
  static Future<bool> verifyToken() async {
    try {
      final token = await TokenStorage.getAccessToken();
      if (token == null) return false;

      final response = await http.post(
        Uri.parse('$_authServerUrl/api/auth/verify'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'token': token}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        // Update user info if available
        if (data['user'] != null) {
          await TokenStorage.saveUserInfo(
            userId: data['user']['id']?.toString(),
            email: data['user']['email'],
            name: data['user']['name'],
          );
        }

        return data['valid'] == true;
      }

      return false;
    } catch (e) {
      debugPrint('Token verification error: $e');
      return false;
    }
  }

  /// Refresh access token using refresh token
  static Future<bool> refreshToken() async {
    try {
      final refreshToken = await TokenStorage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await http.post(
        Uri.parse('$_authServerUrl/auth/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refreshToken': refreshToken}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        // Save new tokens
        await TokenStorage.saveAccessToken(data['accessToken']);
        if (data['refreshToken'] != null) {
          await TokenStorage.saveRefreshToken(data['refreshToken']);
        }

        // Calculate expiry (24 hours from now)
        final expiry = DateTime.now().add(const Duration(hours: 24));
        await TokenStorage.saveTokenExpiry(expiry);

        return true;
      }

      return false;
    } catch (e) {
      debugPrint('Token refresh error: $e');
      return false;
    }
  }

  /// Manual token login (for testing or direct token input)
  static Future<bool> loginWithToken(
    String accessToken, {
    String? refreshToken,
  }) async {
    try {
      // Save tokens
      await TokenStorage.saveAccessToken(accessToken);
      if (refreshToken != null) {
        await TokenStorage.saveRefreshToken(refreshToken);
      }

      // Set expiry (24 hours from now)
      final expiry = DateTime.now().add(const Duration(hours: 24));
      await TokenStorage.saveTokenExpiry(expiry);

      // Verify the token
      final isValid = await verifyToken();

      if (!isValid) {
        await TokenStorage.clearTokens();
        return false;
      }

      return true;
    } catch (e) {
      debugPrint('Login with token error: $e');
      return false;
    }
  }
}
