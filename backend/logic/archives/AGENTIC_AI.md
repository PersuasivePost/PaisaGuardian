# 🤖 AGENTIC AI FRAUD DETECTION SYSTEM

## Complete 5-Layer Architecture Implementation

This document explains how the fraud detection system implements a complete **Agentic AI** architecture with 5 distinct layers that work together to autonomously prevent fraud.

---

## 🎯 What is Agentic AI?

**Agentic AI** is an AI system that:
- Has a **clear objective/goal**
- **Perceives** its environment
- **Reasons** about what it observes
- Takes **autonomous actions** to achieve its goal
- **Learns** from feedback to improve

Our system implements this complete loop for fraud prevention.

---

## 🟧 LAYER 1: AGENT POLICY (The Goal)

**File:** `agent_policy.py`

### The Agent's Objective

```python
goal = "Prevent the user from losing money to fraud"
```

Everything the agent does is optimized for this goal.

### Decision Framework

The agent classifies risk into 4 levels:
- **LOW** (0-39): Safe → Allow and monitor
- **MEDIUM** (40-69): Suspicious → Warn user
- **HIGH** (70-99): Dangerous → Block immediately
- **CRITICAL** (100+): Emergency → Abort transaction

### Action Types

Based on risk level, the agent can:
- ✅ **ALLOW**: Let user continue
- 👀 **MONITOR**: Silently track
- ⚠️ **WARN**: Show warning popup
- ❓ **CONFIRM**: Request user confirmation
- 🛑 **BLOCK**: Stop action immediately
- 🚫 **ABORT_TRANSACTION**: Cancel payment
- 🔄 **REDIRECT**: Navigate to safe page
- ❌ **DISABLE_ACTION**: Disable UI elements

### Key Policy Functions

```python
def classify_risk(score: float) -> RiskLevel:
    """Classify score into risk level"""
    
def determine_action(risk_level: RiskLevel, context: Dict) -> ActionType:
    """Decide what action to take"""
    
def get_action_message(action: ActionType, risk_level: RiskLevel) -> str:
    """Generate user-facing message"""
```

---

## 🟧 LAYER 2: PERCEPTION (Data Capturing)

**Files:** `main.py` (endpoints), `models.py` (data models)

### What the Agent Observes

#### From Chrome Extension:
```python
# URL analysis
url: str
qr_code_data: Optional[str]  # QR codes on page
domain_details: DomainDetails  # Registration, SSL
html_content: HTMLContentAnalysis  # Fake forms, password fields
redirect_chain: RedirectChain  # Suspicious redirects
suspicious_keywords: List[str]
typosquatting_score: float  # 0-1 similarity
has_https: bool
certificate_valid: bool
```

#### From Android App:
```python
# SMS analysis
message: str
sender: str
is_unusual_time: bool  # 2 AM message?
sender_is_contact: bool
contains_urgency_words: bool

# Device security
device_info: DeviceInfo
  - is_new_device: bool
  - sim_changed_recently: bool
  - screen_sharing_apps: List[str]
  - last_sim_change: datetime

# UPI intents
upi_intent: UPIIntent
  - intent_type: "upi_pay" | "upi_collect"
  - payee_address: str
  - amount: float
```

#### Behavioral Signals:
```python
# Transaction behavior
is_new_payee: bool
is_unusual_amount: bool
is_unusual_time: bool
transaction_velocity: int  # Transactions in last hour
user_typical_transaction_amount: float
```

### Implementation

**Chrome Extension sends:**
```javascript
chrome.tabs.onUpdated.addListener(() => {
    sendToBackend({
        url: tab.url,
        qr_code_data: scannedQR,
        suspicious_keywords: detectKeywords(),
        typosquatting_score: checkSimilarity()
    });
});
```

**Android App sends:**
```kotlin
if (intent.dataString?.startsWith("upi://")) {
    sendToBackend(UPIAnalysisRequest(
        upi_intent = parseIntent(intent),
        device_info = getDeviceInfo(),
        ...
    ))
}
```

