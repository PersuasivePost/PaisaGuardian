"""
🟧 LAYER 3: REASONING LAYER (The "AI Brain")
ML-based reasoning with NLP, domain similarity, and behavioral anomaly detection
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import math

logger = logging.getLogger(__name__)


# ============================================================
# (A) RULE-BASED REASONING ENGINE
# ============================================================

class RuleBasedEngine:
    """
    Fast, deterministic rule-based fraud detection
    Returns a weighted score based on pattern matching
    """
    
    # Fraud keywords with their risk weights
    SMS_FRAUD_KEYWORDS = {
        # High risk (40 points each)
        'account blocked': 40,
        'suspended': 40,
        'verify now': 40,
        'urgent action': 40,
        'click here immediately': 40,
        'confirm your identity': 40,
        'update kyc': 40,
        'refund pending': 40,
        'claim your prize': 40,
        'won lottery': 40,
        
        # Medium risk (25 points each)
        'verify account': 25,
        'update details': 25,
        'confirm payment': 25,
        'link expired': 25,
        'last chance': 25,
        'act now': 25,
        'limited time': 25,
        
        # Low risk (15 points each)
        'click here': 15,
        'free gift': 15,
        'congratulations': 15,
    }
    
    URL_FRAUD_PATTERNS = {
        r'bit\.ly': 20,              # URL shortener
        r'tiny\.url': 20,
        r't\.co': 15,
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}': 30,  # IP address in URL
        r'\.tk$|\.ml$|\.ga$|\.cf$': 35,  # Free domains
        r'login|signin|verify|secure|account|update': 20,  # Suspicious words in domain
    }
    
    def analyze_sms(self, message: str, sender: Optional[str] = None) -> Tuple[float, List[str]]:
        """
        Analyze SMS content using rule-based patterns
        
        Returns:
            Tuple of (score, indicators)
        """
        score = 0.0
        indicators = []
        message_lower = message.lower()
        
        # Check fraud keywords
        for keyword, weight in self.SMS_FRAUD_KEYWORDS.items():
            if keyword in message_lower:
                score += weight
                indicators.append(f"Fraud keyword: '{keyword}'")
        
        # Check for urgency
        urgency_words = ['urgent', 'immediately', 'now', 'asap', 'hurry', 'quick']
        urgency_count = sum(1 for word in urgency_words if word in message_lower)
        if urgency_count >= 2:
            score += 30
            indicators.append("Multiple urgency words detected")
        
        # Check for suspicious sender patterns
        if sender:
            if re.match(r'^[A-Z]{2}-[A-Z]+$', sender):  # e.g., VK-REWARD
                score += 25
                indicators.append("Suspicious sender ID pattern")
            elif sender.startswith('+91') and len(sender) == 13:
                # Normal phone number, slight trust
                score -= 5
        
        # Check for URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        if urls:
            score += 20
            indicators.append(f"Contains {len(urls)} URL(s)")
        
        # Check for UPI IDs
        upi_ids = re.findall(r'[\w.-]+@[\w.-]+', message)
        if upi_ids:
            score += 15
            indicators.append(f"Contains UPI ID(s)")
        
        return score, indicators
    
    def analyze_url(self, url: str) -> Tuple[float, List[str]]:
        """
        Analyze URL using rule-based patterns
        
        Returns:
            Tuple of (score, indicators)
        """
        score = 0.0
        indicators = []
        
        # Check URL patterns
        for pattern, weight in self.URL_FRAUD_PATTERNS.items():
            if re.search(pattern, url, re.IGNORECASE):
                score += weight
                indicators.append(f"Suspicious URL pattern: {pattern}")
        
        # Check for HTTPS
        if not url.startswith('https://'):
            score += 25
            indicators.append("Not using HTTPS")
        
        # Check for multiple subdomains
        domain_part = url.split('//')[1].split('/')[0] if '//' in url else url.split('/')[0]
        subdomain_count = domain_part.count('.')
        if subdomain_count > 3:
            score += 20
            indicators.append(f"Excessive subdomains: {subdomain_count}")
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.xyz', '.top', '.work', '.click', '.loan']
        if any(url.endswith(tld) for tld in suspicious_tlds):
            score += 30
            indicators.append("Suspicious top-level domain")
        
        return score, indicators
    
    def analyze_upi_intent(self, intent_type: str, amount: Optional[float] = None) -> Tuple[float, List[str]]:
        """
        Analyze UPI intent
        
        Returns:
            Tuple of (score, indicators)
        """
        score = 0.0
        indicators = []
        
        # Collect requests are more suspicious than pay
        if intent_type == 'collect' or intent_type == 'upi_collect':
            score += 40
            indicators.append("UPI collect request (higher risk)")
        
        # High amount transactions
        if amount and amount > 10000:
            score += 25
            indicators.append(f"High amount transaction: ₹{amount}")
        
        if amount and amount > 50000:
            score += 35
            indicators.append(f"Very high amount: ₹{amount}")
        
        return score, indicators


# ============================================================
# (B) NLP REASONING ENGINE
# ============================================================

class NLPEngine:
    """
    Natural Language Processing for fraud detection
    Uses lightweight keyword analysis (can be upgraded to DistilBERT)
    """
    
    # Fraud phrases with confidence scores
    FRAUD_PHRASES = {
        'account will be blocked': 0.9,
        'verify your account': 0.8,
        'congratulations you have won': 0.9,
        'claim your prize': 0.85,
        'urgent verification required': 0.9,
        'kyc update required': 0.85,
        'refund will be processed': 0.8,
        'suspended due to': 0.9,
        'click to verify': 0.85,
        'confirm your details': 0.8,
        'unauthorized transaction detected': 0.7,
        'update your information': 0.75,
    }
    
    def analyze_text(self, text: str) -> Tuple[float, float, List[str]]:
        """
        Analyze text for fraud indicators using NLP
        
        Returns:
            Tuple of (nlp_score, confidence, detected_phrases)
        """
        text_lower = text.lower()
        detected_phrases = []
        max_confidence = 0.0
        total_score = 0.0
        
        # Check for fraud phrases
        for phrase, confidence in self.FRAUD_PHRASES.items():
            if phrase in text_lower:
                detected_phrases.append(phrase)
                max_confidence = max(max_confidence, confidence)
                total_score += confidence * 50  # Scale to 0-50 range
        
        # Sentiment analysis (simple version)
        fear_words = ['urgent', 'immediately', 'blocked', 'suspended', 'expired', 'limited']
        fear_count = sum(1 for word in fear_words if word in text_lower)
        
        if fear_count >= 2:
            total_score += 30
            detected_phrases.append(f"High fear sentiment ({fear_count} fear words)")
        
        # Cap the score
        nlp_score = min(total_score, 100)
        
        return nlp_score, max_confidence, detected_phrases
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text (URLs, phone numbers, UPI IDs)
        
        Returns:
            Dictionary with entity types and values
        """
        entities = {
            'urls': [],
            'phone_numbers': [],
            'upi_ids': [],
            'amounts': []
        }
        
        # Extract URLs
        entities['urls'] = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            text
        )
        
        # Extract phone numbers
        entities['phone_numbers'] = re.findall(r'\+?\d{10,13}', text)
        
        # Extract UPI IDs
        entities['upi_ids'] = re.findall(r'[\w.-]+@[\w.-]+', text)
        
        # Extract amounts
        amounts = re.findall(r'₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)', text)
        entities['amounts'] = [amt.replace(',', '') for amt in amounts]
        
        return entities


