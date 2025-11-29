import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/remote_access_detector.dart';
import '../theme/colors.dart';

/// Widget that displays a warning when remote access is detected
class RemoteAccessWarning extends StatelessWidget {
  final RemoteAccessDetectionResult detection;
  final VoidCallback? onDismiss;
  final VoidCallback? onLearnMore;

  const RemoteAccessWarning({
    super.key,
    required this.detection,
    this.onDismiss,
    this.onLearnMore,
  });

  @override
  Widget build(BuildContext context) {
    if (!detection.isDetected) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        border: Border.all(color: Colors.red.shade700, width: 2),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.red.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded,
                  color: Colors.red.shade700, size: 32),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  '⚠️ REMOTE ACCESS DETECTED',
                  style: GoogleFonts.inter(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade900,
                  ),
                ),
              ),
              if (onDismiss != null)
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: onDismiss,
                  color: Colors.red.shade700,
                ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Detected Applications:',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.red.shade900,
                  ),
                ),
                const SizedBox(height: 8),
                ...detection.detectedApps.map((app) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          Icon(Icons.desktop_windows,
                              size: 16, color: Colors.red.shade700),
                          const SizedBox(width: 8),
                          Text(
                            app,
                            style: GoogleFonts.inter(
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                              color: Colors.red.shade800,
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Text(
            '🚨 FRAUD WARNING',
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.red.shade900,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Remote access apps are commonly used by scammers to:',
            style: GoogleFonts.inter(
              fontSize: 13,
              color: Colors.red.shade800,
            ),
          ),
          const SizedBox(height: 8),
          _buildWarningPoint('Take control of your device'),
          _buildWarningPoint('Access your banking apps'),
          _buildWarningPoint('Steal money from your accounts'),
          _buildWarningPoint('View your personal information'),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.red.shade900,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '🛡️ PROTECT YOURSELF:',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                _buildProtectionStep('1. Close ALL remote access apps immediately'),
                _buildProtectionStep(
                    '2. Do NOT proceed with any transactions'),
                _buildProtectionStep('3. Uninstall suspicious apps'),
                _buildProtectionStep(
                    '4. Contact your bank if you shared any details'),
                _buildProtectionStep('5. Report the scammer to authorities'),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: onLearnMore,
                  icon: const Icon(Icons.info_outline),
                  label: const Text('Learn More'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade700,
                    foregroundColor: Colors.white,
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

  Widget _buildWarningPoint(String text) {
    return Padding(
      padding: const EdgeInsets.only(left: 16, bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('• ',
              style: GoogleFonts.inter(
                  fontSize: 13, color: Colors.red.shade800)),
          Expanded(
            child: Text(
              text,
              style:
                  GoogleFonts.inter(fontSize: 13, color: Colors.red.shade800),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProtectionStep(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Text(
        text,
        style: GoogleFonts.inter(
          fontSize: 13,
          color: Colors.white,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

/// Compact warning banner for headers
class RemoteAccessBanner extends StatelessWidget {
  final RemoteAccessDetectionResult detection;
  final VoidCallback? onTap;

  const RemoteAccessBanner({
    super.key,
    required this.detection,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (!detection.isDetected) return const SizedBox.shrink();

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        decoration: BoxDecoration(
          color: Colors.red.shade700,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            const Icon(Icons.warning_amber_rounded,
                color: Colors.white, size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '⚠️ Remote Access Detected: ${detection.detectedApps.join(", ")}',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.white),
          ],
        ),
      ),
    );
  }
}