---

## 🟧 LAYER 3: REASONING (The AI Brain)

**File:** `ml_reasoning.py`

This layer evaluates risk using multiple engines:

### (A) Rule-Based Engine

Fast, deterministic pattern matching:

```python
score = 0

# SMS fraud keywords
if "kyc" in sms: score += 40
if "account blocked" in sms: score += 40
if "verify now" in sms: score += 40

# URL patterns
if domain_similar < 3: score += 30  # Typosquatting
if uses_ip_address: score += 30
if free_domain: score += 35

# UPI intents
if upi_intent == "collect": score += 40
if amount > 50000: score += 35

# Device security
if screen_share_installed: score += 50
if sim_changed_recently: score += 40
```

### (B) NLP Reasoning Engine

Natural language processing for fraud detection:

```python
class NLPEngine:
    FRAUD_PHRASES = {
        'account will be blocked': 0.9,
        'urgent verification required': 0.9,
        'claim your prize': 0.85,
        ...
    }
    
    def analyze_text(text: str) -> (nlp_score, confidence, phrases):
        # Detect fraud phrases
        # Sentiment analysis (fear, urgency)
        # Entity extraction (URLs, phone numbers, UPI IDs)
```

For production, can be upgraded to **DistilBERT** for better accuracy.

### (C) Domain Similarity Engine

Detects typosquatting and impersonation:

```python
LEGITIMATE_DOMAINS = [
    'google.com', 'paytm.com', 'phonepe.com',
    'icicibank.com', 'hdfcbank.com', ...
]

def check_typosquatting(domain: str):
    # Levenshtein distance
    # Jaro-Winkler similarity
    # Returns: (score, similar_domain, similarity)
    
    if 0.7 < similarity < 0.95:
        score = 40 + (similarity - 0.7) * 200
```

Examples:
- `gooogle.com` → Similar to `google.com` (typosquatting)
- `paytm-secure.com` → Similar to `paytm.com` (fake domain)

### (D) Behavioral Anomaly Detector

Detects unusual patterns:

```python
def analyze_transaction_behavior():
    # New payee + high amount = risky
    if is_new_payee and amount > 5000:
        score += 35
    
    # Unusual amount (3x typical)
    if amount > typical_amount * 3:
        score += 40
    
    # High velocity (5+ transactions/hour)
    if transaction_velocity > 5:
        score += 30
    
    # Unusual time (2 AM - 5 AM)
    if is_unusual_time:
        score += 20
```

### (E) Risk Score Combining

Combines all signals into final score:

```python
final_risk = (
    rules_score * 0.50 +
    nlp_score * 0.30 +
    anomaly_score * 0.20
)
```

Weights are adjusted by the Learning Layer based on feedback.

---

## 🟧 LAYER 4: ACTION (Autonomous Control)

**File:** `action_engine.py`

This is where the agent becomes truly **AGENTIC** by taking autonomous actions.

### Decision Flow

```
Risk Score → Risk Level → Action Decision → Platform-Specific Actions
```

### Chrome Extension Actions

#### LOW Risk (< 40):
```python
{
    'type': 'silent_monitor',
    'track': True,
    'send_analytics': True
}
```
→ User continues normally, agent monitors silently

#### MEDIUM Risk (40-69):
```python
{
    'type': 'show_popup',
    'severity': 'warning',
    'title': '⚠️ Security Warning',
    'message': 'Potential phishing detected',
    'buttons': ['Cancel', 'Proceed Anyway']
}
```
→ Warning popup, user can choose

#### HIGH Risk (70-100):
```python
{
    'type': 'block_navigation',
    'target_url': 'http://fraudsite.com',
    'redirect_to': 'chrome://warning-page',
    'message': '🛑 This website has been blocked'
}
```
→ **AUTONOMOUS BLOCK** - Agent takes control

**Chrome Extension Implementation:**
```javascript
chrome.tabs.update({ url: "chrome://warning-page" });
// Navigation blocked autonomously
```

