import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../theme/colors.dart';
import '../theme/text_styles.dart';

class SmsAnalysisScreen extends StatefulWidget {
  final String baseUrl;
  final String jwt;

  const SmsAnalysisScreen({
    super.key,
    required this.baseUrl,
    required this.jwt,
  });

  @override
  State<SmsAnalysisScreen> createState() => _SmsAnalysisScreenState();
}

class _SmsAnalysisScreenState extends State<SmsAnalysisScreen> {
  final _sender = TextEditingController();
  final _message = TextEditingController();
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
      final res = await api.analyzeSms(
        _sender.text.trim(),
        _message.text.trim(),
        widget.jwt,
      );
      setState(() => _result = res);
      await StorageService.addAlert({
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'title': 'SMS Analysis',
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
        title: Text('SMS Analysis', style: AppTextStyles.headline3),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _sender,
              decoration: InputDecoration(hintText: 'Sender'),
            ),
            SizedBox(height: 8),
            TextField(
              controller: _message,
              decoration: InputDecoration(hintText: 'Message'),
              maxLines: 4,
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
