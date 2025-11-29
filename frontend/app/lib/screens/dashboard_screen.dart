import 'package:flutter/material.dart';
import '../theme/colors.dart';
import '../theme/text_styles.dart';
import '../services/storage_service.dart';
import '../services/jwt_helper.dart';
import '../services/permission_service.dart';
import '../services/token_storage.dart';
import '../services/remote_access_detector.dart';
import '../services/notification_service.dart';
import 'url_analysis_screen.dart';
import 'sms_analysis_screen.dart';
import 'transaction_analysis_screen.dart';
import 'qr_scanner_screen.dart';
import '../widgets/stat_card.dart';
import '../widgets/action_card.dart';
import '../widgets/alert_list_item.dart';
import '../widgets/remote_access_warning.dart';

class DashboardScreen extends StatefulWidget {
  final String jwtToken; // Now required
  final String? baseUrl;

  const DashboardScreen({
    super.key,
    required this.jwtToken, // Make it required
    this.baseUrl =
        'http://10.0.2.2:8000', // Android emulator uses 10.0.2.2 for host localhost
  });

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<Map<String, dynamic>> _alerts = [];
  String _name = 'Guardian';
  int _totalScans = 0;
  int _blocked = 0;
  int _threats = 0;
  bool _isProtected = true;
  RemoteAccessDetectionResult? _remoteAccessDetection;
  bool _showRemoteAccessWarning = false;

  @override
  void initState() {
    super.initState();
    _loadData();
    _startRemoteAccessMonitoring();
  }

  Future<void> _startRemoteAccessMonitoring() async {
    // Initial check
    await _checkRemoteAccess();
    
    // Periodic monitoring every 30 seconds
    Future.delayed(const Duration(seconds: 30), () {
      if (mounted) {
        _checkRemoteAccess();
        _startRemoteAccessMonitoring();
      }
    });
  }

  Future<void> _checkRemoteAccess() async {
    final detection = await RemoteAccessDetector.detectRemoteAccessApps();
    if (mounted) {
      final wasDetectedBefore = _remoteAccessDetection?.isDetected ?? false;
      final isDetectedNow = detection.isDetected;
      
      setState(() {
        _remoteAccessDetection = detection;
        if (detection.isDetected) {
          _showRemoteAccessWarning = true;
        }
      });
      
      // Send notification if this is a NEW detection (not previously detected)
      if (isDetectedNow && !wasDetectedBefore) {
        await NotificationService.showRemoteAccessAlert(
          appName: detection.detectedApps.first,
          detectedApps: detection.detectedApps,
        );
      }
      
      // Store alert if remote access detected and not already stored
      if (detection.isDetected) {
        await StorageService.addAlert({
          'id': 'remote_access_${DateTime.now().millisecondsSinceEpoch}',
          'type': 'security',
          'title': '🚨 CRITICAL: Remote Access Detected',
          'summary': 'Detected: ${detection.detectedApps.join(", ")}',
          'payload': detection.toJson(),
        });
        await _loadData(); // Reload to show new alert
      }
    }
  }

  Future<void> _loadData() async {
    final alerts = await StorageService.getAlerts();
    final payload = JwtHelper.parsePayload(widget.jwtToken);

    // Get user name from TokenStorage as fallback
    final storedName = await TokenStorage.getUserName();

    // Calculate stats
    int totalScans = alerts.length;
    int blocked = alerts.where((a) {
      final score = a['payload']?['risk_score'] ?? 0;
      return score >= 70;
    }).length;
    int threats = alerts.where((a) {
      final score = a['payload']?['risk_score'] ?? 0;
      return score >= 40;
    }).length;

    setState(() {
      _alerts = alerts;
      // Try JWT payload first, then stored user name, then default to 'User'
      _name =
          payload?['name'] ?? payload?['given_name'] ?? storedName ?? 'User';
      _totalScans = totalScans;
      _blocked = blocked;
      _threats = threats;
      _isProtected = _blocked == 0 && _threats == 0;
    });
  }