#### Special: QR Code Fraud
```python
{
    'type': 'block_qr_usage',
    'message': '🛑 Fraudulent QR code detected'
}
```

#### Special: Redirect Chain
```python
{
    'type': 'stop_redirect',
    'message': '🛑 Suspicious redirect chain blocked'
}
```

### Android App Actions

#### LOW Risk:
```python
{
    'type': 'silent_monitor',
    'track': True,
    'log': True
}
```

#### MEDIUM Risk:
```python
{
    'type': 'show_alert',
    'severity': 'medium',
    'title': '⚠️ Fraud Warning',
    'message': 'Possible SMS scam detected',
    'buttons': ['OK'],
    'vibrate': False
}
```

#### HIGH Risk - UPI Transaction:
```python
{
    'type': 'abort_transaction',
    'message': '🛑 Payment blocked - fraud detected',
    'vibrate': True,
    'show_full_screen_alert': True
}

{
    'type': 'block_upi_intent',
    'intent_data': {...},
    'message': '🛑 Fraudulent UPI request blocked'
}
```

**Android Implementation:**
```kotlin
abortTransaction()  // Cancel payment autonomously
disablePayButton()  // Disable UI
showFullScreenAlert()  // Force user attention
```

#### Special: Screen Sharing Detection
```python
{
    'type': 'warn_screen_sharing',
    'message': '⚠️ Screen sharing apps detected',
    'apps': ['AnyDesk', 'TeamViewer']
}
```

#### Special: SIM Swap Detection
```python
{
    'type': 'sim_change_alert',
    'message': '⚠️ SIM recently changed - be cautious'
}
```

### UI Instructions

Action engine also generates UI presentation details:

```python
{
    'color': '#F44336',  # Red for high risk
    'icon': '🛑',
    'priority': 'max',
    'should_vibrate': True,
    'should_sound': True,
    'fullscreen': True,  # Critical risk
    'require_user_action': True
}
```

---

## 🟧 LAYER 5: LEARNING (Feedback Loop)

**File:** `learning_engine.py`

The agent learns and adapts from user feedback.

### Feedback Collection

```python
@app.post("/feedback")
async def submit_feedback(feedback: UserFeedback):
    """
    User provides feedback:
    - "This is safe" (marked fraud, but wasn't)
    - "This is fraud" (marked safe, but was fraud)
    """
```

### Learning Process

#### When User Says "SAFE":

```python
if feedback == "safe":
    # Add to whitelist
    whitelist['urls'].add(url)
    
    # Update metrics
    if was_flagged_as_fraud:
        metrics['false_positives'] += 1
        
        # Adjust weights (be less strict)
        weights['nlp_score'] -= 0.01
        weights['rules_score'] -= 0.01
```

**Result:** Next time this URL appears, risk score lowered by 50 points.

#### When User Says "FRAUD":

```python
if feedback == "fraud":
    # Add to blacklist
    blacklist['urls'].add(url)
    
    # Update metrics
    if was_not_flagged:
        metrics['false_negatives'] += 1
        
        # Adjust weights (be more strict)
        weights['nlp_score'] += 0.01
        weights['rules_score'] += 0.01
```

**Result:** Next time this URL appears, risk score increased by 60 points. Future similar patterns weighted higher.

### Whitelist/Blacklist Application

```python
def adjust_risk_score(entity_id, entity_type, original_score):
    # Check whitelist
    if entity_id in whitelist[entity_type]:
        adjusted_score = max(0, original_score - 50)
        return adjusted_score, ["Whitelisted based on feedback"]
    
    # Check blacklist (overrides whitelist)
    if entity_id in blacklist[entity_type]:
        adjusted_score = min(100, original_score + 60)
        return adjusted_score, ["Blacklisted based on feedback"]
```

### Weight Adjustment

Reasoning engine uses updated weights:

```python
# Default weights
weights = {
    'rules_score': 0.50,
    'nlp_score': 0.30,
    'anomaly_score': 0.20
}

# After learning (example)
weights = {
    'rules_score': 0.48,  # Adjusted down (false positives)
    'nlp_score': 0.31,    # Adjusted up (missed frauds)
    'anomaly_score': 0.21
}
```

