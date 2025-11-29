"""
Google Gemini AI Integration for Enhanced Fraud Detection
Uses Gemini Pro to analyze suspicious content with AI reasoning
"""

import logging
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """
    Gemini AI analyzer for fraud detection
    Provides AI-powered analysis of URLs, SMS, and transactions
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """
        Initialize Gemini analyzer
        
        Args:
            api_key: Gemini API key (uses settings if not provided)
            model: Model name (defaults to gemini-pro)
        """
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model or settings.gemini_model
        self.enabled = settings.gemini_enabled and bool(self.api_key)
        
        if self.enabled:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini AI initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
                self.enabled = False
        else:
            logger.warning("Gemini AI is disabled (no API key or enabled=False)")
    
    def analyze_url(
        self,
        url: str,
        domain_details: Optional[Dict] = None,
        html_content: Optional[Dict] = None
    ) -> Tuple[float, List[str], Dict]:
        """
        AI analysis of URL for phishing/fraud
        
        Args:
            url: URL to analyze
            domain_details: Optional domain information
            html_content: Optional HTML content analysis
            
        Returns:
            Tuple of (ai_risk_score, ai_indicators, ai_details)
        """
        if not self.enabled:
            return 0.0, [], {}
        
        try:
            # Build comprehensive prompt
            prompt = f"""You are a cybersecurity expert analyzing URLs for fraud and phishing.

URL to analyze: {url}

Additional context:
"""
            if domain_details:
                prompt += f"- Domain age: {domain_details.get('creation_date', 'Unknown')}\n"
                prompt += f"- SSL valid: {domain_details.get('ssl_valid', 'Unknown')}\n"
            
            if html_content:
                prompt += f"- Has payment forms: {html_content.get('has_payment_forms', False)}\n"
                prompt += f"- Has OTP fields: {html_content.get('has_otp_fields', False)}\n"
                prompt += f"- Has password fields: {html_content.get('has_password_fields', False)}\n"
            
            prompt += """
Analyze this URL and provide:
1. Risk score (0-100, where 100 is maximum risk)
2. List of specific fraud indicators found
3. Type of fraud (phishing, fake payment, typosquatting, etc.)
4. Confidence level (low/medium/high)
5. Reasoning for the risk assessment

Format your response as JSON:
{
    "risk_score": <number 0-100>,
    "fraud_indicators": ["indicator1", "indicator2", ...],
    "fraud_type": "<type>",
    "confidence": "<low/medium/high>",
    "reasoning": "<explanation>"
}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            risk_score = result.get('risk_score', 0.0)
            indicators = result.get('fraud_indicators', [])
            indicators = [f"🤖 AI: {ind}" for ind in indicators]
            
            details = {
                'ai_fraud_type': result.get('fraud_type'),
                'ai_confidence': result.get('confidence'),
                'ai_reasoning': result.get('reasoning'),
                'ai_enabled': True
            }
            
            logger.info(f"Gemini analysis for {url}: score={risk_score}, confidence={details['ai_confidence']}")
            return risk_score, indicators, details
            
        except Exception as e:
            logger.error(f"Gemini URL analysis error: {str(e)}")
            return 0.0, [], {'ai_error': str(e)}
    
    def analyze_sms(
        self,
        message: str,
        sender: Optional[str] = None
    ) -> Tuple[float, List[str], Dict]:
        """
        AI analysis of SMS for fraud patterns
        
        Args:
            message: SMS content
            sender: Sender ID or number
            
        Returns:
            Tuple of (ai_risk_score, ai_indicators, ai_details)
        """
        if not self.enabled:
            return 0.0, [], {}
        
        try:
            prompt = f"""You are a fraud detection expert analyzing SMS messages for scams.

SMS Message: "{message}"
Sender: {sender or "Unknown"}

Common SMS fraud types in India:
- Fake KYC updates
- Prize/lottery scams
- Impersonation of banks
- OTP/password requests
- Screen sharing app installation requests
- Fake customer support
- Refund scams

Analyze this SMS and provide:
1. Risk score (0-100)
2. Specific fraud indicators
3. Type of scam (if any)
4. Red flags present
5. Confidence level

Format as JSON:
{{
    "risk_score": <number>,
    "fraud_indicators": ["indicator1", "indicator2"],
    "scam_type": "<type>",
    "red_flags": ["flag1", "flag2"],
    "confidence": "<low/medium/high>",
    "reasoning": "<explanation>"
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            risk_score = result.get('risk_score', 0.0)
            indicators = result.get('fraud_indicators', [])
            red_flags = result.get('red_flags', [])
            all_indicators = [f"🤖 AI: {ind}" for ind in indicators + red_flags]
            
            details = {
                'ai_scam_type': result.get('scam_type'),
                'ai_confidence': result.get('confidence'),
                'ai_reasoning': result.get('reasoning'),
                'ai_enabled': True
            }
            
            return risk_score, all_indicators, details
            
        except Exception as e:
            logger.error(f"Gemini SMS analysis error: {str(e)}")
            return 0.0, [], {'ai_error': str(e)}
    
    def analyze_transaction(
        self,
        amount: float,
        recipient_upi: str,
        recipient_name: Optional[str] = None,
        note: Optional[str] = None,
        is_new_payee: bool = False
    ) -> Tuple[float, List[str], Dict]:
        """
        AI analysis of UPI transaction for fraud
        
        Args:
            amount: Transaction amount
            recipient_upi: UPI ID
            recipient_name: Display name
            note: Transaction note
            is_new_payee: Whether this is first transaction
            
        Returns:
            Tuple of (ai_risk_score, ai_indicators, ai_details)
        """
        if not self.enabled:
            return 0.0, [], {}
        
        try:
            prompt = f"""You are a financial fraud expert analyzing UPI transactions.

