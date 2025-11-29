import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:google_sign_in/google_sign_in.dart';
import 'token_storage.dart';

/// Authentication service for Google OAuth flow
class AuthService {
  // Use 10.0.2.2 for Android emulator to reach localhost on the host machine
  static const String _authServerUrl = 'http://10.0.2.2:3000';

  /// Sign in with Google OAuth using WebView
  static Future<bool> signInWithGoogle() async {
    try {
      // Import will be added at the top
      // For now, we need to use google_sign_in package instead of WebView
      // because WebView-based OAuth has complications on mobile

      // Using google_sign_in package for native Google Sign-In
      // IMPORTANT: The serverClientId is the Web Client ID from Google Cloud Console
      final GoogleSignIn googleSignIn = GoogleSignIn(
        scopes: ['email', 'profile'],
        serverClientId: '783551040760-t5jvr87j1haef13j748ttoilce8n5er3.apps.googleusercontent.com',
      );

      // Sign out first to ensure clean state
      await googleSignIn.signOut();

      // Trigger Google Sign-In
      final GoogleSignInAccount? account = await googleSignIn.signIn();

      if (account == null) {
        debugPrint('Google Sign-In cancelled by user');
        return false;
      }

      // Get authentication details
      final GoogleSignInAuthentication auth = await account.authentication;
      final String? idToken = auth.idToken;

      if (idToken == null) {
        debugPrint('Failed to get ID token from Google');
        return false;
      }

      // Send the ID token to our auth server for verification
      final response = await http.post(
        Uri.parse('$_authServerUrl/auth/google/verify'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'idToken': idToken,
          'email': account.email,
          'name': account.displayName,
          'picture': account.photoUrl,
        }),
      );

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

        debugPrint('Google Sign-In successful');
        return true;
      } else {
        debugPrint('Auth server returned error: ${response.statusCode}');
        debugPrint('Response body: ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('Sign in error: $e');
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
