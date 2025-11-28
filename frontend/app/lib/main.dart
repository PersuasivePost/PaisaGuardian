import 'package:flutter/material.dart';
import 'theme/theme_data.dart';
import 'screens/dashboard_screen.dart';
import 'services/storage_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Warm up local storage
  await StorageService.alertsCount();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fraud Sentinel',
      theme: royalDarkTheme,
      home: const DashboardScreen(),
    );
  }
}
