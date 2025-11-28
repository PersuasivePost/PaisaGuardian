import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'token_storage.dart';

/// Authentication service for Google OAuth flow
class AuthService {
  static const String _authServerUrl = 'http://localhost:3000';

  /// Sign in with Google OAuth
  /// TODO: Implement WebView-based OAuth flow
  static Future<bool> signInWithGoogle() async {
    try {
      // OAuth URL
      final oauthUrl = '$_authServerUrl/auth/google';

      // Note: This is a simplified implementation
      // In a real app, you would:
      // 1. Open WebView with OAuth URL
      // 2. Listen for redirect to callback URL
      // 3. Extract token from URL hash (#token=xxx)
      // 4. Save token to secure storage

      // For now, return false and show instructions
      debugPrint('OAuth Flow:');
      debugPrint('1. Open browser to: $oauthUrl');
      debugPrint('2. Complete Google sign-in');
      debugPrint('3. You will be redirected with token');
      debugPrint('4. Extract token from URL hash and save');

      // TODO: Implement full WebView flow using webview_flutter package
      // This is a placeholder that will be completed
      return false;
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
