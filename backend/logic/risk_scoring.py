"""
Risk scoring system for fraud detection
Helper functions to analyze URLs, SMS, and transactions
"""
import re
from typing import List, Tuple, Dict
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Fraud indicators for different types
SUSPICIOUS_URL_PATTERNS = [
    r'bit\.ly', r'tinyurl\.com', r'goo\.gl',  # URL shorteners
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
    r'free', r'winner', r'claim', r'prize', r'lottery',  # Suspicious keywords
    r'urgent', r'verify', r'suspend', r'limited',
    r'click.*here', r'act.*now',
]

SUSPICIOUS_DOMAINS = [
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co',
    'paytm-secure', 'googlepay-verification', 'phonepe-kyc',
    'upi-verify', 'bank-alert', 'sbi-secure'
]

LEGITIMATE_DOMAINS = [
    'paytm.com', 'phonepe.com', 'google.com', 'googlepay.com',
    'sbi.co.in', 'hdfcbank.com', 'icicibank.com', 'axisbank.com'
]

SMS_FRAUD_KEYWORDS = [
    'congratulations', 'winner', 'won', 'prize', 'lottery', 'crore', 'lakh',
    'claim now', 'urgent', 'expire', 'verify', 'otp', 'password', 'pin',
    'block', 'suspend', 'limited time', 'act now', 'click here',
    'free gift', 'cashback', 'reward points', 'kyc', 'update required'
]

# Fake KYC SMS patterns (more specific)
FAKE_KYC_PATTERNS = [
    r'kyc.*updat',
    r'kyc.*expir',
    r'kyc.*pending',
    r'kyc.*verify',
    r'kyc.*complet',
    r'update.*kyc',
    r'verify.*kyc',
    r'complete.*kyc',
    r'kyc.*link',
    r'kyc.*click',
    r'kyc.*suspend',
    r'kyc.*block',
    r'kyc.*deadline',
    r'ekyc.*requir',
    r're-kyc',
]

# Phishing website indicators (advanced)
PHISHING_DOMAIN_KEYWORDS = [
    'verify', 'secure', 'update', 'confirm', 'account', 'login',
    'signin', 'bank', 'payment', 'wallet', 'support', 'help',
    'customer', 'service', 'alert', 'urgent', 'suspended',
    'blocked', 'security', 'authentication', 'validation'
]

# Typosquatting common targets
LEGITIMATE_DOMAINS_TYPOSQUATTING = [
    'paytm.com', 'phonepe.com', 'googlepay.com', 'google.com',
    'amazonpay.com', 'amazon.in', 'flipkart.com',
    'sbi.co.in', 'hdfcbank.com', 'icicibank.com', 'axisbank.com',
    'paytmbank.com', 'kotak.com', 'yesbank.in',
    'bharatpe.com', 'cred.club', 'mobikwik.com'
]

UPI_FRAUD_PATTERNS = [
    r'\d{10}@paytm',  # Personal UPI IDs
    r'[a-z]+\d+@',  # Random character + number combinations
    r'test@', r'demo@', r'fake@',
]

# Screen sharing apps that are commonly used in fraud
SCREEN_SHARING_APPS = [
    'anydesk', 'teamviewer', 'quicksupport', 'remotesupport',
    'supremo', 'ammyy', 'ultraviewer', 'remotepc', 'screenshare'
]

# Suspicious HTML patterns
SUSPICIOUS_HTML_PATTERNS = [
    r'<input[^>]*type=["\']password["\'][^>]*>',
    r'<input[^>]*name=["\']otp["\'][^>]*>',
    r'<input[^>]*name=["\']cvv["\'][^>]*>',
    r'<input[^>]*name=["\']card["\'][^>]*>',
    r'<form[^>]*action=["\']https?://[^"\'>]+["\'][^>]*>',
]


