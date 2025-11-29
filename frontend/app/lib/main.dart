import 'package:flutter/material.dart';
import 'theme/theme_data.dart';
import 'screens/dashboard_screen.dart';
import 'screens/login_screen.dart';
import 'screens/manual_token_screen.dart';
import 'services/storage_service.dart';
import 'services/token_storage.dart';

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
      title: 'PaisaGuardian',
      theme: royalDarkTheme,
      home: const AuthGate(),
      routes: {
        '/login': (context) => const LoginScreen(),
        '/manual-token': (context) => const ManualTokenScreen(),
        '/dashboard': (context) => DashboardScreen(jwtToken: ''),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/dashboard') {
          // Handle dashboard route with token parameter
          final token = settings.arguments as String? ?? '';
          return MaterialPageRoute(
            builder: (context) => DashboardScreen(jwtToken: token),
          );
        }
        return null;
      },
    );
  }
}

/// Authentication gate - checks login status
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _isLoading = true;
  bool _isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    final isLoggedIn = await TokenStorage.isLoggedIn();

    setState(() {
      _isLoggedIn = isLoggedIn;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    // Navigate based on authentication status
    if (_isLoggedIn) {
      // Get the token and pass to dashboard
      return FutureBuilder<String?>(
        future: TokenStorage.getAccessToken(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }

          final token = snapshot.data ?? '';
          return DashboardScreen(jwtToken: token);
        },
      );
    } else {
      return const LoginScreen();
    }
  }
}
