import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/token_storage.dart';
import '../theme/app_theme.dart';

/// Login screen with Google OAuth
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _handleGoogleSignIn() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final success = await AuthService.signInWithGoogle();

      if (!mounted) return;

      if (success) {
        // Get the access token after successful login
        final token = await TokenStorage.getAccessToken();

        if (!mounted) return;

        // Navigate to dashboard with token
        Navigator.of(
          context,
        ).pushReplacementNamed('/dashboard', arguments: token ?? '');
      } else {
        setState(() {
          _errorMessage = 'Sign in failed. Please try again.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  /// Build logo widget with fallback to icon
  Widget _buildLogo() {
    // Try to load custom logo, fallback to icon if not found
    return Image.asset(
      'assets/images/logo.png',
      width: 120,
      height: 120,
      fit: BoxFit.contain,
      errorBuilder: (context, error, stackTrace) {
        // Fallback to icon if logo image not found
        return const Icon(
          Icons.shield_outlined,
          size: 64,
          color: AppTheme.goldAccent,
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppTheme.primaryColor,
              AppTheme.accentColor,
              const Color(0xFF1a1a2e),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Logo
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white.withOpacity(0.1),
                      border: Border.all(color: AppTheme.goldAccent, width: 3),
                    ),
                    child: ClipOval(child: _buildLogo()),
                  ),
                  const SizedBox(height: 32),

                  // App Title
                  Text(
                    'PaisaGuardian',
                    style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      letterSpacing: 1.2,
                      shadows: [
                        Shadow(
                          color: AppTheme.goldAccent.withOpacity(0.5),
                          blurRadius: 10,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Subtitle
                  Text(
                    'AI-Powered Fraud Detection',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white.withOpacity(0.7),
                      letterSpacing: 0.5,
                    ),
                  ),
                  const SizedBox(height: 48),

                  // Description
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: AppTheme.goldAccent.withOpacity(0.3),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      children: [
                        _buildFeatureItem(
                          Icons.link,
                          'URL Analysis',
                          'Detect malicious links',
                        ),
                        const SizedBox(height: 16),
                        _buildFeatureItem(
                          Icons.message,
                          'SMS Protection',
                          'Identify phishing messages',
                        ),
                        const SizedBox(height: 16),
                        _buildFeatureItem(
                          Icons.qr_code_scanner,
                          'QR Scanning',
                          'Verify QR code safety',
                        ),
                        const SizedBox(height: 16),
                        _buildFeatureItem(
                          Icons.analytics,
                          'Transaction Monitor',
                          'Real-time fraud detection',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 48),

                  // Error Message
                  if (_errorMessage != null)
                    Container(
                      padding: const EdgeInsets.all(12),
                      margin: const EdgeInsets.only(bottom: 24),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline, color: Colors.red),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _errorMessage!,
                              style: const TextStyle(color: Colors.red),
                            ),
                          ),
                        ],
                      ),
                    ),

                  // Sign In Button
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _handleGoogleSignIn,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: AppTheme.primaryColor,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        elevation: 8,
                        shadowColor: AppTheme.goldAccent.withOpacity(0.5),
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  AppTheme.primaryColor,
                                ),
                              ),
                            )
                          : Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Image.network(
                                  'https://www.google.com/favicon.ico',
                                  width: 24,
                                  height: 24,
                                  errorBuilder: (context, error, stackTrace) =>
                                      const Icon(Icons.login, size: 24),
                                ),
                                const SizedBox(width: 12),
                                const Text(
                                  'Sign in with Google',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Manual Token Login (for testing)
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed('/manual-token');
                    },
                    child: Text(
                      'Use Manual Token Login (Testing)',
                      style: TextStyle(
                        color: AppTheme.goldAccent.withOpacity(0.7),
                        fontSize: 14,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Terms
                  Text(
                    'By signing in, you agree to our Terms of Service\nand Privacy Policy',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white.withOpacity(0.5),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String description) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.goldAccent.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: AppTheme.goldAccent, size: 24),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                description,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.6),
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
