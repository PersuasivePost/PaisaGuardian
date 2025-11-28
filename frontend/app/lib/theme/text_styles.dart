import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'colors.dart';

class AppTextStyles {
  AppTextStyles._();

  // Headlines: Poppins Bold
  static TextStyle headline1 = GoogleFonts.poppins(
    color: AppColors.text,
    fontSize: 32,
    fontWeight: FontWeight.w700,
  );

  static TextStyle headline2 = GoogleFonts.poppins(
    color: AppColors.text,
    fontSize: 24,
    fontWeight: FontWeight.w700,
  );

  static TextStyle headline3 = GoogleFonts.poppins(
    color: AppColors.text,
    fontSize: 20,
    fontWeight: FontWeight.w600,
  );

  // Body: Inter Regular
  static TextStyle body1 = GoogleFonts.inter(
    color: AppColors.text,
    fontSize: 16,
    fontWeight: FontWeight.w400,
  );

  static TextStyle body2 = GoogleFonts.inter(
    color: AppColors.textSecondary,
    fontSize: 14,
    fontWeight: FontWeight.w400,
  );

  // Buttons: Poppins SemiBold
  static TextStyle button = GoogleFonts.poppins(
    color: AppColors.primary,
    fontSize: 16,
    fontWeight: FontWeight.w600,
  );
}