def calculate_url_risk_score(url: str) -> Tuple[float, List[str], Dict]:
    """
    Calculate risk score for a URL
    
    Args:
        url: URL to analyze
        
    Returns:
        Tuple of (risk_score, fraud_indicators, details)
    """
    risk_score = 0.0
    indicators = []
    details = {}
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()
        
        details['domain'] = domain
        details['has_https'] = parsed.scheme == 'https'
        
        # Check for HTTPS
        if parsed.scheme != 'https':
            risk_score += 20
            indicators.append("Non-HTTPS connection")
        
        # Check for IP address instead of domain
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            risk_score += 30
            indicators.append("IP address used instead of domain name")
        
        # Check for URL shorteners
        if any(shortener in domain for shortener in SUSPICIOUS_DOMAINS):
            risk_score += 25
            indicators.append("URL shortener or suspicious domain")
        
        # Check for suspicious keywords
        full_url = url.lower()
        suspicious_count = sum(1 for pattern in SUSPICIOUS_URL_PATTERNS 
                              if re.search(pattern, full_url, re.IGNORECASE))
        if suspicious_count > 0:
            risk_score += min(suspicious_count * 10, 30)
            indicators.append(f"Contains {suspicious_count} suspicious keywords")
        
        # Check for legitimate domains
        is_legitimate = any(legit in domain for legit in LEGITIMATE_DOMAINS)
        if is_legitimate:
            risk_score = max(0, risk_score - 30)
            details['is_known_legitimate'] = True
        
        # Check for multiple subdomains
        subdomain_count = domain.count('.') - 1
        if subdomain_count > 2:
            risk_score += 15
            indicators.append(f"Multiple subdomains ({subdomain_count})")
        
        # Check URL length
        if len(url) > 100:
            risk_score += 10
            indicators.append("Unusually long URL")
        
        # Advanced phishing detection: Check for phishing keywords in domain
        phishing_keyword_count = sum(1 for keyword in PHISHING_DOMAIN_KEYWORDS if keyword in domain)
        if phishing_keyword_count >= 2:
            risk_score += 30
            indicators.append(f"Phishing keywords in domain ({phishing_keyword_count} matches)")
        elif phishing_keyword_count == 1:
            risk_score += 15
            indicators.append("Phishing keyword in domain")
        
        # Typosquatting detection using edit distance
        typosquat_result = detect_typosquatting(domain)
        if typosquat_result['is_typosquatting']:
            risk_score += 50
            indicators.append(f"⚠️ Typosquatting: Looks like '{typosquat_result['similar_to']}' (similarity: {typosquat_result['similarity']:.0%})")
            details['typosquatting_detected'] = True
            details['similar_to_domain'] = typosquat_result['similar_to']
            details['typosquatting_similarity'] = typosquat_result['similarity']
        
        # Check for homograph attacks (unicode lookalikes)
        if has_homograph_attack(domain):
            risk_score += 45
            indicators.append("⚠️ Homograph attack detected (lookalike characters)")
        
        # Fake payment pages: Check path for payment-related terms
        payment_terms = ['payment', 'pay', 'checkout', 'cart', 'order', 'transaction']
        if any(term in path or term in query for term in payment_terms):
            if not is_legitimate:
                risk_score += 20
                indicators.append("Fake payment page on suspicious domain")
        
        details['risk_factors'] = len(indicators)
        
    except Exception as e:
        logger.error(f"Error analyzing URL: {str(e)}")
        risk_score = 50
        indicators.append("Unable to parse URL")
    
    return min(risk_score, 100), indicators, details


