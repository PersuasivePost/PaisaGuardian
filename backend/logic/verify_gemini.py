#!/usr/bin/env python3
"""
Quick Gemini Integration Verification Script
Checks if Gemini AI is properly configured and working
"""

import os
import sys
from pathlib import Path

# Add backend logic to path
sys.path.insert(0, str(Path(__file__).parent))

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking Environment Configuration...")
    print("-" * 50)
    
    # Check .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    print("✅ .env file exists")
    
    # Load environment variables
    from config import settings
    
    # Check Gemini API key
    if not settings.gemini_api_key:
        print("❌ GEMINI_API_KEY is empty!")
        print("   → Add your API key to .env file")
        print("   → Get it from: https://makersuite.google.com/app/apikey")
        return False
    
    # Mask API key for security
    masked_key = settings.gemini_api_key[:10] + "..." + settings.gemini_api_key[-4:]
    print(f"✅ GEMINI_API_KEY configured: {masked_key}")
    
    # Check enabled flag
    if not settings.gemini_enabled:
        print("⚠️  GEMINI_ENABLED is False")
        print("   → Set GEMINI_ENABLED=true in .env")
        return False
    print("✅ GEMINI_ENABLED is True")
    
    # Check model
    print(f"✅ GEMINI_MODEL: {settings.gemini_model}")
    
    return True


def check_dependencies():
    """Check required dependencies"""
    print("\n🔍 Checking Dependencies...")
    print("-" * 50)
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package installed")
        return True
    except ImportError:
        print("❌ google-generativeai not installed!")
        print("   → Run: pip install google-generativeai==0.3.2")
        return False


def test_gemini_connection():
    """Test actual Gemini API connection"""
    print("\n🔍 Testing Gemini API Connection...")
    print("-" * 50)
    
    try:
        from gemini_analyzer import gemini_analyzer
        
        if not gemini_analyzer.enabled:
            print("❌ Gemini analyzer is disabled")
            print("   Reasons:")
            print("   - API key not configured")
            print("   - GEMINI_ENABLED=false")
            print("   - Initialization failed")
            return False
        
        print("✅ Gemini analyzer initialized")
        print(f"   Model: {gemini_analyzer.model_name}")
        
        # Test a simple analysis
        print("\n🧪 Testing URL analysis...")
        risk, indicators, details = gemini_analyzer.analyze_url(
            url="https://test-phishing-site.com",
            domain_details={"creation_date": "2024-01-01"},
            html_content={"has_password_fields": True}
        )
        
        print(f"✅ Analysis successful!")
        print(f"   Risk Score: {risk:.1f}")
        print(f"   Indicators: {len(indicators)}")
        print(f"   Fraud Type: {details.get('fraud_type', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini connection failed: {str(e)}")
        return False


def check_integration():
    """Check main API integration"""
    print("\n🔍 Checking API Integration...")
    print("-" * 50)
    
    try:
        from main import app
        print("✅ Main API imports successfully")
        print("✅ Gemini analyzer integrated")
        return True
    except Exception as e:
        print(f"❌ API integration error: {str(e)}")
        return False


def main():
    """Run all checks"""
    print("=" * 50)
    print("🤖 GEMINI AI INTEGRATION VERIFICATION")
    print("=" * 50)
    print()
    
    all_checks = []
    
    # Run checks
    all_checks.append(("Environment", check_environment()))
    all_checks.append(("Dependencies", check_dependencies()))
    all_checks.append(("Gemini Connection", test_gemini_connection()))
    all_checks.append(("API Integration", check_integration()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    for check_name, passed in all_checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    all_passed = all(passed for _, passed in all_checks)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("=" * 50)
        print("\n✅ Gemini AI is properly integrated and working!")
        print("\n🚀 Next steps:")
        print("   1. Start API server: python main.py")
        print("   2. Check logs for: 'Gemini AI initialized'")
        print("   3. Test endpoints with JWT token")
        print("   4. Monitor AI-enhanced responses")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 50)
        print("\n⚠️  Please fix the issues above and run again")
        print("\n📖 See GEMINI_AI_INTEGRATION.md for detailed setup")
        return 1


if __name__ == "__main__":
    sys.exit(main())
