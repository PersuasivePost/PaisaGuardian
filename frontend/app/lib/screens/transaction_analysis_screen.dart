import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/text_styles.dart';
import '../theme/colors.dart';
import '../services/storage_service.dart';

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
        'title': 'Transaction Analysis',
        'summary': res['explanation'] ?? res.toString(),
        'payload': res,
      });
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
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
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
              Text(
                'Risk score: ' + (_result!['risk_score']?.toString() ?? 'N/A'),
                style: AppTextStyles.headline2,
              ),
              SizedBox(height: 8),
              Text('Explanation:', style: AppTextStyles.body2),
              Text(_result!['explanation']?.toString() ?? ''),
            ],
          ],
        ),
      ),
    );
  }
}
