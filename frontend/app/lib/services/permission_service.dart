import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/material.dart';

class PermissionService {
  /// Request all necessary permissions at app startup
  static Future<Map<String, bool>> requestInitialPermissions() async {
    Map<Permission, PermissionStatus> statuses = await [
      Permission.camera,
      Permission.notification,
    ].request();

    return {
      'camera': statuses[Permission.camera]?.isGranted ?? false,
      'notification': statuses[Permission.notification]?.isGranted ?? false,
    };
  }

  /// Request SMS permissions (dangerous permission - needs user consent)
  static Future<bool> requestSmsPermissions() async {
    Map<Permission, PermissionStatus> statuses = await [
      Permission.sms,
      Permission.phone,
    ].request();

    return statuses[Permission.sms]?.isGranted == true &&
        statuses[Permission.phone]?.isGranted == true;
  }

  /// Check if SMS permissions are granted
  static Future<bool> hasSmsPermissions() async {
    return await Permission.sms.isGranted && await Permission.phone.isGranted;
  }

  /// Check if camera permission is granted
  static Future<bool> hasCameraPermission() async {
    return await Permission.camera.isGranted;
  }

  /// Check if notification permission is granted
  static Future<bool> hasNotificationPermission() async {
    return await Permission.notification.isGranted;
  }

  /// Open app settings if permission is permanently denied
  static Future<void> openAppSettings() async {
    await openAppSettings();
  }

  /// Show permission dialog with explanation
  static Future<bool> showPermissionDialog(
    BuildContext context, {
    required String title,
    required String message,
    required Function() onRequest,
  }) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Not Now'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context, true);
              await onRequest();
            },
            child: const Text('Allow'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  /// Check and request camera permission with explanation
  static Future<bool> ensureCameraPermission(BuildContext context) async {
    if (await hasCameraPermission()) return true;

    final status = await Permission.camera.status;
    if (status.isPermanentlyDenied) {
      final shouldOpen = await showPermissionDialog(
        context,
        title: 'Camera Permission Required',
        message:
            'Camera access is needed to scan QR codes for fraud detection. Please enable it in app settings.',
        onRequest: openAppSettings,
      );
      return shouldOpen;
    }

    return await showPermissionDialog(
      context,
      title: 'Camera Permission',
      message:
          'Allow PaisaGuardian to access your camera to scan QR codes and detect fraudulent payment links.',
      onRequest: () async {
        await Permission.camera.request();
      },
    );
  }

  /// Check and request SMS permission with explanation
  static Future<bool> ensureSmsPermission(BuildContext context) async {
    if (await hasSmsPermissions()) return true;

    final status = await Permission.sms.status;
    if (status.isPermanentlyDenied) {
      final shouldOpen = await showPermissionDialog(
        context,
        title: 'SMS Permission Required',
        message:
            'SMS access is needed to automatically detect fraudulent messages. Please enable it in app settings.',
        onRequest: openAppSettings,
      );
      return shouldOpen;
    }

    return await showPermissionDialog(
      context,
      title: 'SMS Protection',
      message:
          'Allow PaisaGuardian to read SMS messages to automatically detect and warn you about potential scams.',
      onRequest: () async {
        await requestSmsPermissions();
      },
    );
  }
}