### Metrics Tracking

```python
metrics = {
    'total_feedbacks': 1250,
    'true_positives': 450,   # Correctly flagged fraud
    'true_negatives': 720,   # Correctly allowed safe
    'false_positives': 60,   # Flagged safe as fraud
    'false_negatives': 20,   # Missed fraud
    'accuracy': 0.936,       # 93.6% accurate
    'false_positive_rate': 0.048  # 4.8% FP rate
}
```

### Adaptive Thresholds

```python
def adjust_threshold(false_positive_rate):
    # If too many false positives (> 15%)
    if false_positive_rate > 0.15:
        medium_threshold += 5  # 70 → 75 (less strict)
        high_threshold += 5    # 100 → 105
    
    # If very few false positives (< 5%)
    elif false_positive_rate < 0.05:
        medium_threshold -= 5  # 70 → 65 (more strict)
        high_threshold -= 5    # 100 → 95
```

### Persistence

All learning data saved to disk:

```
learning_data/
├── whitelist.json          # Trusted entities
├── blacklist.json          # Known fraud entities
├── feedback_history.json   # All user feedback
├── metrics.json            # Performance metrics
└── weight_adjustments.json # ML weight adjustments
```

Loaded on startup, saved periodically and on shutdown.

---

## 🔄 COMPLETE WORKFLOW EXAMPLE

### Example 1: SMS Fraud Detection

#### 1. **PERCEPTION** (Layer 2)

User receives SMS:
```
"Your account will be blocked. Verify immediately: bit.ly/verify123
Call: +91-9876543210"
```

Android app sends:
```python
{
    "message": "Your account will be blocked...",
    "sender": "VK-BANK",
    "is_unusual_time": True,  # Received at 2 AM
    "device_info": {
        "sim_changed_recently": False,
        "screen_sharing_apps": []
    }
}
```

#### 2. **REASONING** (Layer 3)

```python
# Rule-based
score = 0
score += 40  # "account will be blocked"
score += 40  # "verify immediately"
score += 20  # Contains URL
score += 25  # Suspicious sender pattern "VK-BANK"
score += 20  # Unusual time (2 AM)
# Rules total: 145

# NLP
nlp_score = 50  # High fear sentiment, fraud phrases
entities = {
    'urls': ['bit.ly/verify123'],
    'phone_numbers': ['+91-9876543210']
}

# Combine
final_score = 145 * 0.50 + 50 * 0.30 = 87.5
```

#### 3. **LEARNING** (Layer 5)

```python
# Check if sender was previously reported
if "VK-BANK" in blacklist['senders']:
    final_score += 60  # Boost to 147.5
```

#### 4. **POLICY & ACTION** (Layers 1 & 4)

```python
# Layer 1: Classify
risk_level = CRITICAL  # score > 100

# Layer 4: Take action
action = BLOCK

android_actions = {
    'type': 'block_sms_links',
    'message': '🛑 This SMS is fraudulent',
    'disable_click': True
}
```

#### 5. **EXECUTION**

Android app receives:
```json
{
    "risk_level": "critical",
    "risk_score": 147.5,
    "should_block": true,
    "action": "block",
    "android_actions": {
        "type": "block_sms_links",
        "message": "🛑 This SMS is fraudulent",
        "disable_click": true
    }
}
```

App autonomously:
- Disables all clickable links ❌
- Shows full-screen alert 📱
- Vibrates phone 📳
- Logs SMS for reporting 📝

User is protected **WITHOUT** clicking anything.

#### 6. **FEEDBACK**

User confirms: "Yes, this was fraud"

```python
learning_engine.process_feedback(
    entity_id="VK-BANK",
    entity_type="sender",
    feedback="fraud",
    original_risk_score=87.5
)

# Result:
# - Added to blacklist
# - Metrics updated: true_positive++
# - Weights adjusted slightly higher
```