Transaction Details:
- Amount: ₹{amount:,.2f}
- Recipient UPI: {recipient_upi}
- Recipient Name: {recipient_name or "Not provided"}
- Transaction Note: {note or "None"}
- New Payee: {"Yes (First time)" if is_new_payee else "No (Known payee)"}

Common UPI fraud patterns:
- Personal mobile UPIs (10 digits before @)
- Name-UPI mismatch
- Suspicious transaction notes (urgent, help, emergency)
- Large amounts to new/unknown recipients
- Test/demo/fake UPIs
- Unusual UPI providers

Analyze this transaction and provide:
1. Risk score (0-100)
2. Fraud indicators
3. Red flags
4. Whether to proceed or block
5. Confidence level

Format as JSON:
{{
    "risk_score": <number>,
    "fraud_indicators": ["indicator1"],
    "red_flags": ["flag1"],
    "recommendation": "proceed/caution/block",
    "confidence": "<low/medium/high>",
    "reasoning": "<explanation>"
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            risk_score = result.get('risk_score', 0.0)
            indicators = result.get('fraud_indicators', [])
            red_flags = result.get('red_flags', [])
            all_indicators = [f"🤖 AI: {ind}" for ind in indicators + red_flags]
            
            details = {
                'ai_recommendation': result.get('recommendation'),
                'ai_confidence': result.get('confidence'),
                'ai_reasoning': result.get('reasoning'),
                'ai_enabled': True
            }
            
            return risk_score, all_indicators, details
            
        except Exception as e:
            logger.error(f"Gemini transaction analysis error: {str(e)}")
            return 0.0, [], {'ai_error': str(e)}
    
    def analyze_qr_code(
        self,
        qr_data: str,
        qr_type: str
    ) -> Tuple[float, List[str], Dict]:
        """
        AI analysis of QR code for fraud
        
        Args:
            qr_data: QR code content
            qr_type: Type of QR (upi_intent, url, text)
            
        Returns:
            Tuple of (ai_risk_score, ai_indicators, ai_details)
        """
        if not self.enabled:
            return 0.0, [], {}
        
        try:
            prompt = f"""You are a fraud detection expert analyzing QR codes.

QR Code Data: {qr_data}
QR Type: {qr_type}

Common QR code frauds:
- Fake collect requests (steals money FROM user)
- Fake UPI payment QR codes
- Phishing website links
- Malicious URLs
- Fake merchant QR codes

Critical: If this is a UPI collect request (mode=02 or 'collect' in data), it's HIGH RISK.

Analyze and provide:
1. Risk score (0-100)
2. Fraud indicators
3. Type of fraud
4. Safety recommendation
5. Confidence level

Format as JSON:
{{
    "risk_score": <number>,
    "fraud_indicators": ["indicator1"],
    "fraud_type": "<type>",
    "recommendation": "<text>",
    "confidence": "<low/medium/high>",
    "reasoning": "<explanation>"
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            risk_score = result.get('risk_score', 0.0)
            indicators = result.get('fraud_indicators', [])
            indicators = [f"🤖 AI: {ind}" for ind in indicators]
            
            details = {
                'ai_fraud_type': result.get('fraud_type'),
                'ai_recommendation': result.get('recommendation'),
                'ai_confidence': result.get('confidence'),
                'ai_reasoning': result.get('reasoning'),
                'ai_enabled': True
            }
            
            return risk_score, indicators, details
            
        except Exception as e:
            logger.error(f"Gemini QR analysis error: {str(e)}")
            return 0.0, [], {'ai_error': str(e)}
    
    def explain_fraud(
        self,
        fraud_type: str,
        indicators: List[str],
        risk_score: float
    ) -> str:
        """
        Get AI explanation of why something was flagged as fraud
        
        Args:
            fraud_type: Type of fraud detected
            indicators: List of fraud indicators
            risk_score: Risk score
            
        Returns:
            Human-readable explanation
        """
        if not self.enabled:
            return "AI analysis not available (Gemini disabled)"
        
        try:
            prompt = f"""You are explaining fraud detection to a user.

Fraud Type: {fraud_type}
Risk Score: {risk_score}/100
Detected Indicators:
{chr(10).join(f"- {ind}" for ind in indicators)}

Provide a clear, simple explanation:
1. What type of fraud this is
2. Why it's dangerous
3. How the scam typically works
4. What the user should do

Keep it concise (3-4 sentences) and user-friendly.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini explanation error: {str(e)}")
            return "Unable to generate AI explanation"
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response (handles JSON in markdown code blocks)"""
        import json
        import re
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            # Try to find JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse Gemini response as JSON: {response_text[:100]}")
            return {}


# Global instance
gemini_analyzer = GeminiAnalyzer()
