import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/token_storage.dart';
import '../theme/colors.dart';
import '../theme/text_styles.dart';

class ScamReportScreen extends StatefulWidget {
  final String baseUrl;
  final String jwt;
  final String? prefillEntity;
  final String? prefillType;

  const ScamReportScreen({
    super.key,
    required this.baseUrl,
    required this.jwt,
    this.prefillEntity,
    this.prefillType,
  });

  @override
  State<ScamReportScreen> createState() => _ScamReportScreenState();
}

class _ScamReportScreenState extends State<ScamReportScreen> {
  final _entityController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _amountController = TextEditingController();

  String _entityType = 'phone_numbers';
  String _fraudCategory = 'sms_scam';
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _result;

  @override
  void initState() {
    super.initState();
    if (widget.prefillEntity != null) {
      _entityController.text = widget.prefillEntity!;
    }
    if (widget.prefillType != null) {
      _entityType = widget.prefillType!;
    }
  }

  Future<void> _submitReport() async {
    if (_entityController.text.trim().isEmpty) {
      setState(() => _error = 'Please enter a phone number or UPI ID');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });

    try {
      final token = await TokenStorage.getAccessToken() ?? widget.jwt;
      final api = ApiService(widget.baseUrl);

      final amount = double.tryParse(_amountController.text.trim());

      final result = await api.reportFraud(
        entityId: _entityController.text.trim(),
        entityType: _entityType,
        description: _descriptionController.text.trim(),
        fraudCategory: _fraudCategory,
        amountLost: amount,
        jwt: token,
      );

      setState(() => _result = result);

      // Show success dialog
      if (mounted) {
        _showSuccessDialog();
      }
    } on ApiException catch (apiErr) {
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

  void _showSuccessDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green, size: 32),
            SizedBox(width: 8),
            Text('Report Submitted!', style: AppTextStyles.headline3),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Thank you for helping protect others!',
              style: AppTextStyles.body1,
            ),
            SizedBox(height: 16),
            if (_result != null) ...[
              Text(
                'Entity: ${_result!['entity_id']}',
                style: AppTextStyles.body2,
              ),
              SizedBox(height: 4),
              Text(
                'Total Reports: ${_result!['report_count']}',
                style: AppTextStyles.body2.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.error,
                ),
              ),
              if (_result!['blacklisted'] == true) ...[
                SizedBox(height: 8),
                Container(
                  padding: EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.error.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.block, color: AppColors.error, size: 20),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'This entity has been blacklisted!',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.error,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // Go back to previous screen
            },
            child: Text('Done'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Report Scam', style: AppTextStyles.headline3),
        backgroundColor: AppColors.error,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Warning banner
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.error.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.error.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.warning_amber_rounded,
                    color: AppColors.error,
                    size: 32,
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Help Protect Others!',
                          style: AppTextStyles.headline3.copyWith(
                            color: AppColors.error,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Report scam numbers and UPI IDs to warn the community.',
                          style: AppTextStyles.body2,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            SizedBox(height: 24),

            // Entity Type Selector
            Text('What are you reporting?', style: AppTextStyles.headline3),
            SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _entityType,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.category),
              ),
              items: [
                DropdownMenuItem(
                  value: 'phone_numbers',
                  child: Text('Phone Number'),
                ),
                DropdownMenuItem(value: 'upi_ids', child: Text('UPI ID')),
                DropdownMenuItem(value: 'urls', child: Text('Website URL')),
                DropdownMenuItem(
                  value: 'senders',
                  child: Text('SMS Sender ID'),
                ),
              ],
              onChanged: (value) =>
                  setState(() => _entityType = value ?? _entityType),
            ),

            SizedBox(height: 16),

            // Entity Input
            Text('Enter Details *', style: AppTextStyles.headline3),
            SizedBox(height: 8),
            TextField(
              controller: _entityController,
              decoration: InputDecoration(
                hintText: _entityType == 'phone_numbers'
                    ? '+91XXXXXXXXXX'
                    : _entityType == 'upi_ids'
                    ? 'scammer@paytm'
                    : _entityType == 'urls'
                    ? 'https://scam-site.com'
                    : 'VK-SCAM',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.report_problem),
              ),
              keyboardType: _entityType == 'phone_numbers'
                  ? TextInputType.phone
                  : TextInputType.text,
            ),

            SizedBox(height: 16),

            // Fraud Category
            Text('Scam Type', style: AppTextStyles.headline3),
            SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _fraudCategory,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.security),
              ),
              items: [
                DropdownMenuItem(value: 'sms_scam', child: Text('SMS Scam')),
                DropdownMenuItem(value: 'phishing', child: Text('Phishing')),
                DropdownMenuItem(
                  value: 'fake_upi',
                  child: Text('Fake UPI Request'),
                ),
                DropdownMenuItem(
                  value: 'impersonation',
                  child: Text('Impersonation'),
                ),
                DropdownMenuItem(
                  value: 'qr_code_fraud',
                  child: Text('QR Code Fraud'),
                ),
                DropdownMenuItem(
                  value: 'social_engineering',
                  child: Text('Social Engineering'),
                ),
              ],
              onChanged: (value) =>
                  setState(() => _fraudCategory = value ?? _fraudCategory),
            ),

            SizedBox(height: 16),

            // Description
            Text('Description (Optional)', style: AppTextStyles.headline3),
            SizedBox(height: 8),
            TextField(
              controller: _descriptionController,
              decoration: InputDecoration(
                hintText: 'Describe what happened...',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.description),
              ),
              maxLines: 4,
            ),

            SizedBox(height: 16),

            // Amount Lost
            Text('Amount Lost (Optional)', style: AppTextStyles.headline3),
            SizedBox(height: 8),
            TextField(
              controller: _amountController,
              decoration: InputDecoration(
                hintText: 'Enter amount in ₹',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.currency_rupee),
              ),
              keyboardType: TextInputType.numberWithOptions(decimal: true),
            ),

            SizedBox(height: 24),

            // Error display
            if (_error != null) ...[
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.error.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: AppColors.error),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _error!,
                        style: TextStyle(color: AppColors.error),
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 16),
            ],

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _loading ? null : _submitReport,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.error,
                  foregroundColor: Colors.white,
                ),
                child: _loading
                    ? CircularProgressIndicator(color: Colors.white)
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.report),
                          SizedBox(width: 8),
                          Text('Submit Report', style: AppTextStyles.button),
                        ],
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _entityController.dispose();
    _descriptionController.dispose();
    _amountController.dispose();
    super.dispose();
  }
}
