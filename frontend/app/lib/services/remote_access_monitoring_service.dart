import 'package:flutter/foundation.dart';
import 'remote_access_detector.dart';
import 'notification_service.dart';
import 'storage_service.dart';
import 'dart:async';

/// Background monitoring service for remote access detection
/// Runs periodic checks and sends notifications
class RemoteAccessMonitoringService {
  static Timer? _monitoringTimer;
  static bool _isMonitoring = false;
  static RemoteAccessDetectionResult? _lastDetection;
  static final Duration _checkInterval = const Duration(minutes: 2);

  /// Start monitoring for remote access apps in the background
  static void startMonitoring() {
    if (_isMonitoring) {
      debugPrint('Remote access monitoring already running');
      return;
    }

    _isMonitoring = true;
    debugPrint('Starting remote access monitoring (every ${_checkInterval.inMinutes} minutes)');

    // Initial check
    _performCheck();

    // Schedule periodic checks
    _monitoringTimer = Timer.periodic(_checkInterval, (timer) {
      _performCheck();
    });
  }

  /// Stop monitoring
  static void stopMonitoring() {
    _monitoringTimer?.cancel();
    _monitoringTimer = null;
    _isMonitoring = false;
    debugPrint('Stopped remote access monitoring');
  }

  /// Perform a single check
  static Future<void> _performCheck() async {
    try {
      final detection = await RemoteAccessDetector.detectRemoteAccessApps();
      
      final wasDetectedBefore = _lastDetection?.isDetected ?? false;
      final isDetectedNow = detection.isDetected;
      
      // Only send notification if this is a NEW detection
      if (isDetectedNow && !wasDetectedBefore) {
        debugPrint('🚨 NEW remote access detected: ${detection.detectedApps}');
        
        // Send critical notification
        await NotificationService.showRemoteAccessAlert(
          appName: detection.detectedApps.first,
          detectedApps: detection.detectedApps,
        );
        
        // Store alert
        await StorageService.addAlert({
          'id': 'remote_access_monitor_${DateTime.now().millisecondsSinceEpoch}',
          'type': 'security',
          'title': '🚨 Remote Access Detected by Monitor',
          'summary': 'Background check found: ${detection.detectedApps.join(", ")}',
          'payload': detection.toJson(),
        });
      } else if (isDetectedNow) {
        debugPrint('Remote access still active: ${detection.detectedApps}');
      } else {
        debugPrint('No remote access detected');
      }
      
      _lastDetection = detection;
    } catch (e) {
      debugPrint('Error in remote access monitoring: $e');
    }
  }

  /// Check if monitoring is active
  static bool get isMonitoring => _isMonitoring;

  /// Get last detection result
  static RemoteAccessDetectionResult? get lastDetection => _lastDetection;

  /// Force an immediate check
  static Future<RemoteAccessDetectionResult?> forceCheck() async {
    await _performCheck();
    return _lastDetection;
  }
}
