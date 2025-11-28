"""
FastAPI Fraud Detection System - AGENTIC AI IMPLEMENTATION
Main application file with 5-layer agentic architecture:
🟧 Layer 1: Agent Policy (Goal-driven decisions)
🟧 Layer 2: Perception (Data capturing)
🟧 Layer 3: Reasoning (AI Brain with ML)
🟧 Layer 4: Action (Autonomous control)
🟧 Layer 5: Learning (Feedback loop)
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Dict, Any

from models import (
    URLAnalysisRequest, URLAnalysisResponse,
    SMSAnalysisRequest, SMSAnalysisResponse,
    TransactionAnalysisRequest, TransactionAnalysisResponse,
    HealthCheckResponse, ErrorResponse,
    RiskLevel, FraudType,
    UserFeedback, FeedbackResponse,
    FraudReportRequest, FraudReportResponse,
    AnalysisHistoryItem, AnalysisHistoryResponse,
    DashboardStats, UserSettings, SettingsUpdateRequest,
    QRCodeAnalysisRequest, QRCodeAnalysisResponse
)
from auth import get_current_user, get_optional_user, TokenData, check_auth_service_health
from risk_scoring import (
    calculate_url_risk_score,
    calculate_sms_risk_score,
    calculate_transaction_risk_score,
    extract_urls_from_text,
    extract_upi_ids,
    extract_phone_numbers,
    get_risk_level,
    generate_recommendations,
    analyze_qr_code,
    analyze_domain_details,
    analyze_html_content,
    analyze_redirect_chain,
    analyze_upi_intent,
    analyze_device_security,
    detect_typosquatting,
    analyze_fake_collect_request,
    analyze_fake_kyc_sms
)

# Import all 5 agentic layers
from agent_policy import get_agent_goal, classify_and_act
from ml_reasoning import reasoning_engine
from action_engine import action_engine, ActionContext, Platform, ThreatType
from learning_engine import learning_engine, FeedbackType

# Import payee database for new payee detection
from payee_database import payee_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("=" * 60)
    logger.info("🤖 Starting AGENTIC FRAUD DETECTION API")
    logger.info("=" * 60)
    logger.info(f"🟧 Layer 1: Agent Goal = {get_agent_goal()}")
    logger.info("🟧 Layer 2: Perception Layer = ACTIVE")
    logger.info("🟧 Layer 3: Reasoning Engine = INITIALIZED")
    logger.info("🟧 Layer 4: Action Engine = READY")
    logger.info("🟧 Layer 5: Learning Engine = LOADED")
    logger.info("=" * 60)
    
    logger.info("Checking auth service connection...")
    auth_healthy = await check_auth_service_health()
    if auth_healthy:
        logger.info("✓ Auth service is reachable")
    else:
        logger.warning("⚠ Auth service is not reachable - authentication will fail")
    
    # Load learning data
    metrics = learning_engine.get_metrics()
    logger.info(f"📊 Learning Metrics: {metrics['total_feedbacks']} feedbacks processed")
    logger.info(f"📊 Accuracy: {metrics['accuracy']:.2%}, FP Rate: {metrics['false_positive_rate']:.2%}")
    
    yield
    
    # Shutdown
    logger.info("Saving learning data...")
    learning_engine.save_data()
    logger.info("Shutting down Fraud Detection API...")


# Initialize FastAPI app
app = FastAPI(
    title="Agentic Fraud Detection API",
    description="5-Layer Agentic AI System for autonomous fraud prevention",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Node.js auth server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative frontend
        "chrome-extension://*",   # Chrome extension
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoints
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns the status of the API and its dependencies
    """
    auth_service_healthy = await check_auth_service_health()
    
    return HealthCheckResponse(
        status="healthy" if auth_service_healthy else "degraded",
        services={
            "api": True,
            "auth_service": auth_service_healthy
        }
    )


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Returns API info with agent status"""
    return {
        "message": "🤖 Agentic Fraud Detection API",
        "version": "2.0.0",
        "status": "running",
        "agent_goal": get_agent_goal(),
        "layers": 5,
        "documentation": "/docs"
    }


# ============================================================
# HELPER FUNCTION: Orchestrate all 5 Agentic Layers
# ============================================================

def orchestrate_agentic_analysis(
    entity_id: str,
    entity_type: str,
    base_risk_score: float,
    indicators: List[str],
    user_id: str,
    platform: Platform,
    threat_type: ThreatType,
    additional_data: dict = None
) -> dict:
    """
    Orchestrate all 5 layers of agentic AI:
    1. Policy (goal-driven)
    2. Perception (already captured)
    3. Reasoning (comprehensive ML analysis)
    4. Action (autonomous decisions)
    5. Learning (apply learned adjustments)
    
    Returns enhanced analysis with actions
    """
    # 🟧 LAYER 5: Apply Learning (whitelist/blacklist)
    adjusted_score, learning_reasons = learning_engine.adjust_risk_score(
        entity_id, entity_type, base_risk_score
    )
    indicators.extend(learning_reasons)
    logger.info(f"Learning adjusted score: {base_risk_score} → {adjusted_score}")
    
    # 🟧 LAYER 3: Enhanced Reasoning with ML
    # Get weight adjustments from learning
    weight_adjustments = learning_engine.get_weight_adjustments()
    reasoning_engine.risk_combiner.update_weights(
        {k: 0.50 + v for k, v in weight_adjustments.items()}
    )
    
    # 🟧 LAYER 4: Determine Actions
    fraud_type = "fraud" if adjusted_score >= 70 else "suspicious_activity" if adjusted_score >= 40 else "unknown"
    
    action_context = ActionContext(
        platform=platform,
        threat_type=threat_type,
        risk_score=adjusted_score,
        fraud_type=fraud_type,
        entity_id=entity_id,
        user_id=user_id,
        additional_data=additional_data
    )
    
    action_response = action_engine.decide_and_act(action_context)
    
    return {
        'original_score': base_risk_score,
        'adjusted_score': adjusted_score,
        'action_response': action_response,
        'learning_applied': len(learning_reasons) > 0
    }


# URL Analysis endpoint with AGENTIC AI
@app.post(
    "/analyze/url",
    response_model=URLAnalysisResponse,
    tags=["Analysis"],
    summary="🤖 Agentic URL Analysis (Chrome Extension)"
)
async def analyze_url(
    request: URLAnalysisRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    🤖 **AGENTIC AI URL ANALYSIS** - All 5 Layers Active
    
    **5-Layer Agentic Architecture:**
    - 🟧 Layer 1 (Policy): Goal = "Prevent user from losing money"
    - 🟧 Layer 2 (Perception): URL, QR code, domain, HTML, redirects
    - 🟧 Layer 3 (Reasoning): ML-based risk assessment with NLP
    - 🟧 Layer 4 (Action): Autonomous blocking/warning/allowing
    - 🟧 Layer 5 (Learning): Whitelist/blacklist from user feedback
    
    **Chrome Extension Signals:**
    - URL analysis with typosquatting detection
    - QR code data (upi:// intents)
    - Domain registration details (age, SSL)
    - HTML content (fake forms, password fields, OTP)
    - Redirect patterns (suspicious chains)
    - Enhanced perception signals (keywords, certificate)
    
    **The Agent Will:**
    - ✅ Allow if LOW risk (< 40)
    - ⚠️ Warn if MEDIUM risk (40-69)
    - 🛑 Block if HIGH risk (70-100)
    - Learn from your feedback
    """
    try:
        logger.info(f"🤖 AGENTIC ANALYSIS: URL for user {user.user_id}: {request.url}")
        
        # 🟧 LAYER 2: PERCEPTION - Gather all signals
        risk_score, indicators, details = calculate_url_risk_score(request.url)
        
        # Enhanced perception signals
        domain = urlparse(request.url).netloc
        
        # Prepare data for comprehensive reasoning
        reasoning_data = {
            'url': request.url,
            'text': None,
            'domain_data': {'domain': domain}
        }
        
        # Analyze QR code
        qr_analysis = None
        if request.qr_code_data:
            qr_score, qr_indicators, qr_details = analyze_qr_code(request.qr_code_data)
            risk_score += qr_score * 0.7
            indicators.extend(qr_indicators)
            qr_analysis = qr_details
            reasoning_data['upi_data'] = qr_details if 'upi' in request.qr_code_data.lower() else None
        
        # Analyze domain details
        domain_risk_factors = None
        if request.domain_details:
            domain_score, domain_indicators = analyze_domain_details(request.domain_details.dict())
            risk_score += domain_score
            indicators.extend(domain_indicators)
            domain_risk_factors = domain_indicators
            reasoning_data['domain_data'].update({
                'creation_date': request.domain_details.creation_date,
                'ssl_valid': request.domain_details.ssl_valid
            })
        
        # Analyze HTML content
        html_threats = None
        if request.html_content:
            html_score, html_indicators = analyze_html_content(request.html_content.dict())
            risk_score += html_score
            indicators.extend(html_indicators)
            html_threats = html_indicators
        
        # Analyze redirect chain
        redirect_risk = None
        if request.redirect_chain:
            redirect_score, redirect_indicators = analyze_redirect_chain(request.redirect_chain.dict())
            risk_score += redirect_score
            indicators.extend(redirect_indicators)
            redirect_risk = "high" if redirect_score > 30 else "medium" if redirect_score > 15 else "low"
        
        # Typosquatting detection (Layer 3)
        if request.typosquatting_score and request.typosquatting_score > 0.7:
            risk_score += 40
            indicators.append(f"Possible typosquatting: similar to {request.similar_to_domain}")
        
        # 🟧 LAYER 3: COMPREHENSIVE REASONING
        reasoning_result = reasoning_engine.analyze_comprehensive(**reasoning_data)
        
        # Combine reasoning scores
        final_score = (risk_score * 0.6) + (reasoning_result['final_score'] * 0.4)
        indicators.extend(reasoning_result['indicators'])
        
        # 🟧 ORCHESTRATE ALL 5 LAYERS
        agentic_result = orchestrate_agentic_analysis(
            entity_id=request.url,
            entity_type='url',
            base_risk_score=final_score,
            indicators=indicators,
            user_id=user.user_id,
            platform=Platform.CHROME,
            threat_type=ThreatType.QR_CODE if request.qr_code_data else ThreatType.URL,
            additional_data={'qr_analysis': qr_analysis}
        )
        
        adjusted_score = min(agentic_result['adjusted_score'], 100)
        risk_level = get_risk_level(adjusted_score)
        is_safe = adjusted_score < 40  # Agent policy: < 40 is safe
        
        # Determine fraud types
        fraud_types = []
        if adjusted_score >= 50:
            fraud_types.append(FraudType.PHISHING)
        if qr_analysis and qr_analysis.get('qr_type') == 'upi_intent':
            fraud_types.append(FraudType.QR_CODE_FRAUD)
        if html_threats and any('password' in t.lower() or 'otp' in t.lower() for t in html_threats):
            fraud_types.append(FraudType.FAKE_PAYMENT_FORM)
        if redirect_risk in ['high', 'medium']:
            fraud_types.append(FraudType.REDIRECT_FRAUD)
        
        recommendations = generate_recommendations(adjusted_score, indicators, "url")
        
        # Add agent action instructions
        action_resp = agentic_result['action_response']
        if action_resp['should_block']:
            recommendations.insert(0, f"🛑 AGENT ACTION: {action_resp['message']}")
        elif action_resp['requires_confirmation']:
            recommendations.insert(0, f"⚠️ AGENT WARNING: {action_resp['message']}")
        
        response = URLAnalysisResponse(
            url=request.url,
            risk_level=RiskLevel(risk_level),
            risk_score=adjusted_score,
            is_safe=is_safe,
            fraud_indicators=indicators,
            detected_fraud_types=fraud_types,
            recommendations=recommendations,
            details={
                **details,
                'original_score': agentic_result['original_score'],
                'learning_applied': agentic_result['learning_applied'],
                'agent_action': action_resp['action'],
                'should_block': action_resp['should_block'],
                'chrome_actions': action_resp.get('chrome_actions')
            },
            qr_code_analysis=qr_analysis,
            domain_risk_factors=domain_risk_factors,
            html_threats=html_threats,
            redirect_risk=redirect_risk
        )
        
        # Track in analysis history
        import uuid
        analysis_id = str(uuid.uuid4())
        learning_engine.add_analysis_history(
            analysis_id=analysis_id,
            analysis_type='url',
            entity=request.url,
            risk_level=risk_level,
            risk_score=adjusted_score,
            is_safe=is_safe,
            fraud_indicators=indicators,
            user_id=user.user_id
        )
        
        logger.info(f"🤖 Agent Decision: {action_resp['action']} (score: {adjusted_score:.1f})")
        return response
        
    except Exception as e:
        logger.error(f"Error in agentic URL analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze URL: {str(e)}"
        )



