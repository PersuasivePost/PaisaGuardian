"""
Test examples for the Fraud Detection API
Run these after starting the server to verify functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Example JWT token - replace with real token from your auth server
TOKEN = "your-jwt-token-here"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_public_url_analysis():
    """Test public URL analysis (no auth required)"""
    print("Testing public URL analysis...")
    
    test_urls = [
        "https://google.com",
        "http://bit.ly/suspicious",
        "http://192.168.1.1/payment",
        "https://paytm-secure-verify.com/kyc"
    ]
    
    for url in test_urls:
        print(f"\nAnalyzing: {url}")
        response = requests.post(
            f"{BASE_URL}/api/analyze/url/public",
            json={"url": url}
        )
        result = response.json()
        print(f"Risk Level: {result['risk_level']}")
        print(f"Risk Score: {result['risk_score']}")
        print(f"Is Safe: {result['is_safe']}")
        if result['fraud_indicators']:
            print(f"Indicators: {', '.join(result['fraud_indicators'])}")
        print("-" * 60)

def test_authenticated_url_analysis():
    """Test authenticated URL analysis"""
    print("\nTesting authenticated URL analysis...")
    
    if TOKEN == "your-jwt-token-here":
        print("⚠️  Please set a valid JWT token in TOKEN variable")
        return
    
    response = requests.post(
        f"{BASE_URL}/api/analyze/url",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "url": "https://suspicious-website.com/payment",
            "user_id": "test_user",
            "context": "email"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_sms_analysis():
    """Test SMS analysis"""
    print("\nTesting SMS analysis...")
    
    if TOKEN == "your-jwt-token-here":
        print("⚠️  Please set a valid JWT token in TOKEN variable")
        return
    
    test_messages = [
        {
            "message": "Congratulations! You have won 1 crore rupees. Click here to claim: bit.ly/win123",
            "sender": "VK-REWARD"
        },
        {
            "message": "Your OTP is 123456. Do not share with anyone.",
            "sender": "SBIINB"
        },
        {
            "message": "Payment of Rs. 500 received from merchant@paytm",
            "sender": "PAYTM"
        }
    ]
    
    for msg in test_messages:
        print(f"\nAnalyzing SMS from {msg['sender']}:")
        print(f"Message: {msg['message'][:50]}...")
        
        response = requests.post(
            f"{BASE_URL}/api/analyze/sms",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json=msg
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Risk Level: {result['risk_level']}")
            print(f"Risk Score: {result['risk_score']}")
            print(f"Extracted URLs: {result['extracted_urls']}")
            print(f"Extracted UPI IDs: {result['extracted_upi_ids']}")
        else:
            print(f"Error: {response.status_code}")
        print("-" * 60)

def test_transaction_analysis():
    """Test transaction analysis"""
    print("\nTesting transaction analysis...")
    
    if TOKEN == "your-jwt-token-here":
        print("⚠️  Please set a valid JWT token in TOKEN variable")
        return
    
    test_transactions = [
        {
            "transaction": {
                "amount": 5000.0,
                "recipient_upi": "merchant@paytm",
                "recipient_name": "Amazon Pay",
                "transaction_note": "Order payment"
            }
        },
        {
            "transaction": {
                "amount": 75000.0,
                "recipient_upi": "9876543210@paytm",
                "recipient_name": "Unknown Person",
                "transaction_note": "Urgent help needed"
            }
        }
    ]
    
    for txn_data in test_transactions:
        txn = txn_data["transaction"]
        print(f"\nAnalyzing transaction:")
        print(f"Amount: ₹{txn['amount']}")
        print(f"Recipient: {txn['recipient_upi']}")
        
        response = requests.post(
            f"{BASE_URL}/api/analyze/transaction",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json=txn_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Risk Level: {result['risk_level']}")
            print(f"Risk Score: {result['risk_score']}")
            print(f"Is Safe: {result['is_safe']}")
            if result['warnings']:
                print(f"Warnings: {', '.join(result['warnings'])}")
        else:
            print(f"Error: {response.status_code}")
        print("-" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("Fraud Detection API - Test Suite")
    print("=" * 60)
    print("\nMake sure the API server is running on http://localhost:8000\n")
    
    try:
        # Run tests
        test_health_check()
        test_public_url_analysis()
        
        # Authenticated tests (will skip if no token)
        test_authenticated_url_analysis()
        test_sms_analysis()
        test_transaction_analysis()
        
        print("\n" + "=" * 60)
        print("Tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Please ensure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
