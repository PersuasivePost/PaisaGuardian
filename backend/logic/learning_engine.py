"""
🟧 LAYER 5: LEARNING LAYER (Feedback Loop)
The agent adapts and learns from user feedback
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class FeedbackType:
    """Feedback types"""
    SAFE = "safe"
    FRAUD = "fraud"
    UNSURE = "unsure"


class LearningEngine:
    """
    Learning engine that adapts based on user feedback
    Manages whitelists, blacklists, and adjusts detection weights
    """
    
    def __init__(self, data_dir: str = "./learning_data"):
        """
        Initialize learning engine
        
        Args:
            data_dir: Directory to store learning data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Whitelists and blacklists
        self.whitelist: Dict[str, Set[str]] = {
            'urls': set(),
            'domains': set(),
            'upi_ids': set(),
            'senders': set(),
            'phone_numbers': set()
        }
        
        self.blacklist: Dict[str, Set[str]] = {
            'urls': set(),
            'domains': set(),
            'upi_ids': set(),
            'senders': set(),
            'phone_numbers': set()
        }
        
        # Feedback history
        self.feedback_history: List[Dict] = []
        
        # Metrics for learning
        self.metrics = {
            'total_feedbacks': 0,
            'safe_feedbacks': 0,
            'fraud_feedbacks': 0,
            'false_positives': 0,  # User said safe, we said fraud
            'false_negatives': 0,  # User said fraud, we said safe
            'true_positives': 0,   # User said fraud, we said fraud
            'true_negatives': 0    # User said safe, we said safe
        }
        
        # Weight adjustments
        self.weight_adjustments = {
            'rules_score': 0.0,
            'nlp_score': 0.0,
            'anomaly_score': 0.0
        }
        
        # Load existing data
        self._lock = threading.Lock()
        self.load_data()
    
    def process_feedback(
        self,
        entity_id: str,
        entity_type: str,
        feedback: str,
        original_risk_score: float,
        user_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Process user feedback and update learning data
        
        Args:
            entity_id: The entity being rated (URL, UPI ID, phone number, etc.)
            entity_type: Type of entity (url, upi_id, sender, domain, etc.)
            feedback: User feedback (safe, fraud, unsure)
            original_risk_score: The risk score we gave
            user_id: User providing feedback
            comment: Optional user comment
            
        Returns:
            Dictionary with learning results
        """
        with self._lock:
            result = {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'feedback': feedback,
                'added_to_whitelist': False,
                'added_to_blacklist': False,
                'learning_applied': False,
                'message': ''
            }
            
            # Update metrics
            self.metrics['total_feedbacks'] += 1
            
            # Determine if this was a false positive/negative
            was_flagged_as_fraud = original_risk_score >= 40  # Medium or higher
            
            if feedback == FeedbackType.SAFE:
                self.metrics['safe_feedbacks'] += 1
                
                # Add to whitelist
                if entity_type in self.whitelist:
                    self.whitelist[entity_type].add(entity_id)
                    result['added_to_whitelist'] = True
                    result['message'] = f"Added to whitelist. Will be trusted in future."
                
                # Update metrics
                if was_flagged_as_fraud:
                    self.metrics['false_positives'] += 1
                    result['learning_applied'] = True
                    # Adjust weights to be less strict
                    self._adjust_weights_for_false_positive(original_risk_score)
                else:
                    self.metrics['true_negatives'] += 1
            
            elif feedback == FeedbackType.FRAUD:
                self.metrics['fraud_feedbacks'] += 1
                
                # Add to blacklist
                if entity_type in self.blacklist:
                    self.blacklist[entity_type].add(entity_id)
                    result['added_to_blacklist'] = True
                    result['message'] = f"Added to blacklist. Will be blocked in future."
                
                # Update metrics
                if was_flagged_as_fraud:
                    self.metrics['true_positives'] += 1
                else:
                    self.metrics['false_negatives'] += 1
                    result['learning_applied'] = True
                    # Adjust weights to be more strict
                    self._adjust_weights_for_false_negative(original_risk_score)
            
            # Store feedback
            feedback_entry = {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'feedback': feedback,
                'original_risk_score': original_risk_score,
                'user_id': user_id,
                'comment': comment,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.feedback_history.append(feedback_entry)
            
            # Periodically save data
            if len(self.feedback_history) % 10 == 0:
                self.save_data()
            
            return result
    
    def _adjust_weights_for_false_positive(self, risk_score: float) -> None:
        """
        Adjust detection weights when we have a false positive
        Makes the system less strict
        """
        # Decrease weights slightly
        adjustment = -0.01
        
        # Adjust based on which component likely caused the false positive
        if risk_score >= 70:  # High risk - likely NLP or rules too strict
            self.weight_adjustments['nlp_score'] += adjustment
            self.weight_adjustments['rules_score'] += adjustment
        elif risk_score >= 40:  # Medium risk - likely rules too strict
            self.weight_adjustments['rules_score'] += adjustment * 2
        
        logger.info(f"Adjusted weights for false positive: {self.weight_adjustments}")
    
    def _adjust_weights_for_false_negative(self, risk_score: float) -> None:
        """
        Adjust detection weights when we have a false negative
        Makes the system more strict
        """
        # Increase weights slightly
        adjustment = 0.01
        
        # Adjust based on what we missed
        if risk_score < 20:  # Very low score - missed obvious fraud
            self.weight_adjustments['nlp_score'] += adjustment * 2
            self.weight_adjustments['rules_score'] += adjustment * 2
            self.weight_adjustments['anomaly_score'] += adjustment
        elif risk_score < 40:  # Low-medium score
            self.weight_adjustments['nlp_score'] += adjustment
            self.weight_adjustments['rules_score'] += adjustment
        
        logger.info(f"Adjusted weights for false negative: {self.weight_adjustments}")
    
    def check_whitelist(self, entity_id: str, entity_type: str) -> bool:
        """
        Check if entity is whitelisted
        
        Returns:
            True if whitelisted
        """
        if entity_type in self.whitelist:
            return entity_id in self.whitelist[entity_type]
        return False
    
    def check_blacklist(self, entity_id: str, entity_type: str) -> bool:
        """
        Check if entity is blacklisted
        
        Returns:
            True if blacklisted
        """
        if entity_type in self.blacklist:
            return entity_id in self.blacklist[entity_type]
        return False
    
    def adjust_risk_score(
        self,
        entity_id: str,
        entity_type: str,
        original_score: float
    ) -> Tuple[float, List[str]]:
        """
        Adjust risk score based on whitelist/blacklist
        
        Returns:
            Tuple of (adjusted_score, reasons)
        """
        reasons = []
        adjusted_score = original_score
        
        # Check whitelist
        if self.check_whitelist(entity_id, entity_type):
            adjusted_score = max(0, original_score - 50)
            reasons.append("Whitelisted based on user feedback")
        
        # Check blacklist (overrides whitelist)
        if self.check_blacklist(entity_id, entity_type):
            adjusted_score = min(100, original_score + 60)
            reasons.append("Blacklisted based on user feedback")
        
        return adjusted_score, reasons
    
    def get_weight_adjustments(self) -> Dict[str, float]:
        """
        Get current weight adjustments for risk combiner
        
        Returns:
            Dictionary of weight adjustments
        """
        return self.weight_adjustments.copy()
    
    def get_false_positive_rate(self) -> float:
        """
        Calculate false positive rate
        
        Returns:
            False positive rate (0.0-1.0)
        """
        total_positives = self.metrics['false_positives'] + self.metrics['true_positives']
        if total_positives == 0:
            return 0.0
        return self.metrics['false_positives'] / total_positives
    
    def get_metrics(self) -> Dict[str, any]:
        """
        Get learning metrics
        
        Returns:
            Dictionary with all metrics
        """
        metrics = self.metrics.copy()
        
        # Calculate rates
        total = metrics['total_feedbacks']
        if total > 0:
            metrics['false_positive_rate'] = self.get_false_positive_rate()
            
            total_negatives = metrics['false_negatives'] + metrics['true_negatives']
            if total_negatives > 0:
                metrics['false_negative_rate'] = metrics['false_negatives'] / total_negatives
            else:
                metrics['false_negative_rate'] = 0.0
            
            # Accuracy
            correct = metrics['true_positives'] + metrics['true_negatives']
            metrics['accuracy'] = correct / total if total > 0 else 0.0
        else:
            metrics['false_positive_rate'] = 0.0
            metrics['false_negative_rate'] = 0.0
            metrics['accuracy'] = 0.0
        
        # Whitelist/blacklist sizes
        metrics['whitelist_sizes'] = {
            entity_type: len(entities)
            for entity_type, entities in self.whitelist.items()
        }
        metrics['blacklist_sizes'] = {
            entity_type: len(entities)
            for entity_type, entities in self.blacklist.items()
        }
        
        return metrics
    
    def get_feedback_history(
        self,
        limit: int = 100,
        entity_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get feedback history with optional filters
        
        Args:
            limit: Maximum number of entries to return
            entity_type: Filter by entity type
            user_id: Filter by user ID
            
        Returns:
            List of feedback entries
        """
        history = self.feedback_history
        
        # Apply filters
        if entity_type:
            history = [h for h in history if h['entity_type'] == entity_type]
        if user_id:
            history = [h for h in history if h['user_id'] == user_id]
        
        return history[-limit:]
    
    def remove_from_whitelist(self, entity_id: str, entity_type: str) -> bool:
        """Remove entity from whitelist"""
        if entity_type in self.whitelist and entity_id in self.whitelist[entity_type]:
            self.whitelist[entity_type].remove(entity_id)
            logger.info(f"Removed from whitelist: {entity_type}:{entity_id}")
            return True
        return False
    
    def remove_from_blacklist(self, entity_id: str, entity_type: str) -> bool:
        """Remove entity from blacklist"""
        if entity_type in self.blacklist and entity_id in self.blacklist[entity_type]:
            self.blacklist[entity_type].remove(entity_id)
            logger.info(f"Removed from blacklist: {entity_type}:{entity_id}")
            return True
        return False
    
    def save_data(self) -> None:
        """Save learning data to disk"""
        try:
            # Save whitelists
            whitelist_file = self.data_dir / 'whitelist.json'
            with open(whitelist_file, 'w') as f:
                json.dump(
                    {k: list(v) for k, v in self.whitelist.items()},
                    f,
                    indent=2
                )
            
            # Save blacklists
            blacklist_file = self.data_dir / 'blacklist.json'
            with open(blacklist_file, 'w') as f:
                json.dump(
                    {k: list(v) for k, v in self.blacklist.items()},
                    f,
                    indent=2
                )
            
            # Save feedback history
            history_file = self.data_dir / 'feedback_history.json'
            with open(history_file, 'w') as f:
                json.dump(self.feedback_history, f, indent=2)
            
            # Save metrics
            metrics_file = self.data_dir / 'metrics.json'
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            
            # Save weight adjustments
            weights_file = self.data_dir / 'weight_adjustments.json'
            with open(weights_file, 'w') as f:
                json.dump(self.weight_adjustments, f, indent=2)
            
            logger.info("Learning data saved successfully")
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def load_data(self) -> None:
        """Load learning data from disk"""
        try:
            # Load whitelists
            whitelist_file = self.data_dir / 'whitelist.json'
            if whitelist_file.exists():
                with open(whitelist_file, 'r') as f:
                    data = json.load(f)
                    self.whitelist = {k: set(v) for k, v in data.items()}
            
            # Load blacklists
            blacklist_file = self.data_dir / 'blacklist.json'
            if blacklist_file.exists():
                with open(blacklist_file, 'r') as f:
                    data = json.load(f)
                    self.blacklist = {k: set(v) for k, v in data.items()}
            
            # Load feedback history
            history_file = self.data_dir / 'feedback_history.json'
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.feedback_history = json.load(f)
            
            # Load metrics
            metrics_file = self.data_dir / 'metrics.json'
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    self.metrics.update(json.load(f))
            
            # Load weight adjustments
            weights_file = self.data_dir / 'weight_adjustments.json'
            if weights_file.exists():
                with open(weights_file, 'r') as f:
                    self.weight_adjustments.update(json.load(f))
            
            logger.info(
                f"Learning data loaded: "
                f"{sum(len(v) for v in self.whitelist.values())} whitelisted, "
                f"{sum(len(v) for v in self.blacklist.values())} blacklisted, "
                f"{len(self.feedback_history)} feedbacks"
            )
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
    
    def reset_learning(self) -> None:
        """Reset all learning data (use with caution!)"""
        with self._lock:
            for entity_type in self.whitelist:
                self.whitelist[entity_type].clear()
            for entity_type in self.blacklist:
                self.blacklist[entity_type].clear()
            
            self.feedback_history.clear()
            
            self.metrics = {
                'total_feedbacks': 0,
                'safe_feedbacks': 0,
                'fraud_feedbacks': 0,
                'false_positives': 0,
                'false_negatives': 0,
                'true_positives': 0,
                'true_negatives': 0
            }
            
            self.weight_adjustments = {
                'rules_score': 0.0,
                'nlp_score': 0.0,
                'anomaly_score': 0.0
            }
            
            self.save_data()
            logger.warning("All learning data has been reset")


# Global learning engine instance
learning_engine = LearningEngine()