# ============================================================
# (C) DOMAIN SIMILARITY ENGINE
# ============================================================

class DomainSimilarityEngine:
    """
    Detect typosquatting and similar domains
    """
    
    # Known legitimate domains
    LEGITIMATE_DOMAINS = [
        'google.com', 'facebook.com', 'amazon.com', 'paytm.com',
        'phonepe.com', 'gpay.app', 'bharatpe.com', 'cred.club',
        'axis.com', 'icicibank.com', 'hdfcbank.com', 'sbi.co.in',
        'irctc.co.in', 'gov.in', 'nic.in'
    ]
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
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
    
    def jaro_winkler_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaro-Winkler similarity (0-1)"""
        return SequenceMatcher(None, s1, s2).ratio()
    
    def check_typosquatting(self, domain: str) -> Tuple[float, Optional[str], float]:
        """
        Check if domain is typosquatting a legitimate domain
        
        Returns:
            Tuple of (score, similar_domain, similarity)
        """
        # Extract domain name without TLD
        domain_clean = domain.lower().replace('www.', '').split('.')[0]
        
        best_match = None
        highest_similarity = 0.0
        score = 0.0
        
        for legit_domain in self.LEGITIMATE_DOMAINS:
            legit_clean = legit_domain.split('.')[0]
            
            # Calculate similarity
            similarity = self.jaro_winkler_similarity(domain_clean, legit_clean)
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = legit_domain
        
        # If very similar but not exact match, likely typosquatting
        if 0.7 < highest_similarity < 0.95:
            score = 40 + (highest_similarity - 0.7) * 200  # Scale: 40-90
        elif highest_similarity >= 0.95 and domain_clean != best_match.split('.')[0]:
            score = 60  # Very suspicious
        
        return score, best_match, highest_similarity
    
    def analyze_domain_age(self, creation_date: Optional[str]) -> Tuple[float, List[str]]:
        """
        Analyze domain age (new domains are riskier)
        
        Returns:
            Tuple of (score, indicators)
        """
        score = 0.0
        indicators = []
        
        if creation_date:
            # Parse date and check age
            # For MVP, we'll use simple heuristics
            # In production, use proper date parsing
            if 'days ago' in creation_date or 'day ago' in creation_date:
                score = 50
                indicators.append("Domain created very recently (days old)")
            elif 'month' in creation_date and not 'months' in creation_date:
                score = 40
                indicators.append("Domain created less than a month ago")
            elif 'months ago' in creation_date:
                months_match = re.search(r'(\d+)\s+months?', creation_date)
                if months_match and int(months_match.group(1)) < 6:
                    score = 30
                    indicators.append(f"Domain created recently ({creation_date})")
        
        return score, indicators


# ============================================================
# (D) BEHAVIORAL ANOMALY DETECTOR
# ============================================================

class BehavioralAnomalyDetector:
    """
    Detect unusual behavioral patterns
    """
    
    def analyze_transaction_behavior(
        self,
        amount: float,
        is_new_payee: bool,
        is_unusual_amount: bool,
        is_unusual_time: bool,
        transaction_velocity: int,
        typical_amount: Optional[float] = None
    ) -> Tuple[float, List[str]]:
        """
        Analyze transaction behavior for anomalies
        
        Returns:
            Tuple of (score, indicators)
        """
        score = 0.0
        indicators = []
        
        # New payee + high amount = risky
        if is_new_payee and amount > 5000:
            score += 35
            indicators.append("First time sending to this payee with high amount")
        elif is_new_payee:
            score += 15
            indicators.append("New payee")
        
        # Unusual amount
        if is_unusual_amount:
            if typical_amount and amount > typical_amount * 3:
                score += 40
                indicators.append(f"Amount 3x higher than typical (₹{typical_amount:.2f})")
            else:
                score += 25
                indicators.append("Unusual transaction amount")
        
        # Unusual time (e.g., 2 AM - 5 AM)
        if is_unusual_time:
            score += 20
            indicators.append("Transaction at unusual time")
        
        # High velocity (multiple transactions quickly)
        if transaction_velocity > 5:
            score += 30
            indicators.append(f"High transaction velocity: {transaction_velocity} in last hour")
        elif transaction_velocity > 3:
            score += 15
            indicators.append(f"Moderate transaction velocity: {transaction_velocity} in last hour")
        
        return score, indicators
    
    def analyze_device_security(
        self,
        is_new_device: bool,
        sim_changed_recently: bool,
        screen_sharing_apps: List[str]
    ) -> Tuple[float, List[str]]:
        """
        Analyze device security indicators
        
        Returns:
            Tuple of (score, indicators)
        """
        score = 0.0
        indicators = []
        
        # SIM swap detection
        if sim_changed_recently:
            score += 40
            indicators.append("SIM card changed recently - possible SIM swap fraud")
        
        # Screen sharing apps
        if screen_sharing_apps:
            score += 50
            indicators.append(f"Screen sharing apps detected: {', '.join(screen_sharing_apps)}")
        
        # New device
        if is_new_device:
            score += 20
            indicators.append("New device detected")
        
        return score, indicators


# ============================================================
# (E) RISK SCORE COMBINING MODULE
# ============================================================

class RiskCombiner:
    """
    Combine all risk signals into final score
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize with custom weights or defaults
        """
        self.weights = weights or {
            'rules_score': 0.50,
            'nlp_score': 0.30,
            'anomaly_score': 0.20,
        }
    
    def combine_scores(
        self,
        rules_score: float,
        nlp_score: float,
        anomaly_score: float,
        additional_scores: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Combine multiple risk scores into final risk score
        
        Returns:
            Final risk score (0-150, typically capped at 100)
        """
        # Base combination
        final_score = (
            rules_score * self.weights['rules_score'] +
            nlp_score * self.weights['nlp_score'] +
            anomaly_score * self.weights['anomaly_score']
        )
        
        # Add additional scores if provided
        if additional_scores:
            for score_name, score_value in additional_scores.items():
                weight = self.weights.get(score_name, 0.1)
                final_score += score_value * weight
        
        return final_score
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """Update combining weights (used in learning layer)"""
        self.weights.update(new_weights)