  Future<void> _clearAlerts() async {
    await StorageService.clearAlerts();
    await _loadData();
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: Text('Logout', style: TextStyle(color: AppColors.text)),
        content: Text(
          'Are you sure you want to logout?',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(
              'Cancel',
              style: TextStyle(color: AppColors.textSecondary),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: Text('Logout', style: TextStyle(color: AppColors.error)),
          ),
        ],
      ),
    );

    if (confirm == true && mounted) {
      // Clear tokens
      await TokenStorage.clearAll();

      // Navigate to login screen
      if (mounted) {
        Navigator.of(
          context,
        ).pushNamedAndRemoveUntil('/login', (route) => false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.primary,
      body: CustomScrollView(
        slivers: [
          _buildAppBar(),
          // Remote Access Banner at top
          if (_remoteAccessDetection != null && _remoteAccessDetection!.isDetected)
            SliverToBoxAdapter(
              child: RemoteAccessBanner(
                detection: _remoteAccessDetection!,
                onTap: () {
                  setState(() {
                    _showRemoteAccessWarning = !_showRemoteAccessWarning;
                  });
                },
              ),
            ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Full Remote Access Warning
                  if (_showRemoteAccessWarning && _remoteAccessDetection != null)
                    RemoteAccessWarning(
                      detection: _remoteAccessDetection!,
                      onDismiss: () {
                        setState(() {
                          _showRemoteAccessWarning = false;
                        });
                      },
                      onLearnMore: () {
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text('About Remote Access Fraud'),
                            content: const SingleChildScrollView(
                              child: Text(
                                'Scammers often trick victims into installing remote access '
                                'apps like AnyDesk or TeamViewer. Once installed, they:\n\n'
                                '1. Gain full control of your device\n'
                                '2. Access your banking apps\n'
                                '3. Transfer money without your knowledge\n'
                                '4. Steal personal information\n\n'
                                'NEVER install remote access apps at someone\'s request, '
                                'especially if they claim to be from a bank, government, '
                                'or tech support.\n\n'
                                'If you see this warning:\n'
                                '• Close the remote access app immediately\n'
                                '• Uninstall it from your device\n'
                                '• Contact your bank if you shared any details\n'
                                '• Report the scammer to authorities',
                              ),
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('Got It'),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  _buildHeader(),
                  const SizedBox(height: 24),
                  _buildSecurityStats(),
                  const SizedBox(height: 24),
                  _buildQuickActions(),
                  const SizedBox(height: 24),
                  _buildRecentAlertsHeader(),
                ],
              ),
            ),
          ),
          _buildAlertsList(),
        ],
      ),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      expandedHeight: 120,
      floating: false,
      pinned: true,
      backgroundColor: AppColors.primary,
      elevation: 0,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [AppColors.primary, AppColors.primary.withOpacity(0.8)],
            ),
          ),
        ),
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // App Logo
            _buildAppLogo(),
            const SizedBox(width: 8),
            // App Name
            Text(
              'PaisaGuardian',
              style: AppTextStyles.headline2.copyWith(
                color: AppColors.secondary,
                fontSize: 20,
              ),
            ),
          ],
        ),
      ),
      actions: [
        IconButton(
          icon: Icon(Icons.refresh, color: AppColors.secondary),
          onPressed: _loadData,
        ),
        IconButton(
          icon: Icon(Icons.delete_sweep, color: AppColors.error),
          onPressed: () async {
            await _clearAlerts();
          },
        ),
        IconButton(
          icon: Icon(Icons.logout, color: AppColors.error),
          onPressed: _handleLogout,
          tooltip: 'Logout',
        ),
      ],
    );
  }

  /// Build app logo widget with fallback to icon
  Widget _buildAppLogo() {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.secondary.withOpacity(0.1),
        border: Border.all(
          color: AppColors.secondary.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: ClipOval(
        child: Image.asset(
          'assets/images/logo.png',
          width: 32,
          height: 32,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            // Fallback to shield icon if logo not found
            return Icon(
              Icons.shield_outlined,
              size: 20,
              color: AppColors.secondary,
            );
          },
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final userName = _name.isNotEmpty ? _name : 'Guest';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppColors.tertiary.withOpacity(0.2),
            AppColors.tertiary.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.secondary.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [
                  AppColors.secondary,
                  AppColors.secondary.withOpacity(0.6),
                ],
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.secondary.withOpacity(0.3),
                  blurRadius: 15,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Icon(
              Icons.account_circle,
              size: 40,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Welcome Back,',
                  style: AppTextStyles.body2.copyWith(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  userName,
                  style: AppTextStyles.headline3.copyWith(
                    color: AppColors.text,
                    fontSize: 20,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: _isProtected ? AppColors.success : AppColors.error,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: (_isProtected ? AppColors.success : AppColors.error)
                      .withOpacity(0.3),
                  blurRadius: 10,
                  spreadRadius: 1,
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  _isProtected ? Icons.shield_outlined : Icons.warning_amber,
                  size: 16,
                  color: Colors.white,
                ),
                const SizedBox(width: 6),
                Text(
                  _isProtected ? 'Protected' : 'At Risk',
                  style: AppTextStyles.body2.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSecurityStats() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Security Overview',
          style: AppTextStyles.headline3.copyWith(
            color: AppColors.text,
            fontSize: 18,
          ),
        ),
        const SizedBox(height: 8),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 8,
          crossAxisSpacing: 8,
          childAspectRatio: 1.65,
          children: [
            StatCard(
              title: 'Total Scans',
              value: _totalScans,
              icon: Icons.analytics_outlined,
              accentColor: AppColors.secondary,
            ),
            StatCard(
              title: 'Blocked',
              value: _blocked,
              icon: Icons.block,
              accentColor: AppColors.error,
            ),
            StatCard(
              title: 'Threats',
              value: _threats,
              icon: Icons.warning_amber,
              accentColor: Colors.orange,
            ),
            StatCard(
              title: 'Protected',
              value: _isProtected ? 1 : 0,
              icon: Icons.shield_outlined,
              accentColor: AppColors.success,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildRecentAlertsHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Recent Alerts',
          style: AppTextStyles.headline3.copyWith(
            color: AppColors.text,
            fontSize: 18,
          ),
        ),
        if (_alerts.isNotEmpty)
          TextButton.icon(
            onPressed: () async {
              final confirm = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: Text(
                    'Clear All Alerts',
                    style: AppTextStyles.headline3,
                  ),
                  content: Text(
                    'Are you sure you want to clear all alerts?',
                    style: AppTextStyles.body1,
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: Text('Cancel', style: AppTextStyles.body1),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: Text(
                        'Clear',
                        style: AppTextStyles.body1.copyWith(
                          color: AppColors.error,
                        ),
                      ),
                    ),
                  ],
                ),
              );
              if (confirm == true) {
                await _clearAlerts();
              }
            },
            icon: Icon(
              Icons.clear_all,
              size: 16,
              color: AppColors.textSecondary,
            ),
            label: Text(
              'Clear All',
              style: AppTextStyles.body2.copyWith(
                color: AppColors.textSecondary,
                fontSize: 12,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildAlertsList() {
    if (_alerts.isEmpty) {
      return SliverFillRemaining(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.security,
                size: 80,
                color: AppColors.secondary.withOpacity(0.3),
              ),
              const SizedBox(height: 16),
              Text(
                'No alerts yet',
                style: AppTextStyles.headline3.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Start scanning to protect yourself',
                style: AppTextStyles.body1.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return SliverList(
      delegate: SliverChildBuilderDelegate((context, index) {
        final alert = _alerts[index];
        final payload = alert['payload'] as Map<String, dynamic>? ?? {};
        final riskScore = (payload['risk_score'] as num?)?.toDouble() ?? 0.0;
        final type = payload['type'] as String? ?? 'unknown';
        final timestampStr = alert['timestamp'] as String? ?? '';

        // Parse timestamp or use current time if parsing fails
        DateTime timestamp;
        try {
          timestamp = DateTime.parse(timestampStr);
        } catch (e) {
          timestamp = DateTime.now();
        }

        // Determine risk level
        String riskLevel;
        if (riskScore >= 70) {
          riskLevel = 'High';
        } else if (riskScore >= 40) {
          riskLevel = 'Medium';
        } else {
          riskLevel = 'Low';
        }

        // Build title and subtitle based on type
        String title;
        String subtitle;
        if (type == 'url') {
          title = 'URL Analysis';
          subtitle = payload['url'] as String? ?? 'Unknown URL';
        } else if (type == 'sms') {
          title = 'SMS Analysis';
          subtitle = 'From: ${payload['sender'] ?? 'Unknown'}';
        } else if (type == 'transaction') {
          title = 'Transaction Analysis';
          subtitle = 'To: ${payload['payee'] ?? 'Unknown'}';
        } else if (type == 'qr') {
          title = 'QR Code Analysis';
          subtitle = payload['qr_data'] as String? ?? 'QR Scan Result';
        } else {
          // Fallback: try to determine from title
          title = payload['title'] as String? ?? 'Analysis Result';
          subtitle = 'Risk Score: ${riskScore.toStringAsFixed(0)}';
        }

        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
          child: AlertListItem(
            title: title,
            subtitle: subtitle,
            riskLevel: riskLevel,
            riskScore: riskScore,
            timestamp: timestamp,
            onTap: () {
              // Show detailed alert dialog
              _showAlertDetails(payload);
            },
          ),
        );
      }, childCount: _alerts.length),
    );
  }

  Widget _buildFloatingActionButton() {
    return FloatingActionButton.extended(
      onPressed: () {
        // Default action: navigate to URL analysis
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => UrlAnalysisScreen(
              jwt: widget.jwtToken,
              baseUrl: widget.baseUrl ?? 'http://localhost:8000',
            ),
          ),
        );
      },
      backgroundColor: Colors.transparent,
      elevation: 8,
      label: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [AppColors.secondary, AppColors.secondary.withOpacity(0.8)],
          ),
          borderRadius: BorderRadius.circular(30),
          boxShadow: [
            BoxShadow(
              color: AppColors.secondary.withOpacity(0.4),
              blurRadius: 15,
              spreadRadius: 2,
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(Icons.shield_outlined, color: AppColors.primary),
            const SizedBox(width: 8),
            Text(
              'Quick Scan',
              style: AppTextStyles.button.copyWith(
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAlertDetails(Map<String, dynamic> payload) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.info_outline, color: AppColors.secondary),
            const SizedBox(width: 8),
            Text('Alert Details', style: AppTextStyles.headline3),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: payload.entries.map((e) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      e.key.toUpperCase(),
                      style: AppTextStyles.body2.copyWith(
                        color: AppColors.secondary,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text('${e.value}', style: AppTextStyles.body1),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close', style: AppTextStyles.button),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    final baseUrl = widget.baseUrl ?? 'http://10.0.2.2:8000';
    final jwt = widget.jwtToken;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: AppTextStyles.headline3.copyWith(
            color: AppColors.text,
            fontSize: 18,
          ),
        ),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.2,
          children: [
            ActionCard(
              title: 'URL Scan',
              subtitle: 'Analyze suspicious links',
              icon: Icons.link,
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        UrlAnalysisScreen(jwt: jwt, baseUrl: baseUrl),
                  ),
                );
              },
            ),
            ActionCard(
              title: 'SMS Check',
              subtitle: 'Verify text messages',
              icon: Icons.sms,
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        SmsAnalysisScreen(jwt: jwt, baseUrl: baseUrl),
                  ),
                );
              },
            ),
            ActionCard(
              title: 'Transaction',
              subtitle: 'Analyze payments',
              icon: Icons.swap_horiz,
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        TransactionAnalysisScreen(jwt: jwt, baseUrl: baseUrl),
                  ),
                );
              },
            ),
            ActionCard(
              title: 'QR Scanner',
              subtitle: 'Scan QR codes',
              icon: Icons.qr_code_scanner,
              onTap: () async {
                // Request camera permission before navigating
                final hasPermission =
                    await PermissionService.ensureCameraPermission(context);
                if (!hasPermission) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                          'Camera permission is required to scan QR codes',
                        ),
                      ),
                    );
                  }
                  return;
                }

                if (mounted) {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          QRScannerScreen(jwt: jwt, baseUrl: baseUrl),
                    ),
                  );
                }
              },
            ),
          ],
        ),
      ],
    );
  }

  // Old methods below are unused and can be removed
  /*
  Widget _buildGreeting() {
    return Row(
      children: [
        CircleAvatar(
          radius: 28,
          backgroundColor: AppColors.tertiary,
          child: Text(
            _name.isNotEmpty ? _name[0].toUpperCase() : 'A',
            style: AppTextStyles.headline3,
          ),
        ),
        SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Welcome', style: AppTextStyles.body2),
            Text(_name, style: AppTextStyles.headline2),
            if (_email.isNotEmpty) Text(_email, style: AppTextStyles.body2),
          ],
        ),
      ],
    );
  }

  Widget _buildLocalStats() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _statCard('Alerts', _alerts.length.toString(), AppColors.secondary),
        _statCard('Recent', '—', AppColors.tertiary),
        _statCard('Stored', _alerts.length.toString(), AppColors.success),
      ],
    );
  }

  Widget _statCard(String title, String value, Color accent) {
    return Expanded(
      child: Container(
        margin: EdgeInsets.only(right: 8),
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.secondary.withOpacity(0.08)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: AppTextStyles.body2),
            SizedBox(height: 6),
            Text(value, style: AppTextStyles.headline2.copyWith(color: accent)),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => UrlAnalysisScreen(
                  baseUrl: 'https://your-backend.example.com',
                  jwt: widget.jwtToken ?? '',
                ),
              ),
            );
          },
          icon: Icon(Icons.link, color: AppColors.primary),
          label: Text('URL', style: AppTextStyles.button),
        ),
        SizedBox(width: 8),
        ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => SmsAnalysisScreen(
                  baseUrl: 'https://your-backend.example.com',
                  jwt: widget.jwtToken ?? '',
                ),
              ),
            );
          },
          icon: Icon(Icons.sms, color: AppColors.primary),
          label: Text('SMS', style: AppTextStyles.button),
        ),
        SizedBox(width: 8),
        ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => TransactionAnalysisScreen(
                  baseUrl: 'https://your-backend.example.com',
                  jwt: widget.jwtToken ?? '',
                ),
              ),
            );
          },
          icon: Icon(Icons.swap_horiz, color: AppColors.primary),
          label: Text('Transaction', style: AppTextStyles.button),
        ),
      ],
    );
  }

  Widget _buildAlertHistory() {
    if (_alerts.isEmpty) {
      return Center(child: Text('No alerts yet', style: AppTextStyles.body1));
    }

    return ListView.separated(
      itemCount: _alerts.length,
      separatorBuilder: (_, __) => SizedBox(height: 8),
      itemBuilder: (context, i) {
        final a = _alerts[i];
        return Container(
          padding: EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.secondary.withOpacity(0.06)),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(a['title'] ?? 'Alert', style: AppTextStyles.headline3),
                    SizedBox(height: 6),
                    Text(a['summary'] ?? '', style: AppTextStyles.body2),
                  ],
                ),
              ),
              Column(
                children: [
                  IconButton(
                    icon: Icon(Icons.delete, color: AppColors.error),
                    onPressed: () async {
                      await StorageService.removeAlert(a['id']);
                      await _loadData();
                    },
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
  */
}
