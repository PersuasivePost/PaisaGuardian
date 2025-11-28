import 'package:flutter/material.dart';
import 'colors.dart';

class CustomShadows {
  CustomShadows._();

  static List<BoxShadow> premiumCard = [
    BoxShadow(
      color: Colors.black.withOpacity(0.6),
      offset: Offset(0, 8),
      blurRadius: 24,
      spreadRadius: -4,
    ),
    BoxShadow(
      color: AppColors.secondary.withOpacity(0.12),
      offset: Offset(0, 1),
      blurRadius: 0,
      spreadRadius: 0,
    ),
  ];

  static List<BoxShadow> subtleElev = [
    BoxShadow(
      color: Colors.black.withOpacity(0.45),
      offset: Offset(0, 6),
      blurRadius: 18,
      spreadRadius: -6,
    ),
  ];
}
