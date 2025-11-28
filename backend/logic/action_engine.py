"""
🟧 LAYER 4: ACTION LAYER (Autonomous Agent Actions)
Where the agent takes autonomous control based on risk assessment
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

from agent_policy import ActionType, RiskLevel, classify_and_act

logger = logging.getLogger(__name__)


class Platform(str, Enum):
    """Platform types"""
    CHROME = "chrome"
    ANDROID = "android"
    WEB = "web"
    UNKNOWN = "unknown"


class ThreatType(str, Enum):
    """Types of threats"""
    URL = "url"
    SMS = "sms"
    UPI = "upi"
    TRANSACTION = "transaction"
    QR_CODE = "qr_code"
    DOMAIN = "domain"
    REDIRECT = "redirect"


@dataclass
class ActionContext:
    """Context for action decisions"""
    platform: Platform
    threat_type: ThreatType
    risk_score: float
    fraud_type: str
    entity_id: str  # URL, phone number, UPI ID, etc.
    user_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class ActionEngine:
    """
    Autonomous action engine that takes control based on risk levels
    This is where the agent becomes truly AGENTIC
    """
    
    def __init__(self):
        self.action_history = []  # Track all actions taken
        self.blocked_entities = set()  # Entities currently blocked
    
    def decide_and_act(self, context: ActionContext) -> Dict[str, Any]:
        """
        Main decision point: Analyze risk and take autonomous action
        
        This is the core of agentic behavior:
        - LOW risk: Allow and monitor
        - MEDIUM risk: Warn user
        - HIGH risk: Block autonomously
        - CRITICAL: Emergency block
        
        Args:
            context: ActionContext with all necessary information
            
        Returns:
            Action response with instructions for client
        """
        # Get classification and action from policy layer
        policy_context = {
            'platform': context.platform.value,
            'type': context.threat_type.value,
            'fraud_type': context.fraud_type,
            'intent_type': context.additional_data.get('intent_type') if context.additional_data else None
        }
        
        decision = classify_and_act(context.risk_score, policy_context)
        
        # Build action response
        action_response = self._build_action_response(
            context=context,
            decision=decision
        )
        
        # Log action
        self._log_action(context, action_response)
        
        # Add to blocked entities if blocking
        if action_response['should_block']:
            self.blocked_entities.add(context.entity_id)
        
        return action_response
    
    def _build_action_response(
        self,
        context: ActionContext,
        decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build detailed action response for client
        """
        action_type = ActionType(decision['action'])
        risk_level = RiskLevel(decision['risk_level'])
        
        response = {
            'action': action_type.value,
            'risk_level': risk_level.value,
            'risk_score': context.risk_score,
            'should_block': decision['should_block'],
            'requires_confirmation': decision['requires_confirmation'],
            'message': decision['message'],
            'entity_id': context.entity_id,
            'fraud_type': context.fraud_type,
            'timestamp': None  # Will be set by caller
        }
        
        # Add platform-specific action details
        if context.platform == Platform.CHROME:
            response['chrome_actions'] = self._get_chrome_actions(action_type, context)
        elif context.platform == Platform.ANDROID:
            response['android_actions'] = self._get_android_actions(action_type, context)
        
        # Add UI instructions
        response['ui_instructions'] = self._get_ui_instructions(action_type, risk_level, context)
        
        return response
    
    def _get_chrome_actions(self, action: ActionType, context: ActionContext) -> Dict[str, Any]:
        """
        Get Chrome-specific action instructions
        
        Chrome Extension will implement these actions:
        - Block navigation
        - Block QR usage
        - Stop redirect
        - Show popup warning
        """
        actions = {
            'type': 'chrome_action',
            'actions': []
        }
        
        if action == ActionType.BLOCK or action == ActionType.REDIRECT:
            actions['actions'].append({
                'type': 'block_navigation',
                'target_url': context.entity_id,
                'redirect_to': 'chrome://warning-page',
                'message': '🛑 This website has been blocked for your safety'
            })
        
        elif action == ActionType.WARN or action == ActionType.CONFIRM:
            actions['actions'].append({
                'type': 'show_popup',
                'severity': 'warning' if action == ActionType.WARN else 'confirm',
                'title': '⚠️ Security Warning',
                'message': f'Potential {context.fraud_type} detected',
                'buttons': ['Cancel', 'Proceed Anyway'] if action == ActionType.CONFIRM else ['OK']
            })
        
        elif action == ActionType.MONITOR:
            actions['actions'].append({
                'type': 'silent_monitor',
                'track': True,
                'send_analytics': True
            })
        
        # Special handling for QR codes
        if context.threat_type == ThreatType.QR_CODE and action in [ActionType.BLOCK, ActionType.REDIRECT]:
            actions['actions'].append({
                'type': 'block_qr_usage',
                'message': '🛑 Fraudulent QR code detected - scanning blocked'
            })
        
        # Special handling for redirects
        if context.threat_type == ThreatType.REDIRECT and action in [ActionType.BLOCK, ActionType.REDIRECT]:
            actions['actions'].append({
                'type': 'stop_redirect',
                'message': '🛑 Suspicious redirect chain blocked'
            })
        
        return actions
    
    def _get_android_actions(self, action: ActionType, context: ActionContext) -> Dict[str, Any]:
        """
        Get Android-specific action instructions
        
        Android App will implement these actions:
        - Block UPI intent
        - Stop collect request
        - Show high-priority alert
        - Disable "Pay" button
        - Abort transaction
        """
        actions = {
            'type': 'android_action',
            'actions': []
        }
        
        if action == ActionType.ABORT_TRANSACTION:
            actions['actions'].append({
                'type': 'abort_transaction',
                'message': '🛑 Payment blocked - fraud detected',
                'vibrate': True,
                'show_full_screen_alert': True
            })
            
            # Block UPI intent
            if context.threat_type == ThreatType.UPI:
                actions['actions'].append({
                    'type': 'block_upi_intent',
                    'intent_data': context.additional_data.get('upi_intent') if context.additional_data else None,
                    'message': '🛑 Fraudulent UPI request blocked'
                })
        
        elif action == ActionType.BLOCK:
            if context.threat_type == ThreatType.SMS:
                actions['actions'].append({
                    'type': 'block_sms_links',
                    'message': '⚠️ Links in this SMS are dangerous',
                    'disable_click': True
                })
            elif context.threat_type == ThreatType.UPI:
                actions['actions'].append({
                    'type': 'disable_pay_button',
                    'message': '🛑 Payment blocked for your safety'
                })
        
        elif action == ActionType.WARN or action == ActionType.CONFIRM:
            actions['actions'].append({
                'type': 'show_alert',
                'severity': 'high' if action == ActionType.CONFIRM else 'medium',
                'title': '⚠️ Fraud Warning',
                'message': f'Possible {context.fraud_type} detected',
                'buttons': ['Cancel', 'I Understand the Risk'] if action == ActionType.CONFIRM else ['OK'],
                'vibrate': action == ActionType.CONFIRM
            })
        
        elif action == ActionType.MONITOR:
            actions['actions'].append({
                'type': 'silent_monitor',
                'track': True,
                'log': True
            })
        
        # Device security actions
        if context.additional_data:
            device_data = context.additional_data.get('device_info', {})
            
            if device_data.get('screen_sharing_apps'):
                actions['actions'].append({
                    'type': 'warn_screen_sharing',
                    'message': '⚠️ Screen sharing apps detected - do not share your screen with unknown contacts',
                    'apps': device_data['screen_sharing_apps']
                })
            
            if device_data.get('sim_changed_recently'):
                actions['actions'].append({
                    'type': 'sim_change_alert',
                    'message': '⚠️ Your SIM was recently changed. Be extra cautious with financial transactions.'
                })
        
        return actions
    
    def _get_ui_instructions(
        self,
        action: ActionType,
        risk_level: RiskLevel,
        context: ActionContext
    ) -> Dict[str, Any]:
        """
        Get UI instructions for displaying alerts/warnings
        """
        # Color coding
        colors = {
            RiskLevel.LOW: '#4CAF50',      # Green
            RiskLevel.MEDIUM: '#FF9800',   # Orange
            RiskLevel.HIGH: '#F44336',     # Red
            RiskLevel.CRITICAL: '#D32F2F'  # Dark Red
        }
        
        # Icon selection
        icons = {
            ActionType.ALLOW: '✅',
            ActionType.MONITOR: '👀',
            ActionType.WARN: '⚠️',
            ActionType.CONFIRM: '⚠️',
            ActionType.BLOCK: '🛑',
            ActionType.ABORT_TRANSACTION: '🛑',
            ActionType.REDIRECT: '🛑',
            ActionType.DISABLE_ACTION: '🚫'
        }
        
        instructions = {
            'color': colors.get(risk_level, '#757575'),
            'icon': icons.get(action, '⚠️'),
            'priority': self._get_priority(risk_level),
            'should_vibrate': risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            'should_sound': risk_level == RiskLevel.CRITICAL,
            'auto_dismiss': action in [ActionType.MONITOR, ActionType.ALLOW],
            'dismiss_timeout': 3000 if action == ActionType.MONITOR else None,
            'require_user_action': action in [ActionType.CONFIRM, ActionType.WARN, ActionType.BLOCK],
            'fullscreen': risk_level == RiskLevel.CRITICAL
        }
        
        return instructions
    
    def _get_priority(self, risk_level: RiskLevel) -> str:
        """Get notification priority"""
        priority_map = {
            RiskLevel.LOW: 'low',
            RiskLevel.MEDIUM: 'default',
            RiskLevel.HIGH: 'high',
            RiskLevel.CRITICAL: 'max'
        }
        return priority_map.get(risk_level, 'default')
    
    def _log_action(self, context: ActionContext, response: Dict[str, Any]) -> None:
        """Log action for audit trail"""
        log_entry = {
            'timestamp': None,  # Will be set by caller
            'context': context,
            'response': response
        }
        self.action_history.append(log_entry)
        
        logger.info(
            f"Action taken: {response['action']} for {context.threat_type.value} "
            f"(risk: {context.risk_score:.2f}, entity: {context.entity_id})"
        )
    
    def is_blocked(self, entity_id: str) -> bool:
        """Check if entity is currently blocked"""
        return entity_id in self.blocked_entities
    
    def unblock(self, entity_id: str) -> bool:
        """Unblock an entity (used when user provides feedback that it's safe)"""
        if entity_id in self.blocked_entities:
            self.blocked_entities.remove(entity_id)
            logger.info(f"Unblocked entity: {entity_id}")
            return True
        return False
    
    def get_action_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent action history"""
        return self.action_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear action history"""
        self.action_history.clear()
        logger.info("Action history cleared")


