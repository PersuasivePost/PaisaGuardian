import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../services/token_storage.dart';
import '../theme/colors.dart';
import '../theme/text_styles.dart';

class QRScannerScreen extends StatefulWidget {
  final String baseUrl;
  final String jwt;

  const QRScannerScreen({super.key, required this.baseUrl, required this.jwt});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  final MobileScannerController controller = MobileScannerController();
  String? scannedData;
  bool isAnalyzing = false;
  Map<String, dynamic>? analysisResult;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('QR Code Scanner', style: AppTextStyles.headline3),
        backgroundColor: AppColors.primary,
      ),
      body: Column(
        children: [
          Expanded(
            flex: 4,
            child: Stack(
              children: [
                MobileScanner(
                  controller: controller,
                  onDetect: (capture) {
                    final List<Barcode> barcodes = capture.barcodes;
                    if (barcodes.isNotEmpty &&
                        !isAnalyzing &&
                        analysisResult == null) {
                      final String? code = barcodes.first.rawValue;
                      if (code != null) {
                        _handleQRCode(code);
                      }
                    }
                  },
                ),
                if (isAnalyzing)
                  Container(
                    color: Colors.black54,
                    child: const Center(child: CircularProgressIndicator()),
                  ),
              ],
            ),
          ),
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(24),
                ),
              ),
              child: analysisResult == null
                  ? _buildInstructions()
                  : _buildAnalysisResult(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstructions() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(Icons.qr_code_scanner, size: 60, color: AppColors.secondary),
        const SizedBox(height: 16),
        Text(
          'Position QR Code in Frame',
          style: AppTextStyles.headline3,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          'The QR code will be analyzed automatically for fraud detection',
          style: AppTextStyles.body2.copyWith(color: AppColors.textSecondary),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildAnalysisResult() {
    final result = analysisResult!;
    final riskScore = (result['risk_score'] as num?)?.toDouble() ?? 0.0;
    final isSafe = result['is_safe'] == true;
    final explanation =
        result['explanation'] as String? ?? 'No explanation available';
    
    // Check for collect request
    final isCollectRequest = result['is_collect_request'] == true ||
        (result['detected_fraud_types'] as List?)?.contains('fake_collect') == true;
    final criticalWarning = result['critical_warning'] as String?;
    
    // Check QR type
    final qrType = result['qr_type'] as String?;
    final paymentMode = result['payment_mode'] as String?;

    Color statusColor = isCollectRequest
        ? Colors.red.shade900
        : (isSafe ? AppColors.success : AppColors.error);
    IconData statusIcon = isCollectRequest
        ? Icons.error
        : (isSafe ? Icons.check_circle : Icons.warning);

    return SingleChildScrollView(
      child: Column(
        children: [
          // Critical collect request warning
          if (isCollectRequest)
            Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.red.shade900,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white, width: 2),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.dangerous, color: Colors.white, size: 40),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '🚨 COLLECT REQUEST DETECTED!',
                          style: AppTextStyles.headline3.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    criticalWarning ?? 
                    'This QR code will DEDUCT money FROM your account! '
                    'Scammers use fake collect requests to steal money. DO NOT APPROVE!',
                    style: AppTextStyles.body1.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: statusColor, width: 2),
            ),
            child: Row(
              children: [
                Icon(statusIcon, color: statusColor, size: 40),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isCollectRequest
                            ? '⚠️ DANGEROUS QR Code'
                            : (isSafe ? 'Safe QR Code' : 'Suspicious QR Code'),
                        style: AppTextStyles.headline3.copyWith(
                          color: statusColor,
                        ),
                      ),
                      Text(
                        'Risk Score: ${riskScore.toStringAsFixed(0)}%',
                        style: AppTextStyles.body2.copyWith(color: statusColor),
                      ),
                      if (qrType != null)
                        Text(
                          'Type: ${qrType.toUpperCase()}',
                          style: AppTextStyles.body2.copyWith(
                            color: statusColor,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      if (paymentMode != null)
                        Text(
                          isCollectRequest
                              ? '🚨 Mode: COLLECT (Money OUT)'
                              : 'Mode: PAY (Money Transfer)',
                          style: AppTextStyles.body2.copyWith(
                            color: statusColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.primary,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Analysis Details',
                  style: AppTextStyles.headline3.copyWith(fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(explanation, style: AppTextStyles.body2),
                // Show detected fraud types
                if (result['detected_fraud_types'] != null &&
                    (result['detected_fraud_types'] as List).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    '🚨 Detected Fraud Types:',
                    style: AppTextStyles.body1.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppColors.error,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: (result['detected_fraud_types'] as List)
                        .map((type) => Chip(
                              label: Text(
                                type.toString().replaceAll('_', ' ').toUpperCase(),
                                style: const TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              backgroundColor: Colors.red.withOpacity(0.8),
                              labelStyle: const TextStyle(color: Colors.white),
                            ))
                        .toList(),
                  ),
                ],
                // Show fraud indicators
                if (result['fraud_indicators'] != null &&
                    (result['fraud_indicators'] as List).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    '⚠️ Warning Signs:',
                    style: AppTextStyles.body1.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ...(result['fraud_indicators'] as List).take(5).map((indicator) =>
                      Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('• ', style: TextStyle(color: Colors.orange)),
                            Expanded(
                              child: Text(
                                indicator.toString(),
                                style: AppTextStyles.body2,
                              ),
                            ),
                          ],
                        ),
                      )),
                ],
              ],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _resetScanner,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Scan Again'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _handleQRCode(String code) async {
    if (isAnalyzing || analysisResult != null) return;

    setState(() {
      scannedData = code;
      isAnalyzing = true;
    });

    await controller.stop();
    await _analyzeQRCode(code);
  }

  Future<void> _analyzeQRCode(String qrData) async {
    try {
      final api = ApiService(widget.baseUrl);
      final result = await api.analyzeQR(qrData, widget.jwt);

      setState(() {
        analysisResult = result;
        isAnalyzing = false;
      });

      // Save to storage
      await StorageService.addAlert({
        'timestamp': DateTime.now().toIso8601String(),
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'type': 'qr',
        'title': 'QR Code Analysis',
        'summary': result['explanation'] ?? result.toString(),
        'payload': result,
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
      setState(() {
        isAnalyzing = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Analysis Error: ${apiErr.message}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } catch (e) {
      setState(() {
        isAnalyzing = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Analysis failed: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }

      await controller.start();
    }
  }

  void _resetScanner() {
    setState(() {
      analysisResult = null;
      scannedData = null;
    });
    controller.start();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }
}
