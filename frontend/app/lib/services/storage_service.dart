import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const _alertsKey = 'alerts';

  StorageService._();

  static Future<List<Map<String, dynamic>>> getAlerts() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_alertsKey) ?? [];
    return raw.map((s) => jsonDecode(s) as Map<String, dynamic>).toList();
  }

  static Future<void> addAlert(Map<String, dynamic> alert) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_alertsKey) ?? [];
    raw.insert(0, jsonEncode(alert));
    await prefs.setStringList(_alertsKey, raw);
  }

  static Future<void> removeAlert(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_alertsKey) ?? [];
    raw.removeWhere((s) {
      try {
        final m = jsonDecode(s) as Map<String, dynamic>;
        return m['id'] == id;
      } catch (_) {
        return false;
      }
    });
    await prefs.setStringList(_alertsKey, raw);
  }

  static Future<void> clearAlerts() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_alertsKey);
  }

  static Future<int> alertsCount() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_alertsKey) ?? [];
    return raw.length;
  }
}
