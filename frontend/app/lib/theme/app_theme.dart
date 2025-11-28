import 'colors.dart';

/// Theme constants wrapper for consistent styling
class AppTheme {
  AppTheme._();

  // Primary colors
  static const primaryColor = AppColors.primary;
  static const accentColor = AppColors.secondary;
  static const goldAccent = AppColors.secondary;
  static const surfaceColor = AppColors.surface;
  static const errorColor = AppColors.error;
  static const successColor = AppColors.success;

  // Text colors
  static const textPrimaryColor = AppColors.text;
  static const textSecondaryColor = AppColors.textSecondary;

  // Gradient colors
  static const gradientStart = AppColors.royalGradientBegin;
  static const gradientEnd = AppColors.royalGradientEnd;
}
