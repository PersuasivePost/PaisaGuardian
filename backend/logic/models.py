"""
Pydantic models for fraud detection system
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudType(str, Enum):
    """Types of fraud that can be detected"""
    PHISHING = "phishing"
    MALWARE = "malware"
    FAKE_UPI = "fake_upi"
    SMS_SCAM = "sms_scam"
    IMPERSONATION = "impersonation"
    SOCIAL_ENGINEERING = "social_engineering"
    FAKE_WEBSITE = "fake_website"
    UNAUTHORIZED_TRANSACTION = "unauthorized_transaction"
    QR_CODE_FRAUD = "qr_code_fraud"
    FAKE_PAYMENT_FORM = "fake_payment_form"
    REDIRECT_FRAUD = "redirect_fraud"
    SCREEN_SHARING_SCAM = "screen_sharing_scam"
    SIM_SWAP_FRAUD = "sim_swap_fraud"


# Chrome Extension Analysis Models
class DomainDetails(BaseModel):
    """Domain information from Chrome extension"""
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiration_date: Optional[str] = None
    nameservers: Optional[List[str]] = None
    ssl_valid: Optional[bool] = None
    ssl_issuer: Optional[str] = None


class RedirectChain(BaseModel):
    """Redirect chain information"""
    redirects: List[str] = Field(default_factory=list, description="List of URLs in redirect chain")
    count: int = Field(0, description="Number of redirects")
    suspicious: bool = Field(False, description="Whether redirect pattern is suspicious")


class HTMLContentAnalysis(BaseModel):
    """HTML content analysis from page"""
    has_payment_forms: bool = False
    has_password_fields: bool = False
    has_otp_fields: bool = False
    external_scripts: List[str] = Field(default_factory=list)
    suspicious_patterns: List[str] = Field(default_factory=list)


class URLAnalysisRequest(BaseModel):
    """Request model for URL analysis from Chrome extension"""
    url: str = Field(..., description="URL to analyze for fraud")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    context: Optional[str] = Field(None, description="Context where URL was found (email, SMS, etc.)")
    
    # Chrome extension specific fields - PERCEPTION LAYER
    qr_code_data: Optional[str] = Field(None, description="Data from scanned QR code")
    domain_details: Optional[DomainDetails] = Field(None, description="Domain registration details")
    html_content: Optional[HTMLContentAnalysis] = Field(None, description="Analyzed HTML content")
    redirect_chain: Optional[RedirectChain] = Field(None, description="Redirect pattern data")
    page_title: Optional[str] = Field(None, description="Page title")
    favicon_url: Optional[str] = Field(None, description="Favicon URL")
    
    # Enhanced perception signals
    suspicious_keywords: List[str] = Field(default_factory=list, description="Suspicious keywords found on page")
    typosquatting_score: Optional[float] = Field(None, description="Typosquatting similarity score (0-1)")
    similar_to_domain: Optional[str] = Field(None, description="Domain this might be impersonating")
    page_load_time: Optional[float] = Field(None, description="Page load time in seconds")
    has_https: bool = Field(True, description="Whether URL uses HTTPS")
    certificate_valid: Optional[bool] = Field(None, description="SSL certificate validity")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/payment",
                "user_id": "user123",
                "context": "QR_CODE",
                "qr_code_data": "upi://pay?pa=merchant@paytm&pn=Store&am=500"
            }
        }


class URLAnalysisResponse(BaseModel):
    """Response model for URL analysis"""
    url: str
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=100, description="Risk score from 0-100")
    is_safe: bool
    fraud_indicators: List[str] = Field(default_factory=list)
    detected_fraud_types: List[FraudType] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict] = Field(default_factory=dict)
    
    # Chrome extension specific response fields
    qr_code_analysis: Optional[Dict] = None
    domain_risk_factors: Optional[List[str]] = None
    html_threats: Optional[List[str]] = None
    redirect_risk: Optional[str] = None


class FraudReportRequest(BaseModel):
    """Request model for reporting fraud by users"""
    entity_id: str = Field(..., description="The fraudulent entity (phone number, UPI ID, URL, etc.)")
    entity_type: str = Field(
        ...,
        description="Type of entity: phone_numbers, upi_ids, urls, senders, domains"
    )
    description: Optional[str] = Field(None, description="Description of the fraud incident")
    fraud_category: Optional[str] = Field(
        None,
        description="Category: phishing, fake_upi, sms_scam, impersonation, qr_code_fraud, etc."
    )
    amount_lost: Optional[float] = Field(None, ge=0, description="Amount lost in fraud (if any)")
    additional_info: Optional[Dict] = Field(
        default_factory=dict,
        description="Additional information (transaction ID, timestamps, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "+919876543210",
                "entity_type": "phone_numbers",
                "description": "Received SMS claiming to be from bank, asking for OTP",
                "fraud_category": "sms_scam",
                "amount_lost": 5000.0,
                "additional_info": {
                    "sms_content": "Your account will be blocked. Share OTP: XXXXX",
                    "bank_name": "HDFC Bank"
                }
            }
        }


class FraudReportResponse(BaseModel):
    """Response model for fraud report submission"""
    success: bool
    entity_id: str
    entity_type: str
    report_count: int = Field(..., description="Total number of reports for this entity")
    threshold: int = Field(..., description="Threshold for automatic blacklisting")
    blacklisted: bool = Field(..., description="Whether entity was automatically blacklisted")
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "entity_id": "+919876543210",
                "entity_type": "phone_numbers",
                "report_count": 52,
                "threshold": 50,
                "blacklisted": True,
                "message": "⚠️ ALERT: Entity automatically blacklisted after 52 fraud reports"
            }
        }


# Analysis History Models
class AnalysisHistoryItem(BaseModel):
    """Single analysis history entry"""
    id: str = Field(..., description="Unique analysis ID")
    analysis_type: str = Field(..., description="Type: url, sms, transaction, qr_code")
    entity: str = Field(..., description="Entity analyzed (URL, phone, UPI ID)")
    risk_level: RiskLevel
    risk_score: float
    is_safe: bool
    fraud_indicators: List[str] = Field(default_factory=list)
    timestamp: datetime
    user_action: Optional[str] = Field(None, description="User feedback: safe, fraud, blocked")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "analysis_type": "url",
                "entity": "https://suspicious-site.com",
                "risk_level": "high",
                "risk_score": 85.0,
                "is_safe": False,
                "fraud_indicators": ["Typosquatting detected", "Suspicious TLD"],
                "timestamp": "2025-11-29T10:30:00Z",
                "user_action": "blocked"
            }
        }


class AnalysisHistoryResponse(BaseModel):
    """Response for analysis history"""
    total_analyses: int
    analyses: List[AnalysisHistoryItem]
    filters: Dict[str, Any] = Field(default_factory=dict)
    

# Dashboard Models
class DashboardStats(BaseModel):
    """Dashboard overview statistics"""
    total_analyses: int = Field(..., description="Total fraud checks performed")
    analyses_today: int = Field(..., description="Analyses performed today")
    blocked_threats: int = Field(..., description="Total threats blocked")
    active_alerts: int = Field(..., description="Current active alerts")
    
    risk_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution by risk level: low, medium, high, critical"
    )
    
    analysis_by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by type: url, sms, transaction, qr_code"
    )
    
    recent_alerts: List[AnalysisHistoryItem] = Field(
        default_factory=list,
        description="Last 5 high-risk detections"
    )
    
    protection_rate: float = Field(
        0.0,
        description="Percentage of threats successfully blocked"
    )
    
    learning_accuracy: float = Field(
        0.0,
        description="ML model accuracy from user feedback"
    )


# User Settings Models
class RiskThresholds(BaseModel):
    """Risk threshold settings"""
    low: float = Field(40.0, ge=0, le=100, description="Low risk threshold (0-39 = safe)")
    medium: float = Field(70.0, ge=0, le=100, description="Medium risk threshold (40-69 = warn)")
    high: float = Field(100.0, ge=0, le=100, description="High risk threshold (70+ = block)")


class FeatureToggles(BaseModel):
    """Feature enable/disable settings"""
    url_analysis: bool = Field(True, description="Enable URL fraud detection")
    sms_analysis: bool = Field(True, description="Enable SMS fraud detection")
    transaction_analysis: bool = Field(True, description="Enable UPI transaction analysis")
    qr_code_scanning: bool = Field(True, description="Enable QR code fraud detection")
    auto_blocking: bool = Field(True, description="Automatically block high-risk threats")
    learning_mode: bool = Field(True, description="Learn from user feedback")
    notifications: bool = Field(True, description="Send fraud alerts")


class UserSettings(BaseModel):
    """User settings configuration"""
    risk_thresholds: RiskThresholds = Field(default_factory=RiskThresholds)
    features: FeatureToggles = Field(default_factory=FeatureToggles)
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email_alerts": True,
            "push_notifications": True,
            "sms_alerts": False
        }
    )
    auto_submit_feedback: bool = Field(
        False,
        description="Automatically submit feedback for blocked threats"
    )


class SettingsUpdateRequest(BaseModel):
    """Request to update user settings"""
    risk_thresholds: Optional[RiskThresholds] = None
    features: Optional[FeatureToggles] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    auto_submit_feedback: Optional[bool] = None


# QR Code Analysis Models
class QRCodeAnalysisRequest(BaseModel):
    """Request model for QR code analysis"""
    qr_data: str = Field(..., description="Raw data extracted from QR code")
    context: Optional[str] = Field(None, description="Context where QR was found")
    image_url: Optional[str] = Field(None, description="URL to QR code image")
    
    class Config:
        json_schema_extra = {
            "example": {
                "qr_data": "upi://pay?pa=merchant@paytm&pn=Store&am=500",
                "context": "Physical poster at store"
            }
        }


class QRCodeAnalysisResponse(BaseModel):
    """Response model for QR code analysis"""
    qr_data: str
    qr_type: str = Field(..., description="Type: upi_payment, url, text, unknown")
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=100)
    is_safe: bool
    fraud_indicators: List[str] = Field(default_factory=list)
    extracted_info: Dict = Field(default_factory=dict, description="Parsed QR data")
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    detected_fraud_types: List[FraudType] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict] = Field(default_factory=dict)
    
    # Chrome extension specific response fields
    qr_code_analysis: Optional[Dict] = None
    domain_risk_factors: Optional[List[str]] = None
    html_threats: Optional[List[str]] = None
    redirect_risk: Optional[str] = None


# Mobile App Analysis Models
class DeviceInfo(BaseModel):
    """Device information from mobile app"""
    device_id: Optional[str] = None
    is_new_device: bool = False
    sim_changed_recently: bool = False
    last_sim_change: Optional[datetime] = None
    screen_sharing_apps_detected: List[str] = Field(default_factory=list)
    device_model: Optional[str] = None
    os_version: Optional[str] = None


class UPIIntent(BaseModel):
    """UPI intent data from mobile app"""
    intent_type: str = Field(..., description="Type: upi_pay or upi_collect")
    payee_address: Optional[str] = None
    payee_name: Optional[str] = None
    amount: Optional[float] = None
    transaction_ref: Optional[str] = None
    transaction_note: Optional[str] = None
    merchant_code: Optional[str] = None


class SMSAnalysisRequest(BaseModel):
    """Request model for SMS analysis from mobile app"""
    message: str = Field(..., description="SMS message content to analyze")
    sender: Optional[str] = Field(None, description="Sender ID or phone number")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    timestamp: Optional[datetime] = Field(None, description="When SMS was received")
    
    # Mobile app specific fields - PERCEPTION LAYER
    device_info: Optional[DeviceInfo] = Field(None, description="Device security information")
    upi_intent: Optional[UPIIntent] = Field(None, description="UPI intent data if present")
    
    # Enhanced behavioral perception
    is_unusual_time: bool = Field(False, description="Message received at unusual time (e.g., 2 AM)")
    sender_is_contact: bool = Field(False, description="Sender is in user's contacts")
    previous_message_count: int = Field(0, description="Number of previous messages from this sender")
    contains_urgency_words: bool = Field(False, description="Contains urgency keywords")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Congratulations! You've won 1 crore. Click here to claim: bit.ly/xyz",
                "sender": "VK-REWARD",
                "user_id": "user123",
                "device_info": {
                    "is_new_device": False,
                    "sim_changed_recently": False,
                    "screen_sharing_apps_detected": []
                }
            }
        }


class SMSAnalysisResponse(BaseModel):
    """Response model for SMS analysis"""
    message: str
    sender: Optional[str]
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=100)
    is_safe: bool
    fraud_indicators: List[str] = Field(default_factory=list)
    detected_fraud_types: List[FraudType] = Field(default_factory=list)
    extracted_urls: List[str] = Field(default_factory=list)
    extracted_upi_ids: List[str] = Field(default_factory=list)
    extracted_phone_numbers: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict] = Field(default_factory=dict)
    
    # Mobile app specific response fields
    device_security_alerts: List[str] = Field(default_factory=list)
    upi_intent_risk: Optional[Dict] = None
    sim_change_warning: Optional[str] = None
    screen_sharing_warning: Optional[str] = None


# Transaction Analysis Models
class TransactionDetails(BaseModel):
    """Details of a UPI transaction"""
    amount: float = Field(..., gt=0, description="Transaction amount")
    recipient_upi: str = Field(..., description="Recipient UPI ID")
    recipient_name: Optional[str] = Field(None, description="Recipient display name")
    transaction_note: Optional[str] = Field(None, description="Transaction note/description")
    app_name: Optional[str] = Field(None, description="Payment app being used")


class TransactionAnalysisRequest(BaseModel):
    """Request model for transaction analysis"""
    transaction: TransactionDetails
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    context: Optional[Dict] = Field(None, description="Additional context (location, device info, etc.)")
    
    # Enhanced behavioral perception
    is_new_payee: bool = Field(False, description="First time sending to this UPI ID")
    is_unusual_amount: bool = Field(False, description="Amount is unusual for this user")
    is_unusual_time: bool = Field(False, description="Transaction at unusual time")
    transaction_velocity: int = Field(0, description="Number of transactions in last hour")
    user_typical_transaction_amount: Optional[float] = Field(None, description="User's typical transaction amount")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction": {
                    "amount": 5000.0,
                    "recipient_upi": "merchant@paytm",
                    "recipient_name": "Online Store",
                    "transaction_note": "Payment for order #12345",
                    "app_name": "Google Pay"
                },
                "user_id": "user123"
            }
        }


class TransactionAnalysisResponse(BaseModel):
    """Response model for transaction analysis"""
    transaction: TransactionDetails
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=100)
    is_safe: bool
    fraud_indicators: List[str] = Field(default_factory=list)
    detected_fraud_types: List[FraudType] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    similar_fraud_reports: int = Field(0, description="Number of similar fraud reports")
    recipient_trust_score: Optional[float] = Field(None, ge=0, le=100)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict] = Field(default_factory=dict)


# Health Check Models
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    services: Dict[str, bool] = Field(default_factory=dict)


# Error Response Model
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Feedback and Learning Models (Layer 5)
class UserFeedback(BaseModel):
    """User feedback for learning layer"""
    user_id: str = Field(..., description="User ID")
    entity_id: str = Field(..., description="URL, UPI ID, phone number, or other identifier")
    entity_type: str = Field(..., description="Type: url, upi_id, sender, domain")
    feedback: str = Field(..., description="Feedback: safe, fraud, unsure")
    original_risk_score: float = Field(..., description="Original risk score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    comment: Optional[str] = Field(None, description="Optional user comment")


class FeedbackResponse(BaseModel):
    """Response after submitting feedback"""
    message: str
    entity_added_to_whitelist: bool = False
    entity_added_to_blacklist: bool = False
    learning_applied: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
