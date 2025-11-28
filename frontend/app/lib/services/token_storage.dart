import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Secure token storage using FlutterSecureStorage
/// Stores JWT tokens encrypted in device keychain/keystore
class TokenStorage {
  static final _storage = const FlutterSecureStorage();

  // Storage keys
  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyTokenExpiry = 'token_expiry';
  static const String _keyUserEmail = 'user_email';
  static const String _keyUserName = 'user_name';
  static const String _keyUserId = 'user_id';

  /// Save access token
  static Future<void> saveAccessToken(String token) async {
    await _storage.write(key: _keyAccessToken, value: token);
  }

  /// Get access token
  static Future<String?> getAccessToken() async {
    return await _storage.read(key: _keyAccessToken);
  }

  /// Save refresh token
  static Future<void> saveRefreshToken(String token) async {
    await _storage.write(key: _keyRefreshToken, value: token);
  }

  /// Get refresh token
  static Future<String?> getRefreshToken() async {
    return await _storage.read(key: _keyRefreshToken);
  }

  /// Save token expiry timestamp
  static Future<void> saveTokenExpiry(DateTime expiry) async {
    await _storage.write(
      key: _keyTokenExpiry,
      value: expiry.millisecondsSinceEpoch.toString(),
    );
  }

  /// Get token expiry
  static Future<DateTime?> getTokenExpiry() async {
    final expiryStr = await _storage.read(key: _keyTokenExpiry);
    if (expiryStr == null) return null;
    return DateTime.fromMillisecondsSinceEpoch(int.parse(expiryStr));
  }

  /// Check if token is expired
  static Future<bool> isTokenExpired() async {
    final expiry = await getTokenExpiry();
    if (expiry == null) return true;
    return DateTime.now().isAfter(expiry);
  }

  /// Save user info
  static Future<void> saveUserInfo({
    String? userId,
    String? email,
    String? name,
  }) async {
    if (userId != null) await _storage.write(key: _keyUserId, value: userId);
    if (email != null) await _storage.write(key: _keyUserEmail, value: email);
    if (name != null) await _storage.write(key: _keyUserName, value: name);
  }

  /// Get user ID
  static Future<String?> getUserId() async {
    return await _storage.read(key: _keyUserId);
  }

  /// Get user email
  static Future<String?> getUserEmail() async {
    return await _storage.read(key: _keyUserEmail);
  }

  /// Get user name
  static Future<String?> getUserName() async {
    return await _storage.read(key: _keyUserName);
  }

  /// Check if user is logged in
  static Future<bool> isLoggedIn() async {
    final token = await getAccessToken();
    if (token == null) return false;
    return !(await isTokenExpired());
  }

  /// Clear all tokens and user data (logout)
  static Future<void> clearAll() async {
    await _storage.deleteAll();
  }

  /// Clear only tokens (keep user data for re-login)
  static Future<void> clearTokens() async {
    await _storage.delete(key: _keyAccessToken);
    await _storage.delete(key: _keyRefreshToken);
    await _storage.delete(key: _keyTokenExpiry);
  }
}