Next time ANY message from "VK-BANK" appears → instant block.

---

### Example 2: UPI Collect Request

#### 1. **PERCEPTION**

User scans QR code showing:
```
upi://pay?pa=fraud@collect&pn=CustomerSupport&am=25000&cu=INR&mode=02
```

Android detects:
- `mode=02` = collect request
- Amount = ₹25,000
- New device just activated
- SIM changed 2 days ago

#### 2. **REASONING**

```python
# Rule-based
score = 0
score += 40  # UPI collect (not pay)
score += 35  # Very high amount (> ₹10,000)

# Behavioral anomaly
score += 40  # SIM changed recently
score += 20  # New device
score += 35  # New payee + high amount

# Total: 170
```

#### 3. **LEARNING**

Not in whitelist, check blacklist:
```python
if "fraud@collect" in blacklist['upi_ids']:
    score += 60  # Already reported by others
```

#### 4. **ACTION**

```python
risk_level = CRITICAL
action = ABORT_TRANSACTION

android_actions = [
    {
        'type': 'abort_transaction',
        'vibrate': True,
        'show_full_screen_alert': True
    },
    {
        'type': 'block_upi_intent',
        'message': '🛑 Fraudulent collect request blocked'
    },
    {
        'type': 'sim_change_alert',
        'message': 'Your SIM was recently changed'
    }
]
```

#### 5. **EXECUTION**

App autonomously:
- Aborts transaction immediately 🛑
- Disables "Pay" button ❌
- Shows: "COLLECT REQUEST BLOCKED - This is a scam. Merchants should send PAY requests, not COLLECT."
- Vibrates intensely 📳
- Warns about recent SIM change ⚠️

**User's ₹25,000 SAVED** 💰

---

## 📊 API ENDPOINTS

### Analysis Endpoints

```
POST /analyze/url          # Chrome extension URL analysis
POST /analyze/sms          # Android SMS analysis  
POST /analyze/transaction  # UPI transaction analysis
```

### Learning Endpoints

```
POST /feedback                     # Submit user feedback
GET  /learning/metrics             # Get learning statistics
GET  /learning/feedback-history    # View feedback history
```

### Agent Status

```
GET /agent/status    # View all 5 layers status
GET /health          # System health check
```

---

## 🚀 RUNNING THE SYSTEM

### Start Server

```bash
cd backend/logic
source venv/bin/activate
python main.py
```

Server starts on `http://localhost:8000`

### Startup Logs

```
============================================================
🤖 Starting AGENTIC FRAUD DETECTION API
============================================================
🟧 Layer 1: Agent Goal = Prevent the user from losing money to fraud
🟧 Layer 2: Perception Layer = ACTIVE
🟧 Layer 3: Reasoning Engine = INITIALIZED
🟧 Layer 4: Action Engine = READY
🟧 Layer 5: Learning Engine = LOADED
============================================================
✓ Auth service is reachable
📊 Learning Metrics: 1250 feedbacks processed
📊 Accuracy: 93.60%, FP Rate: 4.80%
```

---

## 🧪 TESTING THE AGENT

### Test URL Analysis

```bash
curl -X POST http://localhost:8000/analyze/url \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://gooogle.com/signin",
    "suspicious_keywords": ["urgent", "verify"],
    "typosquatting_score": 0.85,
    "similar_to_domain": "google.com"
  }'
```

Response:
```json
{
  "risk_level": "high",
  "risk_score": 78.5,
  "is_safe": false,
  "action": "block",
  "should_block": true,
  "message": "🛑 BLOCKED: Typosquatting detected",
  "chrome_actions": {
    "type": "block_navigation",
    "redirect_to": "chrome://warning-page"
  }
}
```

### Test Feedback

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "gooogle.com",
    "entity_type": "domain",
    "feedback": "fraud",
    "original_risk_score": 78.5,
    "user_id": "user123"
  }'
