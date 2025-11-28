"""
🟧 LAYER 1: AGENT POLICY
Core objective and decision-making framework for the fraud prevention agent
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class AgentGoal(Enum):
    """The agent's primary objective"""
    PREVENT_FRAUD = "Prevent the user from losing money to fraud"
    MAXIMIZE_SAFETY = "Maximize user safety while minimizing false positives"
    PROTECT_PRIVACY = "Protect user data and privacy"


class RiskLevel(Enum):
    """Risk classification levels"""
    LOW = "low"           # 0-39: Safe, allow
    MEDIUM = "medium"     # 40-69: Suspicious, warn
    HIGH = "high"         # 70-100: Dangerous, block
    CRITICAL = "critical" # >100: Emergency, immediate block


class ActionType(Enum):
    """Types of actions the agent can take"""
    ALLOW = "allow"                    # Let user continue
    MONITOR = "monitor"                # Silently track
    WARN = "warn"                      # Show warning popup
    CONFIRM = "confirm"                # Request user confirmation
    BLOCK = "block"                    # Stop action immediately
    ABORT_TRANSACTION = "abort"        # Cancel payment/transaction
    REDIRECT = "redirect"              # Navigate to safe page
    DISABLE_ACTION = "disable"         # Disable UI elements


@dataclass
class AgentPolicy:
    """
    Core policy defining agent behavior based on risk levels
    This is the hardcoded objective that drives all agent decisions
    """
    
    # Primary goal
    goal: str = AgentGoal.PREVENT_FRAUD.value
    
    # Risk thresholds
    low_threshold: int = 40
    medium_threshold: int = 70
    high_threshold: int = 100
    
    # Decision weights (for combining multiple risk signals)
    weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                'rules_score': 0.50,      # Rule-based reasoning weight
                'nlp_score': 0.30,        # NLP model weight
                'anomaly_score': 0.20,    # Behavioral anomaly weight
            }
    
    def classify_risk(self, score: float) -> RiskLevel:
        """
        Classify risk level based on score
        
        Args:
            score: Risk score (0-150)
            
        Returns:
            RiskLevel enum
        """
        if score < self.low_threshold:
            return RiskLevel.LOW
        elif score < self.medium_threshold:
            return RiskLevel.MEDIUM
        elif score < self.high_threshold:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def determine_action(self, risk_level: RiskLevel, context: Dict[str, Any]) -> ActionType:
        """
        Determine what action to take based on risk level and context
        This is the core decision-making logic
        
        Args:
            risk_level: Classified risk level
            context: Additional context (platform, transaction_type, etc.)
            
        Returns:
            ActionType enum
        """
        platform = context.get('platform', 'unknown')  # 'chrome' or 'android'
        transaction_type = context.get('type', 'unknown')  # 'url', 'sms', 'upi', etc.
        
        # LOW RISK: Allow with monitoring
        if risk_level == RiskLevel.LOW:
            return ActionType.MONITOR
        
        # MEDIUM RISK: Warn and confirm
        elif risk_level == RiskLevel.MEDIUM:
            # For financial transactions, be more cautious
            if transaction_type in ['upi', 'payment', 'transaction']:
                return ActionType.CONFIRM
            return ActionType.WARN
        
        # HIGH RISK: Block immediately
        elif risk_level == RiskLevel.HIGH:
            if transaction_type == 'upi' and context.get('intent_type') == 'collect':
                return ActionType.ABORT_TRANSACTION
            elif platform == 'chrome':
                return ActionType.REDIRECT  # Redirect to warning page
            return ActionType.BLOCK
        
        # CRITICAL RISK: Emergency block
        else:  # CRITICAL
            if transaction_type == 'upi':
                return ActionType.ABORT_TRANSACTION
            elif platform == 'chrome':
                return ActionType.REDIRECT
            return ActionType.BLOCK
    
    def get_action_message(self, action: ActionType, risk_level: RiskLevel, details: Dict[str, Any]) -> str:
        """
        Generate user-facing message for each action type
        
        Args:
            action: Action to take
            risk_level: Risk level
            details: Additional details about the threat
            
        Returns:
            User-facing message string
        """
        messages = {
            ActionType.MONITOR: "✅ This action appears safe. Monitoring for your protection.",
            
            ActionType.WARN: f"⚠️ Warning: Potential {details.get('fraud_type', 'fraud')} detected. "
                            f"Risk Level: {risk_level.value.upper()}. Proceed with caution.",
            
            ActionType.CONFIRM: f"⚠️ This action requires confirmation. "
                               f"{details.get('fraud_type', 'Suspicious activity')} detected. "
                               f"Are you sure you want to continue?",
            
            ActionType.BLOCK: f"🛑 BLOCKED: {details.get('fraud_type', 'Fraudulent activity')} detected. "
                             f"This action has been blocked for your safety.",
            
            ActionType.ABORT_TRANSACTION: f"🛑 TRANSACTION ABORTED: {details.get('fraud_type', 'Fraud')} detected. "
                                         f"Payment has been cancelled to protect your money.",
            
            ActionType.REDIRECT: f"🛑 Navigation blocked. This website is dangerous. "
                                f"Redirecting to safety page...",
            
            ActionType.DISABLE_ACTION: f"⚠️ This action has been disabled. "
                                      f"{details.get('fraud_type', 'Suspicious activity')} detected."
        }
        
        return messages.get(action, "Action taken for your protection.")
    
    def should_learn_from_feedback(self, action: ActionType, feedback: str) -> bool:
        """
        Determine if agent should update its learning from user feedback
        
        Args:
            action: Action that was taken
            feedback: User feedback ('safe', 'fraud', 'unsure')
            
        Returns:
            Boolean indicating if learning should occur
        """
        # Only learn from definitive feedback on warned/blocked actions
        if feedback in ['safe', 'fraud']:
            if action in [ActionType.WARN, ActionType.CONFIRM, ActionType.BLOCK]:
                return True
        return False
    
    def adjust_threshold(self, false_positive_rate: float) -> None:
        """
        Dynamically adjust thresholds based on false positive rate
        
        Args:
            false_positive_rate: Rate of false positives (0.0-1.0)
        """
        # If too many false positives, increase thresholds (be less strict)
        if false_positive_rate > 0.15:  # More than 15% false positives
            self.medium_threshold = min(75, self.medium_threshold + 5)
            self.high_threshold = min(105, self.high_threshold + 5)
        
        # If very few false positives, decrease thresholds (be more strict)
        elif false_positive_rate < 0.05:  # Less than 5% false positives
            self.medium_threshold = max(65, self.medium_threshold - 5)
            self.high_threshold = max(95, self.high_threshold - 5)


# Global agent policy instance
agent_policy = AgentPolicy()


def get_agent_goal() -> str:
    """Get the agent's primary goal"""
    return agent_policy.goal


def classify_and_act(score: float, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main decision function: Classify risk and determine action
    
    Args:
        score: Risk score
        context: Context dictionary with platform, type, etc.
        
    Returns:
        Dictionary with risk_level, action, and message
    """
    risk_level = agent_policy.classify_risk(score)
    action = agent_policy.determine_action(risk_level, context)
    
    details = {
        'fraud_type': context.get('fraud_type', 'fraud'),
        'risk_score': score
    }
    
    message = agent_policy.get_action_message(action, risk_level, details)
    
    return {
        'risk_level': risk_level.value,
        'action': action.value,
        'message': message,
        'should_block': action in [ActionType.BLOCK, ActionType.ABORT_TRANSACTION, ActionType.REDIRECT],
        'requires_confirmation': action in [ActionType.CONFIRM, ActionType.WARN]
    }
