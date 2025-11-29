import 'package:flutter/material.dart';
import 'colors.dart';
import 'text_styles.dart';

final ThemeData royalDarkTheme = ThemeData(
  brightness: Brightness.light,
  scaffoldBackgroundColor: AppColors.primary,
  primaryColor: AppColors.secondary,
  canvasColor: AppColors.surface,
  cardColor: AppColors.surface,
  dividerColor: AppColors.textSecondary.withOpacity(0.12),
  colorScheme: ColorScheme.light(
    primary: AppColors.secondary,
    secondary: AppColors.tertiary,
    surface: AppColors.surface,
    background: AppColors.primary,
    error: AppColors.error,
    onPrimary: Colors.white,
    onSecondary: AppColors.text,
    onSurface: AppColors.text,
    onBackground: AppColors.text,
    onError: Colors.white,
  ),
  textTheme: TextTheme(
    headlineLarge: AppTextStyles.headline1,
    headlineMedium: AppTextStyles.headline2,
    headlineSmall: AppTextStyles.headline3,
    bodyLarge: AppTextStyles.body1,
    bodyMedium: AppTextStyles.body2,
    labelLarge: AppTextStyles.button,
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.secondary,
      foregroundColor: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: AppColors.secondary, width: 1.5),
      ),
      textStyle: AppTextStyles.button,
      elevation: 2,
      shadowColor: AppColors.secondary.withOpacity(0.25),
    ),
  ),
  cardTheme: CardThemeData(
    color: AppColors.surface,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
      side: BorderSide(color: AppColors.secondary.withOpacity(0.15)),
    ),
    elevation: 1,
    shadowColor: AppColors.textSecondary.withOpacity(0.15),
    margin: EdgeInsets.all(8),
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: AppColors.surface,
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: AppColors.secondary.withOpacity(0.3)),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: AppColors.secondary, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: AppColors.error),
    ),
  ),
  appBarTheme: AppBarTheme(
    backgroundColor: AppColors.primary,
    elevation: 0,
    titleTextStyle: AppTextStyles.headline3,
    iconTheme: IconThemeData(color: AppColors.text),
    centerTitle: true,
  ),
  bottomNavigationBarTheme: BottomNavigationBarThemeData(
    backgroundColor: AppColors.surface,
    selectedItemColor: AppColors.secondary,
    unselectedItemColor: AppColors.textSecondary,
    selectedIconTheme: IconThemeData(size: 22),
  ),
  dialogTheme: DialogThemeData(
    backgroundColor: AppColors.surface,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
      side: BorderSide(color: AppColors.secondary.withOpacity(0.06)),
    ),
    titleTextStyle: AppTextStyles.headline2,
    contentTextStyle: AppTextStyles.body1,
  ),
  switchTheme: SwitchThemeData(
    thumbColor: MaterialStateProperty.resolveWith(
      (states) => AppColors.secondary,
    ),
    trackColor: MaterialStateProperty.resolveWith(
      (states) => AppColors.secondary.withOpacity(0.3),
    ),
  ),
  snackBarTheme: SnackBarThemeData(
    backgroundColor: AppColors.surface,
    contentTextStyle: AppTextStyles.body1,
    actionTextColor: AppColors.secondary,
  ),
  // Premium shimmer effect helper as a decoration example can be used in widgets
);