# SMS Analysis endpoint
@app.post(
    "/analyze/sms",
    response_model=SMSAnalysisResponse,
    tags=["Analysis"],
    summary="Analyze SMS for fraud indicators (Mobile App)"
)
async def analyze_sms(
    request: SMSAnalysisRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Analyze an SMS message for potential fraud with mobile app security features
    
    **Mobile App Security Features:**
    - Device security status (new device, SIM change)
    - Screen sharing app detection
    - UPI intent analysis
    
    **Parameters:**
    - **message**: The SMS content to analyze
    - **sender**: Optional sender ID or phone number
    - **device_info**: Optional device security information
    - **upi_intent**: Optional UPI intent data
    
    Returns risk score, extracted data, security alerts, and recommendations
    """
    try:
        logger.info(f"Analyzing SMS for user {user.user_id}")
        
        # Calculate base SMS risk score
        risk_score, indicators, details = calculate_sms_risk_score(
            request.message,
            request.sender
        )
        
        # Security alerts for mobile app
        device_security_alerts = []
        sim_change_warning = None
        screen_sharing_warning = None
        
        # Analyze device security if present
        if request.device_info:
            device_score, device_indicators, device_details = analyze_device_security(
                request.device_info.dict()
            )
            risk_score += device_score
            indicators.extend(device_indicators)
            device_security_alerts = device_indicators
            
            if device_details.get('sim_swap_alert'):
                sim_change_warning = "🚨 CRITICAL: Recent SIM change detected. Be extremely cautious with any financial transactions."
            
            if device_details.get('screen_sharing_warning'):
                screen_sharing_warning = device_details['screen_sharing_warning']
            
            logger.info(f"Device security analyzed: risk +{device_score}")
        
        # Analyze UPI intent if present
        upi_intent_risk = None
        if request.upi_intent:
            upi_score, upi_indicators, upi_details = analyze_upi_intent(
                request.upi_intent.dict()
            )
            risk_score += upi_score
            indicators.extend(upi_indicators)
            upi_intent_risk = upi_details
            logger.info(f"UPI intent analyzed: risk +{upi_score}")
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        risk_level = get_risk_level(risk_score)
        is_safe = risk_score < 50
        
        # Extract data
        urls = extract_urls_from_text(request.message)
        upi_ids = extract_upi_ids(request.message)
        phone_numbers = extract_phone_numbers(request.message)
        
        # Determine fraud types
        fraud_types = []
        if risk_score >= 50:
            fraud_types.append(FraudType.SMS_SCAM)
        if urls:
            fraud_types.append(FraudType.PHISHING)
        if "personal information" in str(indicators).lower():
            fraud_types.append(FraudType.SOCIAL_ENGINEERING)
        if screen_sharing_warning:
            fraud_types.append(FraudType.SCREEN_SHARING_SCAM)
        if sim_change_warning:
            fraud_types.append(FraudType.SIM_SWAP_FRAUD)
        
        # Generate recommendations
        recommendations = generate_recommendations(risk_score, indicators, "sms")
        
        # Add device-specific recommendations
        if screen_sharing_warning:
            recommendations.insert(0, "🚨 IMMEDIATELY uninstall screen sharing apps and check device for unauthorized access")
        if sim_change_warning:
            recommendations.insert(0, "🚨 Contact your bank immediately if you didn't change your SIM card")
        
        # Track in analysis history
        import uuid
        analysis_id = str(uuid.uuid4())
        entity = request.sender or "Unknown sender"
        learning_engine.add_analysis_history(
            analysis_id=analysis_id,
            analysis_type='sms',
            entity=entity,
            risk_level=risk_level,
            risk_score=risk_score,
            is_safe=is_safe,
            fraud_indicators=indicators,
            user_id=user.user_id
        )
        
        return SMSAnalysisResponse(
            message=request.message,
            sender=request.sender,
            risk_level=RiskLevel(risk_level),
            risk_score=risk_score,
            is_safe=is_safe,
            fraud_indicators=indicators,
            detected_fraud_types=fraud_types,
            extracted_urls=urls,
            extracted_upi_ids=upi_ids,
            extracted_phone_numbers=phone_numbers,
            recommendations=recommendations,
            details=details,
            device_security_alerts=device_security_alerts,
            upi_intent_risk=upi_intent_risk,
            sim_change_warning=sim_change_warning,
            screen_sharing_warning=screen_sharing_warning
        )
        
    except Exception as e:
        logger.error(f"Error analyzing SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze SMS: {str(e)}"
        )


# Transaction Analysis endpoint
@app.post(
    "/analyze/transaction",
    response_model=TransactionAnalysisResponse,
    tags=["Analysis"],
    summary="Analyze UPI transaction for fraud indicators"
)
async def analyze_transaction(
    request: TransactionAnalysisRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Analyze a UPI transaction for potential fraud
    
    - **transaction**: Transaction details (amount, recipient UPI, etc.)
    - **user_id**: Optional user ID for tracking
    
    Returns risk score, warnings, and recommendations
    """
    try:
        logger.info(
            f"Analyzing transaction for user {user.user_id}: "
            f"₹{request.transaction.amount} to {request.transaction.recipient_upi}"
        )
        
        # Check if this is a new payee using local database
        is_new_payee = payee_db.is_new_payee(user.user_id, request.transaction.recipient_upi)
        payee_info = payee_db.get_payee_info(user.user_id, request.transaction.recipient_upi)
        
        # Calculate risk score
        risk_score, indicators, details = calculate_transaction_risk_score(
            request.transaction.amount,
            request.transaction.recipient_upi,
            request.transaction.recipient_name,
            request.transaction.transaction_note
        )
        
        # NEW PAYEE DETECTION - Add risk for unknown recipients
        if is_new_payee:
            risk_score += 25
            indicators.append("⚠️ NEW PAYEE: First time sending money to this UPI ID")
            details['is_new_payee'] = True
            
            # Higher risk for new payee + large amount
            if request.transaction.amount > 5000:
                risk_score += 15
                indicators.append("🚨 High-risk: Large amount to NEW recipient")
        else:
            # Known payee - check for anomalies
            details['is_new_payee'] = False
            details['payee_info'] = {
                'transaction_count': payee_info['transaction_count'],
                'average_amount': payee_info['average_amount'],
                'is_trusted': payee_info['is_trusted']
            }
            
            # Amount anomaly detection
            if request.transaction.amount > (payee_info['average_amount'] * 3):
                risk_score += 20
                indicators.append(f"⚠️ Amount anomaly: 3x higher than usual (avg: ₹{payee_info['average_amount']:.2f})")
            
            # Trust bonus
            if payee_info['is_trusted']:
                risk_score = max(0, risk_score - 15)
                details['trusted_payee'] = True
        
        risk_level = get_risk_level(risk_score)
        is_safe = risk_score < 50
        
        # Determine fraud types
        fraud_types = []
        if risk_score >= 50:
            fraud_types.append(FraudType.FAKE_UPI)
        if risk_score >= 70:
            fraud_types.append(FraudType.UNAUTHORIZED_TRANSACTION)
        
        # Generate warnings
        warnings = []
        if risk_score >= 75:
            warnings.append("⛔ CRITICAL: High risk of fraud detected")
        elif risk_score >= 50:
            warnings.append("⚠️ WARNING: Suspicious transaction detected")
        
        if request.transaction.amount > 50000:
            warnings.append("Large transaction amount - verify recipient carefully")
        
        # Generate recommendations
        recommendations = generate_recommendations(risk_score, indicators, "transaction")
        
        # Calculate recipient trust score (simplified - in production, use historical data)
        recipient_trust_score = max(0, 100 - risk_score)
        
        # Track in analysis history
        import uuid
        analysis_id = str(uuid.uuid4())
        learning_engine.add_analysis_history(
            analysis_id=analysis_id,
            analysis_type='transaction',
            entity=request.transaction.recipient_upi,
            risk_level=risk_level,
            risk_score=risk_score,
            is_safe=is_safe,
            fraud_indicators=indicators,
            user_id=user.user_id
        )
        
        # Log transaction in payee database (regardless of whether it was blocked)
        # Don't log if risk is critical to avoid tracking blocked fraud attempts
        if risk_score < 90:
            payee_db.add_transaction(
                user_id=user.user_id,
                payee_upi=request.transaction.recipient_upi,
                amount=request.transaction.amount,
                payee_name=request.transaction.recipient_name,
                transaction_note=request.transaction.transaction_note,
                risk_score=risk_score,
                was_blocked=(risk_score >= 70)
            )
        
        return TransactionAnalysisResponse(
            transaction=request.transaction,
            risk_level=RiskLevel(risk_level),
            risk_score=risk_score,
            is_safe=is_safe,
            fraud_indicators=indicators,
            detected_fraud_types=fraud_types,
            warnings=warnings,
            recommendations=recommendations,
            similar_fraud_reports=0,  # In production, query fraud database
            recipient_trust_score=recipient_trust_score,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Error analyzing transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze transaction: {str(e)}"
        )


# Public endpoint for testing (no auth required)
@app.post(
    "/analyze/url/public",
    response_model=URLAnalysisResponse,
    tags=["Public"],
    summary="Public URL analysis endpoint (no auth)"
)
async def analyze_url_public(request: URLAnalysisRequest):
    """
    Public endpoint to analyze URLs without authentication
    Useful for testing or public integrations
    """
    try:
        logger.info(f"Public URL analysis: {request.url}")
        
        risk_score, indicators, details = calculate_url_risk_score(request.url)
        risk_level = get_risk_level(risk_score)
        is_safe = risk_score < 50
        
        fraud_types = []
        if risk_score >= 50:
            fraud_types.append(FraudType.PHISHING)
        
        recommendations = generate_recommendations(risk_score, indicators, "url")
        
        return URLAnalysisResponse(
            url=request.url,
            risk_level=RiskLevel(risk_level),
            risk_score=risk_score,
            is_safe=is_safe,
            fraud_indicators=indicators,
            detected_fraud_types=fraud_types,
            recommendations=recommendations,
            details=details
        )
        
    except Exception as e:
        logger.error(f"Error in public URL analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze URL: {str(e)}"
        )


# User info endpoint
@app.get("/user/me", tags=["User"])
async def get_user_info(user: TokenData = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "user_id": user.user_id,
        "email": user.email,
        "roles": user.roles
    }


# ============================================================
# 🟧 LAYER 5: LEARNING ENDPOINTS (Feedback Loop)
# ============================================================

@app.post(
    "/feedback",
    response_model=FeedbackResponse,
    tags=["Learning"],
    summary="Submit user feedback for learning"
)
async def submit_feedback(
    feedback: UserFeedback,
    user: TokenData = Depends(get_current_user)
):
    """
    Submit user feedback to improve fraud detection
    
    **This is the Learning Layer in action:**
    - User marks entity as 'safe' → Added to whitelist, adjusts weights
    - User marks entity as 'fraud' → Added to blacklist, adjusts weights
    - System learns from false positives/negatives
    
    **Parameters:**
    - **entity_id**: URL, UPI ID, phone number, or domain
    - **entity_type**: Type of entity (url, upi_id, sender, domain)
    - **feedback**: 'safe', 'fraud', or 'unsure'
    - **original_risk_score**: The risk score we originally gave
    - **comment**: Optional user comment
    """
    try:
        logger.info(f"Processing feedback from user {feedback.user_id}: {feedback.feedback} for {feedback.entity_type}")
        
        # Process feedback through learning engine
        result = learning_engine.process_feedback(
            entity_id=feedback.entity_id,
            entity_type=feedback.entity_type,
            feedback=feedback.feedback,
            original_risk_score=feedback.original_risk_score,
            user_id=feedback.user_id,
            comment=feedback.comment
        )
        
        # If marked as safe and was previously blocked, unblock it
        if feedback.feedback == FeedbackType.SAFE and action_engine.is_blocked(feedback.entity_id):
            action_engine.unblock(feedback.entity_id)
        
        return FeedbackResponse(
            message=result['message'],
            entity_added_to_whitelist=result['added_to_whitelist'],
            entity_added_to_blacklist=result['added_to_blacklist'],
            learning_applied=result['learning_applied']
        )
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process feedback: {str(e)}"
        )


