import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';

/// Service to detect third-party remote access applications
/// running on the device (AnyDesk, TeamViewer, Chrome Remote Desktop, etc.)
class RemoteAccessDetector {
  static const MethodChannel _channel =
      MethodChannel('com.paisaguardian/remote_access');

  /// List of known remote access applications to detect
  static const List<String> _knownRemoteAccessApps = [
    'AnyDesk',
    'TeamViewer',
    'Chrome Remote Desktop',
    'Microsoft Remote Desktop',
    'VNC Viewer',
    'Splashtop',
    'LogMeIn',
    'RemotePC',
    'Zoho Assist',
    'AeroAdmin',
    'Ammyy Admin',
    'UltraViewer',
    'SupRemo',
    'RemoteView',
    'Supremo',
  ];

  /// Check if any remote access application is currently running
  /// Returns a map with detection status and list of detected apps
  static Future<RemoteAccessDetectionResult> detectRemoteAccessApps() async {
    try {
      final Map<dynamic, dynamic> result =
          await _channel.invokeMethod('detectRemoteAccess');

      final bool isDetected = result['isDetected'] as bool? ?? false;
      final List<String> detectedApps = (result['detectedApps'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          [];
      final List<String> runningProcesses =
          (result['runningProcesses'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          [];

      return RemoteAccessDetectionResult(
        isDetected: isDetected,
        detectedApps: detectedApps,
        runningProcesses: runningProcesses,
        timestamp: DateTime.now(),
      );
    } on PlatformException catch (e) {
      debugPrint('Remote access detection error: ${e.message}');
      return RemoteAccessDetectionResult(
        isDetected: false,
        detectedApps: [],
        runningProcesses: [],
        timestamp: DateTime.now(),
        error: e.message,
      );
    } catch (e) {
      debugPrint('Unexpected error in remote access detection: $e');
      return RemoteAccessDetectionResult(
        isDetected: false,
        detectedApps: [],
        runningProcesses: [],
        timestamp: DateTime.now(),
        error: e.toString(),
      );
    }
  }

  /// Check if device is currently being remotely accessed
  /// This performs a quick check and returns true if any remote access is active
  static Future<bool> isRemoteAccessActive() async {
    final result = await detectRemoteAccessApps();
    return result.isDetected;
  }

  /// Get list of known remote access applications for reference
  static List<String> getKnownRemoteAccessApps() {
    return List.unmodifiable(_knownRemoteAccessApps);
  }

  /// Start monitoring for remote access applications
  /// Returns a stream that emits detection results periodically
  static Stream<RemoteAccessDetectionResult> monitorRemoteAccess({
    Duration interval = const Duration(seconds: 30),
  }) async* {
    while (true) {
      yield await detectRemoteAccessApps();
      await Future.delayed(interval);
    }
  }
}

/// Result of remote access detection
class RemoteAccessDetectionResult {
  final bool isDetected;
  final List<String> detectedApps;
  final List<String> runningProcesses;
  final DateTime timestamp;
  final String? error;

  RemoteAccessDetectionResult({
    required this.isDetected,
    required this.detectedApps,
    required this.runningProcesses,
    required this.timestamp,
    this.error,
  });

  bool get hasError => error != null;

  /// Get a user-friendly message about the detection
  String getMessage() {
    if (hasError) {
      return 'Unable to check for remote access apps';
    }
    if (isDetected && detectedApps.isNotEmpty) {
      return 'Detected: ${detectedApps.join(", ")}';
    }
    return 'No remote access detected';
  }

  /// Get fraud risk level based on detection
  String getRiskLevel() {
    if (isDetected && detectedApps.isNotEmpty) {
      return 'CRITICAL';
    }
    return 'LOW';
  }

  Map<String, dynamic> toJson() {
    return {
      'isDetected': isDetected,
      'detectedApps': detectedApps,
      'runningProcesses': runningProcesses,
      'timestamp': timestamp.toIso8601String(),
      'error': error,
    };
  }

  @override
  String toString() {
    return 'RemoteAccessDetectionResult(isDetected: $isDetected, apps: ${detectedApps.length}, error: $error)';
  }
}