def calculate_sms_risk_score(message: str, sender: str = None) -> Tuple[float, List[str], Dict]:
    """
    Calculate risk score for an SMS message
    
    Args:
        message: SMS content
        sender: Sender ID or phone number
        
    Returns:
        Tuple of (risk_score, fraud_indicators, details)
    """
    risk_score = 0.0
    indicators = []
    details = {}
    
    message_lower = message.lower()
    
    # Fake KYC SMS Detection
    is_fake_kyc, kyc_confidence, kyc_warning = analyze_fake_kyc_sms(message)
    if is_fake_kyc:
        risk_score += kyc_confidence * 0.8  # Use 80% of confidence as risk score
        indicators.append(kyc_warning)
        details['fake_kyc_detected'] = True
        details['kyc_confidence'] = kyc_confidence
    
    # Extract URLs
    urls = extract_urls_from_text(message)
    details['url_count'] = len(urls)
    
    if urls:
        indicators.append(f"Contains {len(urls)} URL(s)")
        risk_score += len(urls) * 15
        
        # Analyze each URL
        for url in urls:
            url_score, _, _ = calculate_url_risk_score(url)
            if url_score > 50:
                risk_score += 20
                indicators.append(f"High-risk URL detected: {url[:30]}...")
    
    # Extract UPI IDs
    upi_ids = extract_upi_ids(message)
    details['upi_count'] = len(upi_ids)
    
    if upi_ids:
        for upi in upi_ids:
            if any(re.search(pattern, upi) for pattern in UPI_FRAUD_PATTERNS):
                risk_score += 25
                indicators.append(f"Suspicious UPI ID: {upi}")
    
    # Check for fraud keywords
    fraud_keyword_count = sum(1 for keyword in SMS_FRAUD_KEYWORDS 
                              if keyword in message_lower)
    if fraud_keyword_count > 0:
        risk_score += min(fraud_keyword_count * 8, 40)
        indicators.append(f"Contains {fraud_keyword_count} fraud-related keywords")
    
    details['fraud_keywords_found'] = fraud_keyword_count
    
    # Check sender
    if sender:
        details['sender'] = sender
        # Suspicious sender patterns
        if re.match(r'^[A-Z]{2}-[A-Z]+$', sender):  # VK-REWARD, AM-PRIZE
            if any(word in sender.upper() for word in ['REWARD', 'PRIZE', 'WIN', 'GIFT']):
                risk_score += 20
                indicators.append("Suspicious sender ID pattern")
        elif re.match(r'^\d{10}$', sender):  # 10-digit number
            risk_score += 10
            indicators.append("Message from personal number")
    
    # Check for urgency
    urgency_words = ['urgent', 'immediately', 'expire', 'within', 'hours', 'today']
    if any(word in message_lower for word in urgency_words):
        risk_score += 15
        indicators.append("Creates sense of urgency")
    
    # Check for personal info requests
    personal_info = ['otp', 'password', 'pin', 'cvv', 'card number', 'expiry']
    if any(info in message_lower for info in personal_info):
        risk_score += 30
        indicators.append("Requests sensitive personal information")
    
    details['risk_factors'] = len(indicators)
    
    return min(risk_score, 100), indicators, details


