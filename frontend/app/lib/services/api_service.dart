import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'token_storage.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;
  final bool isAuthError; // Flag for 401 errors

  ApiException(this.statusCode, this.message, {this.isAuthError = false});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

  Uri _build(String path) {
    final base = Uri.parse(baseUrl);
    final newPath =
        (base.path.endsWith('/') ? base.path : '${base.path}') + path;
    return base.replace(path: newPath);
  }

  /// Validate JWT token before API calls
  Future<String> _validateAndGetToken(String jwt) async {
    if (jwt.isEmpty) {
      throw ApiException(
        401,
        'No authentication token available',
        isAuthError: true,
      );
    }

    // Check if token is expired
    final isExpired = await TokenStorage.isTokenExpired();
    if (isExpired) {
      throw ApiException(
        401,
        'Authentication token expired',
        isAuthError: true,
      );
    }

    return jwt;
  }

  /// Handle HTTP response and throw appropriate exceptions
  Map<String, dynamic> _handleResponse(http.Response res) {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    }

    // Handle 401 Unauthorized
    if (res.statusCode == 401) {
      throw ApiException(
        401,
        'Unauthorized: Invalid or expired token',
        isAuthError: true,
      );
    }

    // Handle other errors
    String errorMessage = res.body;
    try {
      final errorBody = jsonDecode(res.body);
      errorMessage = errorBody['detail'] ?? errorBody['message'] ?? res.body;
    } catch (_) {
      // Use raw body if JSON parsing fails
    }

    throw ApiException(res.statusCode, errorMessage);
  }

  Future<Map<String, dynamic>> analyzeUrl(String url, String jwt) async {
    final validatedJwt = await _validateAndGetToken(jwt);
    final uri = _build('/analyze/url');

    try {
      final res = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $validatedJwt',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'url': url}),
      );
      return _handleResponse(res);
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }

  Future<Map<String, dynamic>> analyzeSms(
    String sender,
    String message,
    String jwt,
  ) async {
    final validatedJwt = await _validateAndGetToken(jwt);
    final uri = _build('/analyze/sms');

    try {
      final res = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $validatedJwt',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'sender': sender, 'message': message}),
      );
      return _handleResponse(res);
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }

  Future<Map<String, dynamic>> analyzeTransaction(
    String payee,
    double amount,
    String type,
    String jwt,
  ) async {
    final validatedJwt = await _validateAndGetToken(jwt);
    final uri = _build('/analyze/transaction');

    try {
      final res = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $validatedJwt',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'payee': payee, 'amount': amount, 'type': type}),
      );
      return _handleResponse(res);
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }

  Future<Map<String, dynamic>> analyzeQR(String qrData, String jwt) async {
    final validatedJwt = await _validateAndGetToken(jwt);
    final uri = _build('/analyze/qr');

    try {
      final res = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $validatedJwt',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'qr_data': qrData}),
      );
      return _handleResponse(res);
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }

  Future<Map<String, dynamic>> getDashboardStats(String jwt) async {
    final validatedJwt = await _validateAndGetToken(jwt);
    final uri = _build('/dashboard');

    try {
      final res = await http.get(
        uri,
        headers: {'Authorization': 'Bearer $validatedJwt'},
      );
      return _handleResponse(res);
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }

  Future<List<Map<String, dynamic>>> getAnalysisHistory(String jwt) async {
    final validatedJwt = await _validateAndGetToken(jwt);
    final uri = _build('/history');

    try {
      final res = await http.get(
        uri,
        headers: {'Authorization': 'Bearer $validatedJwt'},
      );
      final data = _handleResponse(res);
      final history = data['history'] as List?;
      return history?.cast<Map<String, dynamic>>() ?? [];
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }
}
