"""
Test cases for enhanced fraud detection features
Run these tests to verify the new detection capabilities
"""

# Test data for various fraud detection scenarios

# 1. FAKE COLLECT REQUEST TESTS
fake_collect_requests = [
    {
        "name": "QR Code Collect Request",
        "qr_data": "upi://pay?pa=scammer@paytm&pn=FakeStore&am=5000&mode=02",
        "expected": "Should detect collect request and warn about money deduction"
    },
    {
        "name": "UPI Collect Intent",
        "qr_data": "upi://collect?pa=fraudster@ybl&am=10000",
        "expected": "Should flag as fake collect request with high risk score"
    },
    {
        "name": "Mode 02 Collect",
        "qr_data": "upi://pay?pa=fake@paytm&mode=02&am=2000&tn=Refund",
        "expected": "Should detect mode=02 as collect request"
    }
]

# 2. FAKE KYC SMS TESTS
fake_kyc_sms = [
    {
        "name": "Urgent KYC Update",
        "message": "Your KYC is pending. Update immediately or account will be blocked. Click: bit.ly/kyc123",
        "sender": "VK-BANK",
        "expected": "High confidence fake KYC detection with urgency + shortened URL"
    },
    {
        "name": "KYC Expiry Warning",
        "message": "URGENT: Your eKYC will expire today. Complete Re-KYC now: http://sbi-kyc-verify.com",
        "sender": "SB-ALERT",
        "expected": "Multiple KYC patterns + urgency + suspicious domain"
    },
    {
        "name": "Account Suspension Threat",
        "message": "Dear customer, your account KYC is incomplete. Complete within 24 hours to avoid suspension. Link: kyc.update.tk",
        "sender": "HD-BANK",
        "expected": "KYC scam with suspension threat"
    },
    {
        "name": "Download App KYC",
        "message": "Update your KYC by downloading our app: bit.ly/bankapp. Call 9876543210 for help",
        "sender": "AX-BANK",
        "expected": "KYC + download + phone number red flags"
    }
]

# 3. SCREEN-SHARING APP DETECTION TESTS
screen_sharing_tests = [
    {
        "name": "AnyDesk Installation Request",
        "message": "Dear customer, install AnyDesk for account verification. Support will call you.",
        "device_info": {
            "screen_sharing_apps_detected": ["anydesk"]
        },
        "expected": "Critical warning about screen sharing app"
    },
    {
        "name": "Multiple Screen Sharing Apps",
        "message": "Technical support required",
        "device_info": {
            "screen_sharing_apps_detected": ["teamviewer", "quicksupport"]
        },
        "expected": "Detect multiple remote access apps"
    },
    {
        "name": "Remote Support Scam",
        "message": "Download TeamViewer immediately to fix your account issue",
        "device_info": {
            "screen_sharing_apps_detected": ["teamviewer"]
        },
        "expected": "High risk score for remote access request"
    }
]

# 4. NEW PAYEE DETECTION TESTS
new_payee_tests = [
    {
        "name": "First Time Large Transaction",
        "transaction": {
            "amount": 15000.0,
            "recipient_upi": "unknown@paytm",
            "recipient_name": "Unknown Person"
        },
        "expected": "High risk: new payee + large amount"
    },
    {
        "name": "New Payee Small Amount",
        "transaction": {
            "amount": 100.0,
            "recipient_upi": "newuser@phonepe",
            "recipient_name": "New Contact"
        },
        "expected": "Medium risk: new payee but small amount"
    },
    {
        "name": "Amount Anomaly (Existing Payee)",
        "transaction": {
            "amount": 25000.0,
            "recipient_upi": "regular@paytm",
            "recipient_name": "Regular Merchant",
            "note": "Assume avg transaction with this payee is ₹500"
        },
        "expected": "Should detect 50x amount anomaly if payee exists in DB"
    }
]

# 5. PHISHING WEBSITE TESTS (Basic)
phishing_basic_tests = [
    {
        "name": "HTTP Payment Page",
        "url": "http://payment-gateway-secure.com/checkout",
        "expected": "Non-HTTPS + phishing keywords"
    },
    {
        "name": "Multiple Phishing Keywords",
        "url": "https://verify-secure-login-account.com/update",
        "expected": "Multiple phishing keywords in domain"
    },
    {
        "name": "IP Address URL",
        "url": "http://192.168.1.100/bank/login",
        "expected": "IP address instead of domain name"
    },
    {
        "name": "URL Shortener Phishing",
        "url": "https://bit.ly/bank-verify-2024",
        "expected": "Suspicious URL shortener"
    }
]

# 6. TYPOSQUATTING TESTS
typosquatting_tests = [
    {
        "name": "Paytm Typosquatting",
        "url": "https://paytim.com/login",
        "expected": "95% similar to paytm.com - typosquatting detected"
    },
    {
        "name": "PhonePe with Hyphen",
        "url": "https://phone-pe.com/payment",
        "expected": "Character substitution typosquatting"
    },
    {
        "name": "Google Pay Misspelling",
        "url": "https://googlepey.com/upi",
        "expected": "Typosquatting googlepay.com"
    },
    {
        "name": "SBI Bank Fake",
        "url": "https://sbi-secure.co.in/netbanking",
        "expected": "Hyphen addition typosquatting"
    },
    {
        "name": "Amazon Pay Fake",
        "url": "https://amazinpay.com/checkout",
        "expected": "Character swap typosquatting"
    }
]