@app.get(
    "/learning/metrics",
    tags=["Learning"],
    summary="Get learning metrics and statistics"
)
async def get_learning_metrics(user: TokenData = Depends(get_current_user)):
    """
    Get learning engine metrics
    
    Returns:
    - Total feedbacks processed
    - Accuracy, false positive rate, false negative rate
    - Whitelist/blacklist sizes
    - Weight adjustments
    """
    try:
        metrics = learning_engine.get_metrics()
        weight_adjustments = learning_engine.get_weight_adjustments()
        
        return {
            "metrics": metrics,
            "weight_adjustments": weight_adjustments,
            "agent_goal": get_agent_goal()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


@app.get(
    "/learning/feedback-history",
    tags=["Learning"],
    summary="Get feedback history"
)
async def get_feedback_history(
    limit: int = 100,
    entity_type: str = None,
    user: TokenData = Depends(get_current_user)
):
    """
    Get feedback history with optional filters
    """
    try:
        history = learning_engine.get_feedback_history(
            limit=limit,
            entity_type=entity_type,
            user_id=user.user_id
        )
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting feedback history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback history: {str(e)}"
        )


@app.get(
    "/agent/status",
    tags=["Agent"],
    summary="Get agent status and goal"
)
async def get_agent_status(user: TokenData = Depends(get_current_user)):
    """
    Get the agent's current status, goal, and operational metrics
    
    **Shows all 5 layers:**
    - Layer 1: Agent's goal
    - Layer 2: Perception statistics
    - Layer 3: Reasoning engine status
    - Layer 4: Actions taken
    - Layer 5: Learning metrics
    
    **Requires Authentication**
    """
    try:
        metrics = learning_engine.get_metrics()
        action_history = action_engine.get_action_history(limit=10)
        
        return {
            "layer_1_policy": {
                "goal": get_agent_goal(),
                "version": "2.0.0"
            },
            "layer_2_perception": {
                "status": "active",
                "capabilities": [
                    "URL analysis",
                    "QR code scanning",
                    "Domain details",
                    "HTML content analysis",
                    "Redirect patterns",
                    "SMS fraud detection",
                    "UPI intent analysis",
                    "SIM change detection",
                    "Screen sharing detection",
                    "Device security monitoring"
                ]
            },
            "layer_3_reasoning": {
                "status": "initialized",
                "engines": [
                    "Rule-based engine",
                    "NLP engine",
                    "Domain similarity",
                    "Behavioral anomaly detector"
                ]
            },
            "layer_4_actions": {
                "status": "ready",
                "recent_actions": len(action_history),
                "blocked_entities": len(action_engine.blocked_entities)
            },
            "layer_5_learning": {
                "status": "learning",
                "total_feedbacks": metrics['total_feedbacks'],
                "accuracy": metrics.get('accuracy', 0.0),
                "false_positive_rate": metrics.get('false_positive_rate', 0.0)
            }
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


# ============================================================
# 🚨 FRAUD REPORTING ENDPOINTS (Community Protection)
# ============================================================

@app.post("/report/fraud", response_model=FraudReportResponse, tags=["Fraud Reports"])
async def report_fraud(
    report: FraudReportRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Report a fraud incident to help protect the community
    
    **Automatic Blacklisting**: When an entity receives 50+ fraud reports,
    it will be automatically blacklisted and blocked for all users.
    
    **Entity Types**:
    - `phone_numbers`: SMS/call fraud
    - `upi_ids`: Fake UPI IDs
    - `urls`: Phishing websites
    - `senders`: Fraudulent sender names
    - `domains`: Malicious domains
    
    **Example**:
    ```json
    {
        "entity_id": "+919876543210",
        "entity_type": "phone_numbers",
        "description": "Pretending to be bank, asked for OTP",
        "fraud_category": "sms_scam",
        "amount_lost": 5000.0
    }
    ```
    """
    try:
        logger.info(f"Fraud report received from user {user.user_id} for {report.entity_type}:{report.entity_id}")
        
        # Validate entity type
        valid_types = ['phone_numbers', 'upi_ids', 'urls', 'senders', 'domains']
        if report.entity_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity_type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Submit fraud report to learning engine
        result = learning_engine.report_fraud(
            entity_id=report.entity_id,
            entity_type=report.entity_type,
            user_id=user.user_id,
            description=report.description,
            fraud_category=report.fraud_category,
            amount_lost=report.amount_lost,
            additional_info=report.additional_info
        )
        
        # Log if entity was blacklisted
        if result['blacklisted']:
            logger.warning(
                f"🚨 AUTOMATIC BLACKLIST: {report.entity_type}:{report.entity_id} "
                f"after {result['report_count']} reports"
            )
        
        return FraudReportResponse(
            success=True,
            entity_id=result['entity_id'],
            entity_type=result['entity_type'],
            report_count=result['report_count'],
            threshold=result['threshold'],
            blacklisted=result['blacklisted'],
            message=result['message']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing fraud report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process fraud report: {str(e)}"
        )


@app.get("/report/history", tags=["Fraud Reports"])
async def get_fraud_report_history(
    user: TokenData = Depends(get_current_user),
    entity_id: str = None,
    entity_type: str = None,
    limit: int = 100
):
    """
    Get fraud report history with optional filters
    
    **Query Parameters**:
    - `entity_id`: Filter by specific entity (phone number, UPI ID, etc.)
    - `entity_type`: Filter by entity type (phone_numbers, upi_ids, etc.)
    - `limit`: Maximum number of reports to return (default: 100)
    
    Returns list of fraud reports with timestamps and report counts
    """
    try:
        reports = learning_engine.get_fraud_reports(
            entity_id=entity_id,
            entity_type=entity_type,
            limit=limit
        )
        
        return {
            "total_reports": len(reports),
            "filters": {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "limit": limit
            },
            "reports": reports
        }
    
    except Exception as e:
        logger.error(f"Error fetching fraud report history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fraud report history: {str(e)}"
        )


@app.get("/report/statistics", tags=["Fraud Reports"])
async def get_fraud_report_statistics(
    user: TokenData = Depends(get_current_user)
):
    """
    Get comprehensive statistics about fraud reports
    
    Returns:
    - Total unique entities reported
    - Total number of reports
    - Distribution by report count (1-4, 5-9, 10-19, 20-49, 50+)
    - Reports by entity type
    - Reports by fraud category
    - Total amount lost
    - Entities that reached blacklist threshold
    """
    try:
        stats = learning_engine.get_report_statistics()
        
        return {
            "statistics": stats,
            "threshold_info": {
                "blacklist_threshold": learning_engine.fraud_report_threshold,
                "description": f"Entities with {learning_engine.fraud_report_threshold}+ reports are automatically blacklisted"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching fraud report statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fraud report statistics: {str(e)}"
        )


# ============================================================
# 📊 DASHBOARD ENDPOINT
# ============================================================

@app.get("/dashboard", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard(
    user: TokenData = Depends(get_current_user)
):
    """
    Get dashboard overview with fraud protection statistics
    
    **Returns**:
    - Total analyses performed
    - Analyses today
    - Blocked threats count
    - Active alerts
    - Risk distribution (low, medium, high, critical)
    - Analysis by type (URL, SMS, transaction, QR)
    - Recent high-risk alerts
    - Protection rate percentage
    - Learning accuracy
    
    **Perfect for**: Dashboard homepage showing user's fraud protection status
    """
    try:
        logger.info(f"Fetching dashboard for user {user.user_id}")
        
        # Get stats from learning engine
        stats = learning_engine.get_dashboard_stats(user.user_id)
        
        # Get learning metrics
        metrics = learning_engine.get_metrics()
        
        # Convert recent alerts to proper format
        recent_alerts = [
            AnalysisHistoryItem(
                id=alert['id'],
                analysis_type=alert['analysis_type'],
                entity=alert['entity'],
                risk_level=alert['risk_level'],
                risk_score=alert['risk_score'],
                is_safe=alert['is_safe'],
                fraud_indicators=alert['fraud_indicators'],
                timestamp=datetime.fromisoformat(alert['timestamp']),
                user_action=alert.get('user_action')
            )
            for alert in stats['recent_alerts']
        ]
        
        return DashboardStats(
            total_analyses=stats['total_analyses'],
            analyses_today=stats['analyses_today'],
            blocked_threats=stats['blocked_threats'],
            active_alerts=stats['active_alerts'],
            risk_distribution=stats['risk_distribution'],
            analysis_by_type=stats['analysis_by_type'],
            recent_alerts=recent_alerts,
            protection_rate=stats['protection_rate'],
            learning_accuracy=metrics.get('accuracy', 0.0) * 100
        )
    
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard: {str(e)}"
        )


# ============================================================
# 📜 ANALYSIS HISTORY ENDPOINT
# ============================================================

@app.get("/history", response_model=AnalysisHistoryResponse, tags=["History"])
async def get_analysis_history(
    user: TokenData = Depends(get_current_user),
    analysis_type: str = None,
    risk_level: str = None,
    limit: int = 100
):
    """
    Get history of all fraud analysis results
    
    **Query Parameters**:
    - `analysis_type`: Filter by type (url, sms, transaction, qr_code)
    - `risk_level`: Filter by risk (low, medium, high, critical)
    - `limit`: Maximum results (default: 100, max: 500)
    
    **Returns**:
    - Complete analysis history for the user
    - Each entry includes: type, entity, risk score, indicators, timestamp
    - User actions/feedback if provided
    
    **Perfect for**: History page showing all past fraud checks
    """
    try:
        logger.info(f"Fetching history for user {user.user_id}")
        
        # Validate limit
        if limit > 500:
            limit = 500
        
        # Get history from learning engine
        history = learning_engine.get_analysis_history(
            user_id=user.user_id,
            analysis_type=analysis_type,
            risk_level=risk_level,
            limit=limit
        )
        
        # Convert to proper format
        analyses = [
            AnalysisHistoryItem(
                id=item['id'],
                analysis_type=item['analysis_type'],
                entity=item['entity'],
                risk_level=item['risk_level'],
                risk_score=item['risk_score'],
                is_safe=item['is_safe'],
                fraud_indicators=item['fraud_indicators'],
                timestamp=datetime.fromisoformat(item['timestamp']),
                user_action=item.get('user_action')
            )
            for item in history
        ]
        
        return AnalysisHistoryResponse(
            total_analyses=len(analyses),
            analyses=analyses,
            filters={
                'analysis_type': analysis_type,
                'risk_level': risk_level,
                'limit': limit
            }
        )
    
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )


# ============================================================
# ⚙️ USER SETTINGS ENDPOINTS
# ============================================================

@app.get("/settings", response_model=UserSettings, tags=["Settings"])
async def get_user_settings(
    user: TokenData = Depends(get_current_user)
):
    """
    Get user's current settings
    
    **Returns**:
    - Risk thresholds (low, medium, high)
    - Feature toggles (URL, SMS, transaction analysis, etc.)
    - Notification preferences
    - Auto-feedback settings
    
    **Perfect for**: Settings page to show current configuration
    """
    try:
        settings = learning_engine.get_user_settings(user.user_id)
        return UserSettings(**settings)
    
    except Exception as e:
        logger.error(f"Error fetching settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch settings: {str(e)}"
        )


@app.put("/settings", response_model=UserSettings, tags=["Settings"])
async def update_user_settings(
    settings: SettingsUpdateRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Update user settings
    
    **Request Body**: Partial update - only include fields to change
    - `risk_thresholds`: Update risk threshold values
    - `features`: Enable/disable specific features
    - `notification_preferences`: Update notification settings
    - `auto_submit_feedback`: Toggle automatic feedback
    
    **Returns**: Updated complete settings
    
    **Perfect for**: Settings page save functionality
    """
    try:
        logger.info(f"Updating settings for user {user.user_id}")
        
        # Build update dict
        updates = {}
        if settings.risk_thresholds:
            updates['risk_thresholds'] = settings.risk_thresholds.model_dump()
        if settings.features:
            updates['features'] = settings.features.model_dump()
        if settings.notification_preferences:
            updates['notification_preferences'] = settings.notification_preferences
        if settings.auto_submit_feedback is not None:
            updates['auto_submit_feedback'] = settings.auto_submit_feedback
        
        # Update settings
        learning_engine.update_user_settings(user.user_id, updates)
        
        # Return updated settings
        updated = learning_engine.get_user_settings(user.user_id)
        return UserSettings(**updated)
    
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


# ============================================================
# 📱 QR CODE ANALYSIS ENDPOINT
# ============================================================

@app.post("/analyze/qr", response_model=QRCodeAnalysisResponse, tags=["Analysis"])
async def analyze_qr_code(
    request: QRCodeAnalysisRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    🤖 **QR Code Fraud Analysis** - Scan and analyze QR codes for fraud
    
    **Supported QR Types**:
    - UPI Payment QR codes (upi://pay?...)
    - Website URLs (https://...)
    - Plain text
    
    **The Agent Will Detect**:
    - Fake UPI payment QR codes
    - Phishing URLs in QR codes
    - Suspicious payment amounts
    - Unknown/unverified merchants
    - Typosquatting in UPI IDs
    
    **Perfect for**: Mobile app QR scanner feature
    """
    try:
        import uuid
        import re
        
        logger.info(f"🤖 QR CODE ANALYSIS for user {user.user_id}")
        
        # Determine QR type
        qr_data = request.qr_data
        qr_type = "unknown"
        extracted_info = {}
        fraud_indicators = []
        risk_score = 0.0
        
        # Check if UPI payment
        if qr_data.startswith("upi://pay"):
            qr_type = "upi_payment"
            
            # Parse UPI intent
            upi_analysis = analyze_upi_intent(qr_data)
            extracted_info = {
                'payee_vpa': upi_analysis.get('payee_vpa'),
                'payee_name': upi_analysis.get('payee_name'),
                'amount': upi_analysis.get('amount'),
                'transaction_note': upi_analysis.get('transaction_note')
            }
            
            # Use transaction analysis
            if extracted_info['payee_vpa']:
                risk_score, indicators, _ = calculate_transaction_risk_score(
                    recipient_upi=extracted_info['payee_vpa'],
                    amount=extracted_info.get('amount', 0.0),
                    recipient_name=extracted_info.get('payee_name')
                )
                fraud_indicators = indicators
        
        # Check if URL
        elif qr_data.startswith(('http://', 'https://', 'www.')):
            qr_type = "url"
            
            # Use URL analysis
            risk_score, indicators, details = calculate_url_risk_score(qr_data)
            fraud_indicators = indicators
            extracted_info = {'url': qr_data, 'domain': urlparse(qr_data).netloc}
        
        # Plain text
        else:
            qr_type = "text"
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'password', r'otp', r'pin', r'cvv', r'bank',
                r'account', r'credit', r'debit', r'payment'
            ]
            for pattern in suspicious_patterns:
                if re.search(pattern, qr_data.lower()):
                    fraud_indicators.append(f"Suspicious keyword: {pattern}")
                    risk_score += 15
            
            extracted_info = {'text': qr_data[:100]}
        
        # Apply learning layer adjustments
        if qr_type == "upi_payment" and extracted_info.get('payee_vpa'):
            adjusted_score, reasons = learning_engine.adjust_risk_score(
                entity_id=extracted_info['payee_vpa'],
                entity_type='upi_ids',
                original_score=risk_score
            )
            risk_score = adjusted_score
            fraud_indicators.extend(reasons)
        
        # Determine risk level
        risk_level = get_risk_level(risk_score)
        is_safe = risk_score < 40
        
        # Generate recommendations
        recommendations = []
        if not is_safe:
            if qr_type == "upi_payment":
                recommendations.append("⚠️ Do not scan or pay to this QR code")
                recommendations.append("Verify the merchant/recipient independently")
                recommendations.append("Report this QR code if you found it in a suspicious location")
            elif qr_type == "url":
                recommendations.append("⚠️ Do not visit this URL from the QR code")
                recommendations.append("Manually type the website address instead")
            else:
                recommendations.append("⚠️ This QR code contains suspicious content")
        else:
            recommendations.append("✅ QR code appears safe")
            if qr_type == "upi_payment":
                recommendations.append("Verify payment details before confirming")
        
        # Track in history
        analysis_id = str(uuid.uuid4())
        entity = extracted_info.get('payee_vpa') or extracted_info.get('url') or qr_data[:50]
        learning_engine.add_analysis_history(
            analysis_id=analysis_id,
            analysis_type='qr_code',
            entity=entity,
            risk_level=risk_level.value,
            risk_score=risk_score,
            is_safe=is_safe,
            fraud_indicators=fraud_indicators,
            user_id=user.user_id
        )
        
        return QRCodeAnalysisResponse(
            qr_data=qr_data,
            qr_type=qr_type,
            risk_level=risk_level,
            risk_score=risk_score,
            is_safe=is_safe,
            fraud_indicators=fraud_indicators,
            extracted_info=extracted_info,
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Error analyzing QR code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze QR code: {str(e)}"
        )


# ============================================================
# 💼 PAYEE MANAGEMENT ENDPOINTS (New Payee Detection)
# ============================================================

@app.get("/payee/info/{payee_upi}", tags=["Payee Management"])
async def get_payee_information(
    payee_upi: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Get information about a specific payee
    
    **Returns**:
    - Transaction count with this payee
    - Average transaction amount
    - First and last transaction dates
    - Whether marked as trusted
    - Is new payee or not
    """
    try:
        is_new = payee_db.is_new_payee(user.user_id, payee_upi)
        
        if is_new:
            return {
                "payee_upi": payee_upi,
                "is_new_payee": True,
                "message": "This is a new payee. No transaction history found."
            }
        
        payee_info = payee_db.get_payee_info(user.user_id, payee_upi)
        return {
            "payee_upi": payee_upi,
            "is_new_payee": False,
            **payee_info
        }
    
    except Exception as e:
        logger.error(f"Error fetching payee info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payee info: {str(e)}"
        )


@app.post("/payee/trust/{payee_upi}", tags=["Payee Management"])
async def mark_payee_trusted(
    payee_upi: str,
    trusted: bool = True,
    user: TokenData = Depends(get_current_user)
):
    """
    Mark a payee as trusted or untrusted
    
    **Parameters**:
    - `payee_upi`: UPI ID of the payee
    - `trusted`: True to mark as trusted, False to remove trust
    
    **Trusted payees** get lower risk scores in future transactions
    """
    try:
        # Check if payee exists
        if payee_db.is_new_payee(user.user_id, payee_upi):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payee not found. You need to transact with them first."
            )
        
        payee_db.mark_as_trusted(user.user_id, payee_upi, trusted)
        
        return {
            "success": True,
            "payee_upi": payee_upi,
            "trusted": trusted,
            "message": f"Payee {'marked as trusted' if trusted else 'trust removed'}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking payee trust: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update payee trust: {str(e)}"
        )


@app.get("/payee/transactions", tags=["Payee Management"])
async def get_transaction_history(
    payee_upi: str = None,
    limit: int = 50,
    user: TokenData = Depends(get_current_user)
):
    """
    Get transaction history
    
    **Query Parameters**:
    - `payee_upi`: Optional - filter by specific payee
    - `limit`: Maximum number of transactions (default: 50)
    
    **Returns** list of past transactions with risk scores
    """
    try:
        history = payee_db.get_transaction_history(
            user_id=user.user_id,
            payee_upi=payee_upi,
            limit=min(limit, 200)  # Cap at 200
        )
        
        return {
            "total_transactions": len(history),
            "filtered_by_payee": payee_upi,
            "transactions": history
        }
    
    except Exception as e:
        logger.error(f"Error fetching transaction history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transaction history: {str(e)}"
        )


@app.get("/payee/statistics", tags=["Payee Management"])
async def get_payee_statistics(
    user: TokenData = Depends(get_current_user)
):
    """
    Get user's overall payee and transaction statistics
    
    **Returns**:
    - Total unique payees
    - Trusted payees count
    - Total transactions
    - Total amount transacted
    - Average transaction amount
    - Blocked transactions count
    """
    try:
        stats = payee_db.get_user_statistics(user.user_id)
        
        return {
            "user_id": user.user_id,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching payee statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payee statistics: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
