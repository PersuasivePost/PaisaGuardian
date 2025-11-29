#!/usr/bin/env python3
"""
Quick test script for Gemini AI integration
Tests all analysis functions with sample data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from gemini_analyzer import GeminiAnalyzer


def test_gemini_initialization():
    """Test Gemini initialization"""
    print("=" * 60)
    print("TEST 1: Gemini Initialization")
    print("=" * 60)
    
    # Test with environment variables
    analyzer = GeminiAnalyzer()
    print(f"✓ Gemini Enabled: {analyzer.enabled}")
    print(f"✓ Model: {analyzer.model_name}")
    print(f"✓ API Key: {'***' + analyzer.api_key[-4:] if analyzer.api_key else 'Not set'}")
    print()


def test_url_analysis():
    """Test URL analysis"""
    print("=" * 60)
    print("TEST 2: URL Analysis")
    print("=" * 60)
    
    analyzer = GeminiAnalyzer()
    if not analyzer.enabled:
        print("⚠️  Skipped (Gemini not enabled)")
        print()
        return
    
    test_url = "https://phonepe-verifykec.com"
    domain_details = {
        "creation_date": "2024-01-15",
        "ssl_valid": False
    }
    html_content = {
        "has_payment_forms": True,
        "has_otp_fields": True,
        "has_password_fields": True
    }
    
    print(f"Analyzing URL: {test_url}")
    risk_score, indicators, details = analyzer.analyze_url(
        url=test_url,
        domain_details=domain_details,
        html_content=html_content
    )
    
    print(f"✓ AI Risk Score: {risk_score:.1f}/100")
    print(f"✓ Fraud Type: {details.get('ai_fraud_type', 'N/A')}")
    print(f"✓ Confidence: {details.get('ai_confidence', 'N/A')}")
    print(f"✓ Indicators ({len(indicators)}):")
    for ind in indicators:
        print(f"  - {ind}")
    print(f"✓ Reasoning: {details.get('ai_reasoning', 'N/A')[:100]}...")
    print()


def test_sms_analysis():
    """Test SMS analysis"""
    print("=" * 60)
    print("TEST 3: SMS Analysis")
    print("=" * 60)
    
    analyzer = GeminiAnalyzer()
    if not analyzer.enabled:
        print("⚠️  Skipped (Gemini not enabled)")
        print()
        return
    
    test_sms = "Dear customer, your KYC is expired. Update now by clicking bit.ly/kyc-update or your account will be blocked within 24 hours."
    sender = "VD-KYCINF"
    
    print(f"Analyzing SMS from: {sender}")
    print(f"Message: {test_sms[:80]}...")
    risk_score, indicators, details = analyzer.analyze_sms(
        message=test_sms,
        sender=sender
    )
    
    print(f"✓ AI Risk Score: {risk_score:.1f}/100")
    print(f"✓ Scam Type: {details.get('ai_scam_type', 'N/A')}")
    print(f"✓ Confidence: {details.get('ai_confidence', 'N/A')}")
    print(f"✓ Indicators ({len(indicators)}):")
    for ind in indicators:
        print(f"  - {ind}")
    print(f"✓ Reasoning: {details.get('ai_reasoning', 'N/A')[:100]}...")
    print()


def test_transaction_analysis():
    """Test transaction analysis"""
    print("=" * 60)
    print("TEST 4: Transaction Analysis")
    print("=" * 60)
    
    analyzer = GeminiAnalyzer()
    if not analyzer.enabled:
        print("⚠️  Skipped (Gemini not enabled)")
        print()
        return
    
    amount = 50000
    recipient_upi = "9876543210@paytm"
    recipient_name = "Customer Support"
    note = "Urgent refund processing"
    
    print(f"Analyzing Transaction:")
    print(f"  Amount: ₹{amount:,}")
    print(f"  To: {recipient_upi}")
    print(f"  Name: {recipient_name}")
    print(f"  Note: {note}")
    
    risk_score, indicators, details = analyzer.analyze_transaction(
        amount=amount,
        recipient_upi=recipient_upi,
        recipient_name=recipient_name,
        note=note,
        is_new_payee=True
    )
    
    print(f"✓ AI Risk Score: {risk_score:.1f}/100")
    print(f"✓ Recommendation: {details.get('ai_recommendation', 'N/A')}")
    print(f"✓ Confidence: {details.get('ai_confidence', 'N/A')}")
    print(f"✓ Indicators ({len(indicators)}):")
    for ind in indicators:
        print(f"  - {ind}")
    print(f"✓ Reasoning: {details.get('ai_reasoning', 'N/A')[:100]}...")
    print()


def test_qr_analysis():
    """Test QR code analysis"""
    print("=" * 60)
    print("TEST 5: QR Code Analysis")
    print("=" * 60)
    
    analyzer = GeminiAnalyzer()
    if not analyzer.enabled:
        print("⚠️  Skipped (Gemini not enabled)")
        print()
        return
    
    qr_data = "upi://pay?pa=scammer@upi&pn=Refund Department&am=5000&mode=02&cu=INR"
    qr_type = "upi_intent"
    
    print(f"Analyzing QR Code: {qr_data[:50]}...")
    risk_score, indicators, details = analyzer.analyze_qr_code(
        qr_data=qr_data,
        qr_type=qr_type
    )
    
    print(f"✓ AI Risk Score: {risk_score:.1f}/100")
    print(f"✓ Fraud Type: {details.get('ai_fraud_type', 'N/A')}")
    print(f"✓ Confidence: {details.get('ai_confidence', 'N/A')}")
    print(f"✓ Recommendation: {details.get('ai_recommendation', 'N/A')}")
    print(f"✓ Indicators ({len(indicators)}):")
    for ind in indicators:
        print(f"  - {ind}")
    print()


def test_fraud_explanation():
    """Test fraud explanation generation"""
    print("=" * 60)
    print("TEST 6: Fraud Explanation")
    print("=" * 60)
    
    analyzer = GeminiAnalyzer()
    if not analyzer.enabled:
        print("⚠️  Skipped (Gemini not enabled)")
        print()
        return
    
    fraud_type = "fake_collect_request"
    indicators = [
        "UPI collect mode detected (mode=02)",
        "Requests money FROM user instead of TO recipient",
        "Suspicious merchant name"
    ]
    risk_score = 85.0
    
    print(f"Generating explanation for: {fraud_type}")
    explanation = analyzer.explain_fraud(
        fraud_type=fraud_type,
        indicators=indicators,
        risk_score=risk_score
    )
    
    print(f"✓ Explanation:")
    print(f"{explanation}")
    print()


def main():
    """Run all tests"""
    print("\n🤖 GEMINI AI INTEGRATION TEST SUITE\n")
    
    try:
        test_gemini_initialization()
        test_url_analysis()
        test_sms_analysis()
        test_transaction_analysis()
        test_qr_analysis()
        test_fraud_explanation()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print()
        print("If Gemini is not enabled, set:")
        print("  1. GEMINI_API_KEY in .env")
        print("  2. GEMINI_ENABLED=true in .env")
        print()
        print("Get API key: https://makersuite.google.com/app/apikey")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
