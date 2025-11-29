import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/token_storage.dart';
import '../services/remote_access_detector.dart';
import '../services/notification_service.dart';
import '../theme/text_styles.dart';
import '../theme/colors.dart';
import '../services/storage_service.dart';
import '../widgets/remote_access_warning.dart';

class TransactionAnalysisScreen extends StatefulWidget {
  final String baseUrl;
  final String jwt;

  const TransactionAnalysisScreen({
    super.key,
    required this.baseUrl,
    required this.jwt,
  });

  @override
  State<TransactionAnalysisScreen> createState() =>
      _TransactionAnalysisScreenState();
}

class _TransactionAnalysisScreenState extends State<TransactionAnalysisScreen> {
  final _payee = TextEditingController();
  final _amount = TextEditingController();
  String _type = 'transfer';
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _result;
  RemoteAccessDetectionResult? _remoteAccessDetection;
  bool _showRemoteAccessWarning = false;

  @override
  void initState() {
    super.initState();
    _checkRemoteAccess();
  }

  Future<void> _checkRemoteAccess() async {
    final detection = await RemoteAccessDetector.detectRemoteAccessApps();
    setState(() {
      _remoteAccessDetection = detection;
      _showRemoteAccessWarning = detection.isDetected;
    });
    
    // Send notification and store alert if remote access detected
    if (detection.isDetected) {
      await NotificationService.showRemoteAccessAlert(
        appName: detection.detectedApps.first,
        detectedApps: detection.detectedApps,
      );
      
      await StorageService.addAlert({
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'type': 'security',
        'title': 'Remote Access Detected',
        'summary': 'Detected apps: ${detection.detectedApps.join(", ")}',
        'payload': detection.toJson(),
      });
    }
  }

  Color _getRiskColor(String riskLevel) {
    switch (riskLevel.toLowerCase()) {
      case 'low':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'high':
        return Colors.red;
      case 'critical':
        return Colors.red.shade900;
      default:
        return Colors.grey;
    }
  }

  Future<void> _run() async {
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });
    try {
      final api = ApiService(widget.baseUrl);
      final amount = double.tryParse(_amount.text.trim()) ?? 0.0;
      final res = await api.analyzeTransaction(
        _payee.text.trim(),
        amount,
        _type,
        widget.jwt,
      );
      setState(() => _result = res);
      // store locally
      await StorageService.addAlert({
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'type': 'transaction',
        'title': 'Transaction Analysis',
        'summary': res['explanation'] ?? res.toString(),
        'payload': res,
      });
    } on ApiException catch (apiErr) {
      // Handle auth errors - redirect to login
      if (apiErr.isAuthError && mounted) {
        await TokenStorage.clearAll();
        if (mounted) {
          Navigator.of(
            context,
          ).pushNamedAndRemoveUntil('/login', (route) => false);
        }
        return;
      }
      setState(() => _error = apiErr.toString());
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Transaction Analysis', style: AppTextStyles.headline3),
      ),
      body: Column(
        children: [
          // Remote Access Warning Banner
          if (_remoteAccessDetection != null)
            RemoteAccessBanner(
              detection: _remoteAccessDetection!,
              onTap: () {
                setState(() {
                  _showRemoteAccessWarning = !_showRemoteAccessWarning;
                });
              },
            ),
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
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
                          // Could open a dialog or navigate to info screen
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
                                  'or tech support.',
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
                    TextField(
                      controller: _payee,
                      decoration: InputDecoration(hintText: 'Payee'),
                    ),
                    SizedBox(height: 8),
                    TextField(
                      controller: _amount,
                      decoration: InputDecoration(hintText: 'Amount'),
                      keyboardType: TextInputType.number,
                    ),
                    SizedBox(height: 8),
                    DropdownButton<String>(
                      value: _type,
                      onChanged: (v) => setState(() => _type = v ?? _type),
                      items: [
                        DropdownMenuItem(value: 'transfer', child: Text('Transfer')),
                        DropdownMenuItem(value: 'payment', child: Text('Payment')),
                        DropdownMenuItem(
                          value: 'withdrawal',
                          child: Text('Withdrawal'),
                        ),
                      ],
                    ),
                    SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _loading ? null : _run,
                      child: _loading ? CircularProgressIndicator() : Text('Analyze'),
                    ),
                    if (_error != null) ...[
                      SizedBox(height: 12),
                      Text(
                        'Error: ' + _error!,
                        style: TextStyle(color: AppColors.error),
                      ),
                    ],
                    if (_result != null) ...[
                      SizedBox(height: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Risk Level Card
                          Card(
                            color: _getRiskColor(_result!['risk_level'] ?? 'low'),
                            child: Padding(
                              padding: EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Risk Level: ${(_result!['risk_level'] ?? 'unknown').toString().toUpperCase()}',
                                    style: AppTextStyles.headline2.copyWith(
                                      color: Colors.white,
                                    ),
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    'Risk Score: ${(_result!['risk_score']?.toStringAsFixed(1) ?? 'N/A')}/100',
                                    style: AppTextStyles.body1.copyWith(
                                      color: Colors.white,
                                    ),
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    _result!['is_safe'] == true
                                        ? '✓ Safe Transaction'
                                        : '⚠ Suspicious Transaction',
                                    style: AppTextStyles.body2.copyWith(
                                      color: Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                      // Fraud Indicators
                      if (_result!['fraud_indicators'] != null &&
                          (_result!['fraud_indicators'] as List)
                              .isNotEmpty) ...[
                        SizedBox(height: 16),
                        Text(
                          '⚠️ Fraud Indicators:',
                          style: AppTextStyles.headline3,
                        ),
                        SizedBox(height: 8),
                        ...(_result!['fraud_indicators'] as List)
                            .map(
                              (indicator) => Padding(
                                padding: EdgeInsets.only(bottom: 4),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '• ',
                                      style: TextStyle(color: AppColors.error),
                                    ),
                                    Expanded(
                                      child: Text(
                                        indicator.toString(),
                                        style: AppTextStyles.body2,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            )
                            .toList(),
                      ],

                      // Recommendations
                      if (_result!['recommendations'] != null &&
                          (_result!['recommendations'] as List).isNotEmpty) ...[
                        SizedBox(height: 16),
                        Text(
                          '💡 Recommendations:',
                          style: AppTextStyles.headline3,
                        ),
                        SizedBox(height: 8),
                        ...(_result!['recommendations'] as List)
                            .map(
                              (rec) => Padding(
                                padding: EdgeInsets.only(bottom: 4),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '• ',
                                      style: TextStyle(
                                        color: AppColors.primary,
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        rec.toString(),
                                        style: AppTextStyles.body2,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            )
                            .toList(),
                      ],

                      // Fraud Types
                      if (_result!['detected_fraud_types'] != null &&
                          (_result!['detected_fraud_types'] as List)
                              .isNotEmpty) ...[
                        SizedBox(height: 16),
                        Text(
                          '🚨 Detected Fraud Types:',
                          style: AppTextStyles.headline3,
                        ),
                        SizedBox(height: 8),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: (_result!['detected_fraud_types'] as List)
                              .map(
                                (type) => Chip(
                                  label: Text(
                                    type
                                        .toString()
                                        .replaceAll('_', ' ')
                                        .toUpperCase(),
                                    style: TextStyle(fontSize: 10),
                                  ),
                                  backgroundColor: AppColors.error.withOpacity(
                                    0.2,
                                  ),
                                ),
                              )
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