def calculate_transaction_risk_score(
    amount: float,
    recipient_upi: str,
    recipient_name: str = None,
    note: str = None
) -> Tuple[float, List[str], Dict]:
    """
    Calculate risk score for a UPI transaction
    
    Args:
        amount: Transaction amount
        recipient_upi: Recipient UPI ID
        recipient_name: Display name of recipient
        note: Transaction note
        
    Returns:
        Tuple of (risk_score, fraud_indicators, details)
    """
    risk_score = 0.0
    indicators = []
    details = {}
    
    details['amount'] = amount
    details['recipient_upi'] = recipient_upi
    
    # Check amount
    if amount > 50000:
        risk_score += 20
        indicators.append(f"Large amount: ₹{amount:,.2f}")
    elif amount > 10000:
        risk_score += 10
        indicators.append(f"Medium-high amount: ₹{amount:,.2f}")
    
    # Check UPI ID patterns
    upi_lower = recipient_upi.lower()
    
    # Personal mobile number UPIs (higher risk for unknown recipients)
    if re.match(r'\d{10}@', upi_lower):
        risk_score += 15
        indicators.append("Personal mobile number UPI")
    
    # Check for suspicious patterns
    for pattern in UPI_FRAUD_PATTERNS:
        if re.search(pattern, upi_lower):
            risk_score += 25
            indicators.append("Suspicious UPI ID pattern")
            break
    
    # Check for mismatched name and UPI
    if recipient_name and recipient_upi:
        name_parts = recipient_name.lower().split()
        upi_prefix = recipient_upi.split('@')[0].lower()
        
        # Simple check: if name doesn't appear in UPI
        name_match = any(part in upi_prefix for part in name_parts if len(part) > 2)
        if not name_match and not any(provider in upi_lower for provider in ['paytm', 'phonepe', 'googlepay']):
            risk_score += 15
            indicators.append("Name doesn't match UPI ID")
        
        details['name_upi_mismatch'] = not name_match
    
    # Check transaction note for suspicious keywords
    if note:
        note_lower = note.lower()
        suspicious_note_keywords = ['urgent', 'help', 'emergency', 'please', 'family']
        if any(keyword in note_lower for keyword in suspicious_note_keywords):
            risk_score += 10
            indicators.append("Suspicious transaction note")
    
    # Check UPI provider
    upi_provider = recipient_upi.split('@')[-1] if '@' in recipient_upi else None
    details['upi_provider'] = upi_provider
    
    known_providers = ['paytm', 'phonepe', 'googlepay', 'okhdfcbank', 'okicici', 'okaxis', 'sbi', 'ybl']
    if upi_provider and not any(provider in upi_provider for provider in known_providers):
        risk_score += 10
        indicators.append("Unknown UPI provider")
    
    details['risk_factors'] = len(indicators)
    
    return min(risk_score, 100), indicators, details


def analyze_qr_code(qr_data: str) -> Tuple[float, List[str], Dict]:
    """
    Analyze QR code data for fraud indicators
    
    Args:
        qr_data: Data extracted from QR code
        
    Returns:
        Tuple of (risk_score, fraud_indicators, details)
    """
    risk_score = 0.0
    indicators = []
    details = {'qr_type': 'unknown'}
    
    if not qr_data:
        return risk_score, indicators, details
    
    qr_lower = qr_data.lower()
    
    # Check if it's a UPI intent
    if qr_lower.startswith('upi://') or 'upi:' in qr_lower:
        details['qr_type'] = 'upi_intent'
        
        # FAKE COLLECT REQUEST DETECTION (High Priority)
        is_collect, collect_warning = analyze_fake_collect_request(qr_data)
        if is_collect:
            risk_score += 70
            indicators.append(collect_warning)
            details['is_collect_request'] = True
            details['critical_warning'] = collect_warning
        
        # Extract UPI parameters
        if 'am=' in qr_lower:
            import re
            amount_match = re.search(r'am=([\d.]+)', qr_lower)
            if amount_match:
                amount = float(amount_match.group(1))
                details['amount'] = amount
                if amount > 10000:
                    risk_score += 20
                    indicators.append(f"High amount in QR: ₹{amount}")
        
        # Check for suspicious UPI IDs
        if 'pa=' in qr_lower:
            import re
            upi_match = re.search(r'pa=([^&]+)', qr_lower)
            if upi_match:
                upi_id = upi_match.group(1)
                details['upi_id'] = upi_id
                if re.match(r'\d{10}@', upi_id):
                    risk_score += 15
                    indicators.append("Personal phone number UPI in QR")
    
    # Check if it's a URL
    elif qr_lower.startswith('http://') or qr_lower.startswith('https://'):
        details['qr_type'] = 'url'
        url_score, url_indicators, _ = calculate_url_risk_score(qr_data)
        risk_score += url_score * 0.8  # URLs in QR codes are slightly less risky
        indicators.extend([f"QR URL: {ind}" for ind in url_indicators])
    
    # Check for suspicious patterns
    if any(word in qr_lower for word in ['verify', 'urgent', 'claim', 'prize']):
        risk_score += 15
        indicators.append("Suspicious keywords in QR code")
    
    return min(risk_score, 100), indicators, details


