import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../theme/colors.dart';
import '../theme/text_styles.dart';

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
        'title': 'URL Analysis',
        'summary': res['explanation'] ?? res.toString(),
        'payload': res,
      });
    } on ApiException catch (apiErr) {
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
      body: Padding(
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