# ============================================================
# HELPER FUNCTIONS FOR SPECIFIC ACTIONS
# ============================================================

def create_chrome_warning_page_data(context: ActionContext) -> Dict[str, Any]:
    """
    Create data for Chrome warning page
    Used when redirecting to chrome://warning-page
    """
    return {
        'blocked_url': context.entity_id,
        'fraud_type': context.fraud_type,
        'risk_score': context.risk_score,
        'reason': f"This website was identified as potential {context.fraud_type}",
        'recommendations': [
            "Do not enter any personal information",
            "Do not enter credit card or banking details",
            "Close this tab and report the website",
            "Run a security scan on your device"
        ],
        'support_link': 'https://support.fraud-sentinel.com',
        'report_link': 'https://report.fraud-sentinel.com'
    }


def create_android_alert_data(context: ActionContext, action: ActionType) -> Dict[str, Any]:
    """
    Create data for Android alert dialog
    """
    alert_data = {
        'title': '🛑 Security Alert' if action == ActionType.BLOCK else '⚠️ Warning',
        'message': f"Potential {context.fraud_type} detected",
        'risk_score': context.risk_score,
        'fraud_type': context.fraud_type
    }
    
    # Add specific warnings based on threat type
    if context.threat_type == ThreatType.UPI:
        alert_data['warnings'] = [
            "Verify the recipient before proceeding",
            "Check if the amount is correct",
            "Be cautious of collect requests"
        ]
    elif context.threat_type == ThreatType.SMS:
        alert_data['warnings'] = [
            "Do not click any links in this SMS",
            "Do not call any numbers in this SMS",
            "Do not share OTP or passwords"
        ]
    
    return alert_data


# Global action engine instance
action_engine = ActionEngine()