def analyze_domain_details(domain_info: Dict) -> Tuple[float, List[str]]:
    """
    Analyze domain registration details
    
    Args:
        domain_info: Domain details including registrar, dates, SSL info
        
    Returns:
        Tuple of (risk_score, fraud_indicators)
    """
    risk_score = 0.0
    indicators = []
    
    if not domain_info:
        return risk_score, indicators
    
    # Check SSL validity
    if domain_info.get('ssl_valid') is False:
        risk_score += 30
        indicators.append("Invalid or expired SSL certificate")
    
    # Check domain age
    if domain_info.get('creation_date'):
        from datetime import datetime
        try:
            creation_date = datetime.fromisoformat(domain_info['creation_date'].replace('Z', '+00:00'))
            age_days = (datetime.now() - creation_date).days
            
            if age_days < 30:
                risk_score += 40
                indicators.append(f"Very new domain ({age_days} days old)")
            elif age_days < 90:
                risk_score += 25
                indicators.append(f"Recently created domain ({age_days} days old)")
        except:
            pass
    
    # Check SSL issuer
    ssl_issuer = domain_info.get('ssl_issuer', '').lower()
    if ssl_issuer and 'let\'s encrypt' in ssl_issuer:
        # Not inherently bad, but commonly used by scammers for quick setup
        risk_score += 5
    
    return risk_score, indicators


def analyze_html_content(html_analysis: Dict) -> Tuple[float, List[str]]:
    """
    Analyze HTML content for fake forms and malicious patterns
    
    Args:
        html_analysis: HTML content analysis data
        
    Returns:
        Tuple of (risk_score, fraud_indicators)
    """
    risk_score = 0.0
    indicators = []
    
    if not html_analysis:
        return risk_score, indicators
    
    # Check for payment forms
    if html_analysis.get('has_payment_forms'):
        risk_score += 20
        indicators.append("Contains payment form")
    
    # Check for password fields
    if html_analysis.get('has_password_fields'):
        risk_score += 15
        indicators.append("Contains password input fields")
    
    # Check for OTP fields
    if html_analysis.get('has_otp_fields'):
        risk_score += 25
        indicators.append("Requests OTP/PIN (potential phishing)")
    
    # Check for external scripts
    external_scripts = html_analysis.get('external_scripts', [])
    if len(external_scripts) > 10:
        risk_score += 15
        indicators.append(f"Many external scripts loaded ({len(external_scripts)})")
    
    # Check suspicious patterns
    suspicious = html_analysis.get('suspicious_patterns', [])
    if suspicious:
        risk_score += len(suspicious) * 10
        indicators.extend([f"Suspicious HTML: {p}" for p in suspicious[:3]])
    
    return min(risk_score, 100), indicators


def analyze_redirect_chain(redirect_data: Dict) -> Tuple[float, List[str]]:
    """
    Analyze redirect patterns for fraud
    
    Args:
        redirect_data: Redirect chain information
        
    Returns:
        Tuple of (risk_score, fraud_indicators)
    """
    risk_score = 0.0
    indicators = []
    
    if not redirect_data:
        return risk_score, indicators
    
    redirect_count = redirect_data.get('count', 0)
    redirects = redirect_data.get('redirects', [])
    
    # Multiple redirects are suspicious
    if redirect_count > 3:
        risk_score += 30
        indicators.append(f"Many redirects ({redirect_count}) - potential hiding")
    elif redirect_count > 1:
        risk_score += 15
        indicators.append(f"Multiple redirects ({redirect_count})")
    
    # Check if marked as suspicious
    if redirect_data.get('suspicious'):
        risk_score += 25
        indicators.append("Suspicious redirect pattern detected")
    
    # Check for domain changes in redirect chain
    if redirects:
        from urllib.parse import urlparse
        domains = [urlparse(url).netloc for url in redirects]
        unique_domains = set(domains)
        if len(unique_domains) > 2:
            risk_score += 20
            indicators.append(f"Redirects through {len(unique_domains)} different domains")
    
    return risk_score, indicators