```

Response:
```json
{
  "message": "Added to blacklist. Will be blocked in future.",
  "entity_added_to_blacklist": true,
  "learning_applied": true
}
```

### View Agent Status

```bash
curl http://localhost:8000/agent/status
```

---

## 📈 MONITORING & METRICS

### Key Metrics

```python
GET /learning/metrics
```

Returns:
- **Accuracy**: Overall detection accuracy
- **False Positive Rate**: Legitimate flagged as fraud
- **False Negative Rate**: Fraud missed
- **True Positive Rate**: Fraud correctly detected
- **Whitelist/Blacklist Sizes**
- **Weight Adjustments**

### Performance Goals

- Accuracy: > 95%
- False Positive Rate: < 5%
- False Negative Rate: < 2%
- Response Time: < 200ms

---

## 🔧 CONFIGURATION

### Adjust Risk Thresholds

Edit `agent_policy.py`:

```python
class AgentPolicy:
    low_threshold: int = 40     # Change to 35 for stricter
    medium_threshold: int = 70  # Change to 65 for stricter
    high_threshold: int = 100
```

### Adjust Combining Weights

Edit `agent_policy.py`:

```python
weights = {
    'rules_score': 0.50,    # Rule-based weight
    'nlp_score': 0.30,      # NLP weight
    'anomaly_score': 0.20   # Behavioral weight
}
```

### Add New Fraud Keywords

Edit `ml_reasoning.py`:

```python
SMS_FRAUD_KEYWORDS = {
    'your custom keyword': 40,  # Risk points
    ...
}
```

---

## 📚 CODE STRUCTURE

```
backend/logic/
├── agent_policy.py      # 🟧 Layer 1: Policy & Goals
├── models.py            # 🟧 Layer 2: Perception Models
├── ml_reasoning.py      # 🟧 Layer 3: Reasoning Engines
├── action_engine.py     # 🟧 Layer 4: Autonomous Actions
├── learning_engine.py   # 🟧 Layer 5: Learning & Feedback
├── main.py              # 🔄 Orchestration & API
├── risk_scoring.py      # Legacy risk calculation
├── auth.py              # Authentication
└── learning_data/       # Persistent learning storage
    ├── whitelist.json
    ├── blacklist.json
    ├── feedback_history.json
    ├── metrics.json
    └── weight_adjustments.json
```

---

## 🎓 KEY TAKEAWAYS

### This is TRUE Agentic AI because:

1. **Goal-Driven**: Everything optimizes for "prevent user from losing money"
2. **Autonomous**: Agent takes actions (block, warn) WITHOUT waiting for user
3. **Adaptive**: Learns from feedback and adjusts behavior
4. **Comprehensive**: Perceives multi-modal data (URL, SMS, device, behavioral)
5. **Intelligent**: Uses ML reasoning (NLP, similarity, anomaly detection)

### The Agent is NOT just:
- ❌ A simple rule engine
- ❌ A passive API that only reports scores
- ❌ A static system that never learns

### The Agent IS:
- ✅ An autonomous fraud prevention system
- ✅ A learning system that improves over time
- ✅ An action-taking entity that protects users
- ✅ A multi-layer intelligent system

---

## 🚨 SAFETY NOTES

1. **False Positives**: Agent monitors FP rate and adjusts automatically
2. **User Override**: Users can always provide feedback to correct mistakes
3. **Graceful Degradation**: If reasoning fails, falls back to rule-based
4. **Audit Trail**: All actions logged for review
5. **Reversible**: Blocked entities can be unblocked via feedback

---

## 📞 SUPPORT

For questions or issues:
- Check logs in console
- Review `/agent/status` endpoint
- Check `/learning/metrics` for performance
- Submit feedback via `/feedback` endpoint

---

## 🏆 SUCCESS METRICS

After deployment, monitor:
- ✅ Fraud attempts blocked: > 95%
- ✅ False positives: < 5%
- ✅ User satisfaction: Measured via feedback
- ✅ Learning accuracy: Improves over time
- ✅ Response time: < 200ms average

---

**The Agentic AI fraud detection system is now complete and operational!** 🎉
