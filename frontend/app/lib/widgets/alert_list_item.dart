import 'package:flutter/material.dart';
import '../theme/colors.dart';
import '../theme/text_styles.dart';

class AlertListItem extends StatelessWidget {
  final String title;
  final String subtitle;
  final String riskLevel;
  final double riskScore;
  final DateTime timestamp;
  final VoidCallback? onTap;
  final VoidCallback? onDelete;

  const AlertListItem({
    super.key,
    required this.title,
    required this.subtitle,
    required this.riskLevel,
    required this.riskScore,
    required this.timestamp,
    this.onTap,
    this.onDelete,
  });

  Color _getRiskColor() {
    if (riskScore >= 70) return AppColors.error;
    if (riskScore >= 40) return const Color(0xFFFFA500); // Orange
    return AppColors.success;
  }

  IconData _getRiskIcon() {
    if (riskScore >= 70) return Icons.dangerous;
    if (riskScore >= 40) return Icons.warning_amber;
    return Icons.check_circle;
  }

  String _getTimeAgo() {
    final diff = DateTime.now().difference(timestamp);
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'Just now';
  }

  @override
  Widget build(BuildContext context) {
    final riskColor = _getRiskColor();

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: riskColor.withOpacity(0.3), width: 1.5),
          boxShadow: [
            BoxShadow(
              color: riskColor.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: riskColor.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(_getRiskIcon(), color: riskColor, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: AppTextStyles.headline3.copyWith(fontSize: 16),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: riskColor.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          riskLevel.toUpperCase(),
                          style: AppTextStyles.body2.copyWith(
                            color: riskColor,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: AppTextStyles.body2.copyWith(
                      color: AppColors.textSecondary,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        Icons.access_time,
                        size: 14,
                        color: AppColors.textSecondary,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _getTimeAgo(),
                        style: AppTextStyles.body2.copyWith(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Icon(Icons.trending_up, size: 14, color: riskColor),
                      const SizedBox(width: 4),
                      Text(
                        '${riskScore.toStringAsFixed(0)}%',
                        style: AppTextStyles.body2.copyWith(
                          fontSize: 12,
                          color: riskColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            if (onDelete != null) ...[
              const SizedBox(width: 8),
              IconButton(
                icon: Icon(
                  Icons.delete_outline,
                  color: AppColors.error.withOpacity(0.7),
                ),
                onPressed: onDelete,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