def analyze_upi_intent(upi_data: Dict) -> Tuple[float, List[str], Dict]:
    """
    Analyze UPI intent for fraud indicators
    
    Args:
        upi_data: UPI intent data from mobile app
        
    Returns:
        Tuple of (risk_score, fraud_indicators, details)
    """
    risk_score = 0.0
    indicators = []
    details = {}
    
    if not upi_data:
        return risk_score, indicators, details
    
    intent_type = upi_data.get('intent_type', '')
    details['intent_type'] = intent_type
    
    # FAKE COLLECT REQUEST DETECTION (Critical)
    is_collect, collect_warning = analyze_fake_collect_request(upi_data)
    if is_collect:
        risk_score += 70
        indicators.append(collect_warning)
        details['is_collect_request'] = True
        details['critical_warning'] = collect_warning
    
    # Check amount
    amount = upi_data.get('amount')
    if amount:
        details['amount'] = amount
        if amount > 50000:
            risk_score += 25
            indicators.append(f"Very high amount: ₹{amount:,.2f}")
        elif amount > 10000:
            risk_score += 15
            indicators.append(f"High amount: ₹{amount:,.2f}")
    
    # Check UPI ID
    payee_address = upi_data.get('payee_address', '')
    if payee_address:
        details['payee_address'] = payee_address
        if re.match(r'\d{10}@', payee_address):
            risk_score += 15
            indicators.append("Personal phone number UPI (not merchant)")
        
        for pattern in UPI_FRAUD_PATTERNS:
            if re.search(pattern, payee_address.lower()):
                risk_score += 20
                indicators.append("Suspicious UPI ID pattern")
                break
    
    # Check transaction note
    note = upi_data.get('transaction_note', '')
    if note:
        note_lower = note.lower()
        if any(word in note_lower for word in ['urgent', 'help', 'emergency', 'prize', 'refund']):
            risk_score += 15
            indicators.append("Suspicious transaction note")
    
    return min(risk_score, 100), indicators, details


def analyze_device_security(device_info: Dict) -> Tuple[float, List[str], Dict]:
    """
    Analyze device security indicators
    
    Args:
        device_info: Device information from mobile app
        
    Returns:
        Tuple of (risk_score, fraud_indicators, details)
    """
    risk_score = 0.0
    indicators = []
    details = {}
    
    if not device_info:
        return risk_score, indicators, details
    
    # Check for new device
    if device_info.get('is_new_device'):
        risk_score += 20
        indicators.append("⚠️ Transaction from NEW DEVICE")
        details['new_device_warning'] = True
    
    # Check for recent SIM change
    if device_info.get('sim_changed_recently'):
        risk_score += 40
        indicators.append("🚨 CRITICAL: Recent SIM card change detected")
        details['sim_swap_alert'] = True
        
        last_change = device_info.get('last_sim_change')
        if last_change:
            details['sim_change_date'] = last_change
    
    # Check for screen sharing apps
    screen_sharing_apps = device_info.get('screen_sharing_apps_detected', [])
    if screen_sharing_apps:
        risk_score += 50
        indicators.append(f"🚨 CRITICAL: Screen sharing app detected: {', '.join(screen_sharing_apps)}")
        details['screen_sharing_apps'] = screen_sharing_apps
        details['screen_sharing_warning'] = "Someone may be controlling your device remotely"
    
    return min(risk_score, 100), indicators, details


def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    
    # Also check for common URL patterns without http
    simple_url_pattern = r'\b(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?\b'
    simple_urls = re.findall(simple_url_pattern, text)
    
    # Add http:// to simple URLs
    for url in simple_urls:
        if not url.startswith('http'):
            urls.append(f'http://{url}')
    
    return list(set(urls))


