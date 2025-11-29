import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:vibration/vibration.dart';
import 'notification_service.dart';
import 'storage_service.dart';
import 'token_storage.dart';

/// SMS Monitor Service - Listens for incoming SMS and analyzes for fraud
/// Uses platform channels for native Android SMS access
class SmsMonitorService {
  static const MethodChannel _channel = MethodChannel('com.example.app/sms');
  static bool _isMonitoring = false;

  // API URL for fraud analysis
  static String get _apiBaseUrl {
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  /// Initialize the SMS monitor
  static Future<void> initialize() async {
    // Set up method channel handler for incoming SMS
    _channel.setMethodCallHandler(_handleMethodCall);
    debugPrint('📱 SMS Monitor initialized');
  }

  /// Handle incoming method calls from native code
  static Future<dynamic> _handleMethodCall(MethodCall call) async {
    switch (call.method) {
      case 'onSmsReceived':
        final Map<dynamic, dynamic> args = call.arguments;
        final sender = args['sender'] as String? ?? 'Unknown';
        final message = args['message'] as String? ?? '';
        await _onSmsReceived(sender, message);
        return null;
      default:
        throw MissingPluginException('Method ${call.method} not implemented');
    }
  }

  /// Start SMS monitoring
  static Future<bool> startMonitoring() async {
    if (_isMonitoring) {
      debugPrint('📱 SMS monitoring already active');
      return true;
    }

    try {
      if (!Platform.isAndroid) {
        debugPrint('📱 SMS monitoring only available on Android');
        _isMonitoring = true; // Still allow manual scanning
        return true;
      }

      await initialize();

      // Try to start native listener
      try {
        final bool result = await _channel.invokeMethod('startSmsListener');
        if (result) {
          debugPrint('🛡️ Native SMS listener ACTIVE');
        }
      } catch (e) {
        debugPrint('⚠️ Native SMS listener not available: $e');
        debugPrint('📱 Manual SMS scanning still available');
      }

      _isMonitoring = true;
      debugPrint('🛡️ SMS fraud monitoring ACTIVE');
      return true;
    } catch (e) {
      debugPrint('❌ Failed to start SMS monitoring: $e');
      _isMonitoring = true; // Allow manual scanning
      return true;
    }
  }

  /// Stop SMS monitoring
  static void stopMonitoring() {
    try {
      _channel.invokeMethod('stopSmsListener');
    } catch (e) {
      debugPrint('Note: Native listener stop: $e');
    }
    _isMonitoring = false;
    debugPrint('🛑 SMS monitoring stopped');
  }

  /// Check if monitoring is active
  static bool get isMonitoring => _isMonitoring;

  /// Handle incoming SMS (called from native or manually)
  static Future<void> _onSmsReceived(String sender, String body) async {
    debugPrint('📨 ============ NEW SMS RECEIVED ============');
    debugPrint('📨 From: $sender');
    debugPrint('📨 Message: $body');
    debugPrint('📨 ==========================================');

    // Quick local risk check first (instant feedback)
    final quickRisk = _quickRiskCheck(body);
    debugPrint('🔍 Quick risk assessment: $quickRisk');

    if (quickRisk != 'low') {
      // Show immediate alert for potentially risky messages
      await _showQuickAlert(sender, body, quickRisk);
    }

    // Full analysis with backend
    await _analyzeWithBackend(sender, body);
  }

  /// Quick local pattern-based risk check
  static String _quickRiskCheck(String message) {
    final lowerMessage = message.toLowerCase();

    // Critical fraud patterns
    final criticalPatterns = [
      'you won',
      'you have won',
      'lottery winner',
      'prize winner',
      'click here to claim',
      'upi blocked',
      'upi has been blocked',
      'kyc expired',
      'kyc update',
      'account blocked',
      'account suspended',
      'verify immediately',
      'urgent action required',
      'your account will be closed',
      'bank account closed',
      'otp is',
      'share otp',
      'tell otp',
      'refund of rs',
      'cashback of rs',
      'free gift',
      'click to unblock',
      'click to verify',
      'click to update',
      'paytm kyc',
      'phonepe kyc',
      'gpay kyc',
    ];

    // High risk patterns
    final highRiskPatterns = [
      'won rs',
      'won ₹',
      'lakh',
      'crore',
      'congratulations',
      'selected for',
      'lucky winner',
      'redeem now',
      'limited time',
      'act now',
      'expire today',
      'expiring soon',
      'verify your',
      'update your',
      'confirm your',
      'suspicious activity',
      'unusual activity',
    ];

    // Medium risk patterns
    final mediumRiskPatterns = [
      'click here',
      'tap here',
      'bit.ly',
      'tinyurl',
      'short.link',
      'offer',
      'discount',
      'deal',
      'limited offer',
    ];

    // Check critical patterns
    for (final pattern in criticalPatterns) {
      if (lowerMessage.contains(pattern)) {
        return 'critical';
      }
    }

    // Check high risk patterns
    for (final pattern in highRiskPatterns) {
      if (lowerMessage.contains(pattern)) {
        return 'high';
      }
    }

    // Check medium risk patterns
    for (final pattern in mediumRiskPatterns) {
      if (lowerMessage.contains(pattern)) {
        return 'medium';
      }
    }

    return 'low';
  }

  /// Show quick alert based on local analysis
  static Future<void> _showQuickAlert(
    String sender,
    String message,
    String riskLevel,
  ) async {
    await NotificationService.initialize();

    String title;
    String body;

    switch (riskLevel) {
      case 'critical':
        title = '🚨 CRITICAL FRAUD ALERT';
        body =
            'Highly suspicious SMS from $sender detected! Do NOT click any links or share OTP.';
        // Strong vibration pattern for critical
        if (await Vibration.hasVibrator()) {
          Vibration.vibrate(
            pattern: [0, 500, 200, 500, 200, 500],
            intensities: [255, 255, 255],
          );
        }
        break;
      case 'high':
        title = '⚠️ HIGH RISK SMS';
        body = 'Suspicious message from $sender. Be cautious!';
        // Medium vibration for high risk
        if (await Vibration.hasVibrator()) {
          Vibration.vibrate(pattern: [0, 300, 150, 300]);
        }
        break;
      case 'medium':
        title = '⚡ Suspicious SMS';
        body = 'Message from $sender may contain risky content.';
        // Light vibration for medium
        if (await Vibration.hasVibrator()) {
          Vibration.vibrate(duration: 200);
        }
        break;
      default:
        return; // No alert for low risk
    }

    await _showRiskNotification(title, body, riskLevel, sender, message);
  }

  /// Show risk-based notification with appropriate styling
  static Future<void> _showRiskNotification(
    String title,
    String body,
    String riskLevel,
    String sender,
    String originalMessage,
  ) async {
    await NotificationService.showFraudAlert(
      title: title,
      message: body,
      payload: jsonEncode({
        'type': 'sms_fraud',
        'risk_level': riskLevel,
        'sender': sender,
        'message': originalMessage,
      }),
    );
  }

  /// Analyze SMS with backend API for comprehensive analysis
  static Future<Map<String, dynamic>?> _analyzeWithBackend(
    String sender,
    String message,
  ) async {
    try {
      final token = await TokenStorage.getAccessToken();

      if (token == null || token.isEmpty) {
        debugPrint('⚠️ No auth token, skipping backend analysis');
        return null;
      }

      debugPrint('🔄 Sending SMS to backend for analysis...');

      final response = await http
          .post(
            Uri.parse('$_apiBaseUrl/analyze/sms'),
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
            body: jsonEncode({'sender': sender, 'message': message}),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        debugPrint('✅ Backend analysis complete');
        debugPrint('📊 Risk Score: ${result['risk_score']}');
        debugPrint('📊 Risk Level: ${result['risk_level']}');

        // Store the analysis result
        await StorageService.addAlert({
          'id': 'sms_${DateTime.now().millisecondsSinceEpoch}',
          'type': 'sms',
          'title': _getAlertTitle(result['risk_level']),
          'summary': result['explanation'] ?? 'SMS analyzed',
          'sender': sender,
          'message': message,
          'payload': result,
          'timestamp': DateTime.now().toIso8601String(),
        });

        // Show notification based on backend analysis
        final riskScore = result['risk_score'] ?? 0;
        final riskLevel = result['risk_level'] ?? 'low';

        if (riskScore >= 70 || riskLevel == 'critical' || riskLevel == 'high') {
          await _showBackendAnalysisNotification(sender, message, result);
        }

        return result;
      } else if (response.statusCode == 401) {
        debugPrint('❌ Auth error - token may be expired');
      } else {
        debugPrint('❌ Backend analysis failed: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ Backend analysis error: $e');
    }
    return null;
  }

  /// Show notification based on backend analysis
  static Future<void> _showBackendAnalysisNotification(
    String sender,
    String originalMessage,
    Map<String, dynamic> analysis,
  ) async {
    final riskLevel = analysis['risk_level'] ?? 'medium';
    final riskScore = analysis['risk_score'] ?? 50;
    final explanation =
        analysis['explanation'] ?? 'Suspicious content detected';

    String title;
    String body;

    if (riskScore >= 80 || riskLevel == 'critical') {
      title = '🚨 CRITICAL: Fraud SMS Detected!';
      body = 'From: $sender\n$explanation';
      if (await Vibration.hasVibrator()) {
        Vibration.vibrate(pattern: [0, 1000, 500, 1000, 500, 1000]);
      }
    } else if (riskScore >= 60 || riskLevel == 'high') {
      title = '⚠️ High Risk SMS Detected';
      body = 'From: $sender\nRisk: $riskScore%\n$explanation';
      if (await Vibration.hasVibrator()) {
        Vibration.vibrate(pattern: [0, 500, 200, 500]);
      }
    } else {
      title = '⚡ Suspicious SMS';
      body = 'From: $sender\nRisk: $riskScore%';
      if (await Vibration.hasVibrator()) {
        Vibration.vibrate(duration: 300);
      }
    }

    await NotificationService.showFraudAlert(
      title: title,
      message: body,
      payload: jsonEncode({
        'type': 'sms_fraud_analysis',
        'sender': sender,
        'message': originalMessage,
        'analysis': analysis,
      }),
    );
  }

  /// Get alert title based on risk level
  static String _getAlertTitle(String? riskLevel) {
    switch (riskLevel?.toLowerCase()) {
      case 'critical':
        return '🚨 CRITICAL FRAUD SMS';
      case 'high':
        return '⚠️ High Risk SMS';
      case 'medium':
        return '⚡ Suspicious SMS';
      default:
        return '📱 SMS Analyzed';
    }
  }

  /// Manually analyze an SMS (for testing or manual input)
  static Future<Map<String, dynamic>?> analyzeManually(
    String sender,
    String message,
  ) async {
    final quickRisk = _quickRiskCheck(message);

    // Show quick alert if risky
    if (quickRisk != 'low') {
      await _showQuickAlert(sender, message, quickRisk);
    }

    // Also analyze with backend
    final backendResult = await _analyzeWithBackend(sender, message);

    return backendResult ?? {'risk_level': quickRisk, 'source': 'local'};
  }

  /// Scan all SMS in inbox for fraud
  static Future<List<Map<String, dynamic>>> scanAllSms() async {
    final results = <Map<String, dynamic>>[];

    try {
      if (!Platform.isAndroid) {
        debugPrint('📱 SMS scanning only available on Android');
        return results;
      }

      // Get SMS from native code
      final List<dynamic>? messages = await _channel.invokeMethod(
        'getSmsInbox',
      );

      if (messages == null || messages.isEmpty) {
        debugPrint('📱 No SMS messages found in inbox');
        return results;
      }

      debugPrint('📱 Found ${messages.length} SMS messages to scan');

      for (final msg in messages) {
        final sender = msg['sender'] as String? ?? 'Unknown';
        final message = msg['message'] as String? ?? '';
        final date = msg['date'] as String? ?? '';

        // Quick local check
        final riskLevel = _quickRiskCheck(message);

        if (riskLevel != 'low') {
          results.add({
            'sender': sender,
            'message': message,
            'date': date,
            'risk_level': riskLevel,
          });

          // Also do backend analysis for risky messages
          _analyzeWithBackend(sender, message);
        }
      }

      debugPrint('📱 Found ${results.length} suspicious messages');
      return results;
    } catch (e) {
      debugPrint('❌ Error scanning SMS: $e');
      return results;
    }
  }

  /// Check if SMS permission is granted
  static Future<bool> checkPermission() async {
    try {
      if (!Platform.isAndroid) return true;
      return await _channel.invokeMethod('checkSmsPermission') ?? false;
    } catch (e) {
      debugPrint('⚠️ Permission check error: $e');
      return false;
    }
  }

  /// Request SMS permission
  static Future<bool> requestPermission() async {
    try {
      if (!Platform.isAndroid) return true;
      return await _channel.invokeMethod('requestSmsPermission') ?? false;
    } catch (e) {
      debugPrint('⚠️ Permission request error: $e');
      return false;
    }
  }
}
