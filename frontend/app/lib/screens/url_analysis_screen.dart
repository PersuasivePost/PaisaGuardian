import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../services/token_storage.dart';
import '../services/remote_access_detector.dart';
import '../theme/colors.dart';
import '../theme/text_styles.dart';
import '../widgets/remote_access_warning.dart';

class UrlAnalysisScreen extends StatefulWidget {
  final String baseUrl;
  final String jwt;

  const UrlAnalysisScreen({
    super.key,
    required this.baseUrl,
    required this.jwt,
  });

  @override
  State<UrlAnalysisScreen> createState() => _UrlAnalysisScreenState();
}

class _UrlAnalysisScreenState extends State<UrlAnalysisScreen> {
  final _controller = TextEditingController();
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _result;
  RemoteAccessDetectionResult? _remoteAccessDetection;

  @override
  void initState() {
    super.initState();
    _checkRemoteAccess();
  }

  Future<void> _checkRemoteAccess() async {
    final detection = await RemoteAccessDetector.detectRemoteAccessApps();
    if (mounted) {
      setState(() {
        _remoteAccessDetection = detection;
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
      final res = await api.analyzeUrl(_controller.text.trim(), widget.jwt);
      setState(() => _result = res);
      // store locally
      await StorageService.addAlert({
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'type': 'url',
        'title': 'URL Analysis',
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
        title: Text('URL Analysis', style: AppTextStyles.headline3),
      ),
      body: Column(
        children: [
          if (_remoteAccessDetection != null && _remoteAccessDetection!.isDetected)
            RemoteAccessBanner(
              detection: _remoteAccessDetection!,
              onTap: () {},
            ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  TextField(
                    controller: _controller,
                    decoration: InputDecoration(hintText: 'Enter URL'),
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
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
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
                                    ? '✓ Safe to proceed'
                                    : '⚠ Caution advised',
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
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    ),
      ],
    );
  }
}