# 7. HOMOGRAPH ATTACK TESTS
homograph_tests = [
    {
        "name": "Cyrillic 'a' in Paytm",
        "url": "https://pаytm.com",  # Note: 'а' is Cyrillic, not ASCII
        "expected": "Homograph attack with lookalike character"
    },
    {
        "name": "Mixed Script Domain",
        "url": "https://gооgle.com",  # Cyrillic 'о'
        "expected": "Detect mixed ASCII + Unicode scripts"
    }
]

# 8. ADVANCED PHISHING (Combined Tests)
advanced_phishing_tests = [
    {
        "name": "Complete Phishing Attack",
        "url": "https://paytim.com/secure-login-verify/payment",
        "domain_details": {
            "creation_date": "2025-11-25",
            "ssl_valid": False,
            "ssl_issuer": "Let's Encrypt"
        },
        "html_content": {
            "has_payment_forms": True,
            "has_password_fields": True,
            "has_otp_fields": True,
            "external_scripts": [
                "http://malicious.com/script1.js",
                "http://malicious.com/script2.js"
            ]
        },
        "expected": "Critical risk: typosquatting + no SSL + new domain + OTP fields + phishing keywords"
    },
    {
        "name": "Fake Banking Portal",
        "url": "https://hdfcbank-secure-login.com/netbanking/verify",
        "domain_details": {
            "creation_date": "2025-11-20",
            "ssl_valid": True
        },
        "html_content": {
            "has_password_fields": True,
            "has_otp_fields": True,
            "suspicious_patterns": [
                "Requests ATM PIN",
                "Asks for CVV"
            ]
        },
        "redirect_chain": {
            "count": 3,
            "redirects": [
                "https://hdfcbank-secure-login.com",
                "https://verify.hdfcbank-secure.net",
                "https://login.hdfcsecure.tk"
            ],
            "suspicious": True
        },
        "expected": "High risk: multiple red flags combined"
    }
]


# TESTING INSTRUCTIONS
"""
To test these scenarios:

1. Start the FastAPI server:
   cd backend/logic
   python main.py

2. Get authentication token from auth server

3. Test each scenario using curl or Python requests:

# Example: Test Fake Collect Request
curl -X POST http://localhost:8000/analyze/qr \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "qr_data": "upi://pay?pa=scammer@paytm&mode=02&am=5000"
  }'

# Example: Test Fake KYC SMS
curl -X POST http://localhost:8000/analyze/sms \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Your KYC is pending. Update now: bit.ly/kyc123",
    "sender": "VK-BANK"
  }'

# Example: Test Typosquatting
curl -X POST http://localhost:8000/analyze/url \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://paytim.com/login"
  }'

# Example: Test New Payee
curl -X POST http://localhost:8000/analyze/transaction \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "transaction": {
      "amount": 15000,
      "recipient_upi": "unknown@paytm",
      "recipient_name": "Unknown Person"
    }
  }'

# Example: Get Payee Info
curl -X GET http://localhost:8000/payee/info/merchant@paytm \\
  -H "Authorization: Bearer YOUR_TOKEN"

# Example: Mark Payee as Trusted
curl -X POST http://localhost:8000/payee/trust/merchant@paytm?trusted=true \\
  -H "Authorization: Bearer YOUR_TOKEN"
"""


# EXPECTED RESULTS SUMMARY
expected_results = {
    "Fake Collect Request": {
        "risk_score_range": "60-80",
        "risk_level": "high/critical",
        "key_indicator": "🚨 DANGER: This is a COLLECT REQUEST!"
    },
    "Fake KYC SMS": {
        "risk_score_range": "60-85",
        "risk_level": "high/critical",
        "key_indicator": "🚨 FAKE KYC SCAM DETECTED"
    },
    "Screen-Sharing Apps": {
        "risk_score_range": "50+",
        "risk_level": "high",
        "key_indicator": "🚨 CRITICAL: Screen sharing app detected"
    },
    "New Payee": {
        "risk_score_range": "25-40",
        "risk_level": "medium",
        "key_indicator": "⚠️ NEW PAYEE: First time sending money"
    },
    "Typosquatting": {
        "risk_score_range": "50+",
        "risk_level": "high",
        "key_indicator": "⚠️ Typosquatting: Looks like 'paytm.com'"
    },
    "Homograph Attack": {
        "risk_score_range": "45+",
        "risk_level": "medium/high",
        "key_indicator": "⚠️ Homograph attack detected"
    },
    "Advanced Phishing": {
        "risk_score_range": "80-100",
        "risk_level": "critical",
        "key_indicator": "Multiple fraud indicators combined"
    }
}


if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED FRAUD DETECTION TEST CASES")
    print("=" * 60)
    print()
    
    test_categories = [
        ("Fake Collect Requests", fake_collect_requests),
        ("Fake KYC SMS", fake_kyc_sms),
        ("Screen-Sharing Apps", screen_sharing_tests),
        ("New Payee Detection", new_payee_tests),
        ("Basic Phishing", phishing_basic_tests),
        ("Typosquatting", typosquatting_tests),
        ("Homograph Attacks", homograph_tests),
        ("Advanced Phishing", advanced_phishing_tests)
    ]
    
    for category, tests in test_categories:
        print(f"\n📋 {category} ({len(tests)} tests)")
        print("-" * 60)
        for i, test in enumerate(tests, 1):
            print(f"{i}. {test['name']}")
            print(f"   Expected: {test['expected']}")
        print()
    
    print("\n" + "=" * 60)
    print("Total Test Cases:", sum(len(tests) for _, tests in test_categories))
    print("=" * 60)
    print("\nSee ENHANCED_FRAUD_DETECTION.md for complete documentation")
    print("See testing instructions above for how to run these tests")