def extract_upi_ids(text: str) -> List[str]:
    """Extract UPI IDs from text"""
    upi_pattern = r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\b'
    potential_upis = re.findall(upi_pattern, text)
    
    # Filter out email addresses (basic check)
    upis = [upi for upi in potential_upis 
            if not any(domain in upi.lower() for domain in ['.com', '.in', '.org', '.net'])]
    
    return upis


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    # Indian phone numbers
    phone_pattern = r'\b(?:\+91|91)?[6-9]\d{9}\b'
    return re.findall(phone_pattern, text)


def get_risk_level(risk_score: float) -> str:
    """Convert risk score to risk level"""
    if risk_score >= 75:
        return "critical"
    elif risk_score >= 50:
        return "high"
    elif risk_score >= 25:
        return "medium"
    else:
        return "low"


def generate_recommendations(risk_score: float, indicators: List[str], analysis_type: str) -> List[str]:
    """Generate recommendations based on risk assessment"""
    recommendations = []
    
    if risk_score >= 75:
        recommendations.append("🚨 HIGH RISK: Do not proceed with this action")
        recommendations.append("Report this as potential fraud")
        
    elif risk_score >= 50:
        recommendations.append("⚠️ CAUTION: Verify carefully before proceeding")
        
    if analysis_type == "url":
        if "Non-HTTPS" in str(indicators):
            recommendations.append("Ensure website uses HTTPS encryption")
        if "shortener" in str(indicators).lower():
            recommendations.append("Avoid clicking shortened URLs from unknown sources")
        recommendations.append("Verify the website domain matches official sources")
        
    elif analysis_type == "sms":
        if "URL" in str(indicators):
            recommendations.append("Do not click links in unsolicited messages")
        if "personal information" in str(indicators).lower():
            recommendations.append("Never share OTP, PIN, or passwords via SMS")
        recommendations.append("Verify sender through official channels")
        
    elif analysis_type == "transaction":
        recommendations.append("Verify recipient identity through alternate channel")
        recommendations.append("Check if UPI ID belongs to known/trusted party")
        if risk_score > 30:
            recommendations.append("Consider using smaller test transaction first")
    
    if risk_score < 25:
        recommendations.append("✅ This appears relatively safe, but stay vigilant")
    
    return recommendations


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings
    Used for typosquatting detection
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def detect_typosquatting(domain: str) -> Dict:
    """
    Detect typosquatting by comparing domain with legitimate domains
    
    Args:
        domain: Domain to check
        
    Returns:
        Dictionary with typosquatting info
    """
    result = {
        'is_typosquatting': False,
        'similar_to': None,
        'similarity': 0.0,
        'edit_distance': 0
    }
    
    # Remove www. and extract base domain
    domain = domain.replace('www.', '')
    
    # Compare with legitimate domains
    for legit_domain in LEGITIMATE_DOMAINS_TYPOSQUATTING:
        distance = levenshtein_distance(domain, legit_domain)
        max_len = max(len(domain), len(legit_domain))
        similarity = 1 - (distance / max_len)
        
        # If very similar (80%+) but not exact match, it's typosquatting
        if similarity >= 0.80 and domain != legit_domain:
            if similarity > result['similarity']:
                result['is_typosquatting'] = True
                result['similar_to'] = legit_domain
                result['similarity'] = similarity
                result['edit_distance'] = distance
    
    # Also check for common typosquatting techniques
    if not result['is_typosquatting']:
        for legit_domain in LEGITIMATE_DOMAINS_TYPOSQUATTING:
            base = legit_domain.split('.')[0]
            
            # Character substitution (paytrn, paytm)
            if base in domain or domain in base:
                if domain != legit_domain:
                    result['is_typosquatting'] = True
                    result['similar_to'] = legit_domain
                    result['similarity'] = 0.85
                    break
            
            # Hyphen addition (pay-tm.com)
            if base.replace('-', '') in domain.replace('-', ''):
                if domain != legit_domain:
                    result['is_typosquatting'] = True
                    result['similar_to'] = legit_domain
                    result['similarity'] = 0.85
                    break
    
    return result