# ============================================================
# MAIN REASONING INTERFACE
# ============================================================

class ReasoningEngine:
    """
    Main reasoning interface combining all engines
    """
    
    def __init__(self):
        self.rule_engine = RuleBasedEngine()
        self.nlp_engine = NLPEngine()
        self.domain_engine = DomainSimilarityEngine()
        self.anomaly_detector = BehavioralAnomalyDetector()
        self.risk_combiner = RiskCombiner()
    
    def analyze_comprehensive(
        self,
        text: Optional[str] = None,
        url: Optional[str] = None,
        upi_data: Optional[Dict] = None,
        behavioral_data: Optional[Dict] = None,
        domain_data: Optional[Dict] = None
    ) -> Dict:
        """
        Comprehensive analysis using all reasoning engines
        
        Returns:
            Dictionary with all scores and indicators
        """
        result = {
            'rules_score': 0.0,
            'nlp_score': 0.0,
            'anomaly_score': 0.0,
            'domain_score': 0.0,
            'final_score': 0.0,
            'indicators': [],
            'detected_phrases': [],
            'entities': {}
        }
        
        # Rule-based analysis
        if text:
            rules_score, rules_indicators = self.rule_engine.analyze_sms(text)
            result['rules_score'] += rules_score
            result['indicators'].extend(rules_indicators)
        
        if url:
            url_score, url_indicators = self.rule_engine.analyze_url(url)
            result['rules_score'] += url_score
            result['indicators'].extend(url_indicators)
        
        if upi_data:
            upi_score, upi_indicators = self.rule_engine.analyze_upi_intent(
                upi_data.get('intent_type', ''),
                upi_data.get('amount')
            )
            result['rules_score'] += upi_score
            result['indicators'].extend(upi_indicators)
        
        # NLP analysis
        if text:
            nlp_score, confidence, phrases = self.nlp_engine.analyze_text(text)
            result['nlp_score'] = nlp_score
            result['detected_phrases'] = phrases
            result['entities'] = self.nlp_engine.extract_entities(text)
        
        # Domain analysis
        if domain_data:
            if 'domain' in domain_data:
                typo_score, similar_domain, similarity = self.domain_engine.check_typosquatting(
                    domain_data['domain']
                )
                result['domain_score'] += typo_score
                if similar_domain:
                    result['indicators'].append(
                        f"Similar to {similar_domain} (similarity: {similarity:.2f})"
                    )
            
            if 'creation_date' in domain_data:
                age_score, age_indicators = self.domain_engine.analyze_domain_age(
                    domain_data['creation_date']
                )
                result['domain_score'] += age_score
                result['indicators'].extend(age_indicators)
        
        # Behavioral analysis
        if behavioral_data:
            if 'transaction' in behavioral_data:
                tx_data = behavioral_data['transaction']
                tx_score, tx_indicators = self.anomaly_detector.analyze_transaction_behavior(
                    tx_data.get('amount', 0),
                    tx_data.get('is_new_payee', False),
                    tx_data.get('is_unusual_amount', False),
                    tx_data.get('is_unusual_time', False),
                    tx_data.get('transaction_velocity', 0),
                    tx_data.get('typical_amount')
                )
                result['anomaly_score'] += tx_score
                result['indicators'].extend(tx_indicators)
            
            if 'device' in behavioral_data:
                device_data = behavioral_data['device']
                device_score, device_indicators = self.anomaly_detector.analyze_device_security(
                    device_data.get('is_new_device', False),
                    device_data.get('sim_changed_recently', False),
                    device_data.get('screen_sharing_apps', [])
                )
                result['anomaly_score'] += device_score
                result['indicators'].extend(device_indicators)
        
        # Combine all scores
        result['final_score'] = self.risk_combiner.combine_scores(
            result['rules_score'],
            result['nlp_score'],
            result['anomaly_score'],
            {'domain_score': result['domain_score']}
        )
        
        return result


# Global reasoning engine instance
reasoning_engine = ReasoningEngine()
