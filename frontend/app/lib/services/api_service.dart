import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);
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

  Future<Map<String, dynamic>> analyzeUrl(String url, String jwt) async {
    final uri = _build('/api/analyze/url');
    try {
      final res = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $jwt',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'url': url}),
      );
      if (res.statusCode >= 200 && res.statusCode < 300)
        return jsonDecode(res.body) as Map<String, dynamic>;
      throw ApiException(res.statusCode, res.body);
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }

  Future<Map<String, dynamic>> analyzeSms(
    String sender,
    String message,
    String jwt,
  ) async {
    final uri = _build('/api/analyze/sms');
    try {
      final res = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $jwt',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'sender': sender, 'message': message}),
      );
      if (res.statusCode >= 200 && res.statusCode < 300)
        return jsonDecode(res.body) as Map<String, dynamic>;
      throw ApiException(res.statusCode, res.body);
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
    final uri = _build('/api/analyze/transaction');
    try {
      final res = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $jwt',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'payee': payee, 'amount': amount, 'type': type}),
      );
      if (res.statusCode >= 200 && res.statusCode < 300)
        return jsonDecode(res.body) as Map<String, dynamic>;
      throw ApiException(res.statusCode, res.body);
    } on SocketException catch (e) {
      throw ApiException(-1, 'Network error: ${e.message}');
    }
  }
}