def has_homograph_attack(domain: str) -> bool:
    """
    Detect homograph attacks (unicode characters that look like ASCII)
    
    Args:
        domain: Domain to check
        
    Returns:
        True if homograph attack detected
    """
    # Common homograph pairs
    homograph_pairs = {
        'a': ['а', 'ạ', 'ă', 'ā'],  # Cyrillic and Latin variants
        'e': ['е', 'ē', 'ė', 'ę'],
        'o': ['о', 'ọ', 'ō', 'ő'],
        'p': ['р', 'ṗ'],
        'c': ['с', 'ċ', 'ć'],
        'x': ['х', 'ẋ'],
        'y': ['у', 'ȳ', 'ý'],
        'i': ['і', 'ı', 'ị'],
        'm': ['м', 'ṁ'],
        'n': ['п', 'ń', 'ň'],
    }
    
    # Check if domain contains any lookalike characters
    for char in domain:
        for ascii_char, lookalikes in homograph_pairs.items():
            if char in lookalikes:
                return True
    
    # Check for mixed script usage (ASCII + Cyrillic, etc.)
    has_ascii = any(ord(c) < 128 for c in domain)
    has_unicode = any(ord(c) >= 128 for c in domain)
    
    if has_ascii and has_unicode:
        return True
    
    return False


def analyze_fake_collect_request(upi_data: str) -> Tuple[bool, str]:
    """
    Specifically detect fake collect requests in UPI data
    
    Args:
        upi_data: UPI intent string or data
        
    Returns:
        Tuple of (is_collect_request, warning_message)
    """
    upi_lower = str(upi_data).lower()
    
    # Check for collect request indicators
    is_collect = any([
        'collect' in upi_lower,
        'mode=02' in upi_lower,  # UPI mode 02 is collect
        'mode=collect' in upi_lower,
    ])
    
    if is_collect:
        warning = (
            "🚨 DANGER: This is a COLLECT REQUEST! "
            "Money will be DEDUCTED from YOUR account, not sent to someone. "
            "Scammers use fake collect QR codes to steal money. DO NOT APPROVE!"
        )
        return True, warning
    
    return False, ""


def analyze_fake_kyc_sms(message: str) -> Tuple[bool, int, str]:
    """
    Specifically detect fake KYC SMS scams
    
    Args:
        message: SMS message content
        
    Returns:
        Tuple of (is_fake_kyc, confidence_score, warning_message)
    """
    message_lower = message.lower()
    
    # Count KYC pattern matches
    pattern_matches = sum(1 for pattern in FAKE_KYC_PATTERNS if re.search(pattern, message_lower))
    
    if pattern_matches > 0:
        # Check for additional red flags
        red_flags = []
        
        if any(url in message_lower for url in ['bit.ly', 'tinyurl', 'goo.gl']):
            red_flags.append("shortened URL")
        
        if re.search(r'\d{10}', message):  # Contains phone number
            red_flags.append("phone number")
        
        if any(word in message_lower for word in ['urgent', 'immediately', 'expire', 'block', 'suspend']):
            red_flags.append("urgency tactics")
        
        if any(word in message_lower for word in ['click', 'link', 'download', 'install']):
            red_flags.append("action request")
        
        confidence = min((pattern_matches * 25) + (len(red_flags) * 15), 100)
        
        warning = (
            f"🚨 FAKE KYC SCAM DETECTED (Confidence: {confidence}%)! "
            f"Banks NEVER ask you to update KYC via SMS links. "
            f"Visit your bank branch or official app directly. "
            f"Red flags: {', '.join(red_flags) if red_flags else 'KYC keywords'}"
        )
        
        return True, confidence, warning
    
    return False, 0, ""
