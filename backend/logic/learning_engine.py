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
        
        # Fraud reports tracking
        # Key: entity_id, Value: List of report dictionaries
        self.fraud_reports: Dict[str, List[Dict]] = {}
        
        # Blacklist threshold for automatic blacklisting
        self.fraud_report_threshold = 50
        
        # Analysis history tracking
        self.analysis_history: List[Dict] = []
        
        # User settings storage
        self.user_settings: Dict[str, Dict] = {}
        
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
        
        # Fraud report metrics
        if hasattr(self, 'fraud_reports'):
            metrics['total_fraud_reports'] = sum(len(reports) for reports in self.fraud_reports.values())
            metrics['unique_reported_entities'] = len(self.fraud_reports)
        
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
    
    def report_fraud(
        self,
        entity_id: str,
        entity_type: str,
        user_id: str,
        description: Optional[str] = None,
        fraud_category: Optional[str] = None,
        amount_lost: Optional[float] = None,
        additional_info: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Report a fraud incident by a user
        Automatically blacklists entity if reports reach threshold
        
        Args:
            entity_id: The fraudulent entity (phone number, UPI ID, URL, etc.)
            entity_type: Type of entity (phone_numbers, upi_ids, urls, senders, domains)
            user_id: User reporting the fraud
            description: Description of the fraud incident
            fraud_category: Category of fraud (phishing, scam, etc.)
            amount_lost: Amount lost in fraud (if applicable)
            additional_info: Any additional information
            
        Returns:
            Dictionary with report results including blacklist status
        """
        with self._lock:
            # Create fraud report entry
            report = {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'user_id': user_id,
                'description': description,
                'fraud_category': fraud_category,
                'amount_lost': amount_lost,
                'additional_info': additional_info or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Initialize reports list for this entity if not exists
            if entity_id not in self.fraud_reports:
                self.fraud_reports[entity_id] = []
            
            # Add report
            self.fraud_reports[entity_id].append(report)
            report_count = len(self.fraud_reports[entity_id])
            
            result = {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'report_count': report_count,
                'threshold': self.fraud_report_threshold,
                'blacklisted': False,
                'message': f'Fraud report submitted successfully. Total reports for this entity: {report_count}'
            }
            
            # Check if threshold reached for automatic blacklisting
            if report_count >= self.fraud_report_threshold:
                # Add to blacklist if not already present
                if entity_type in self.blacklist:
                    if entity_id not in self.blacklist[entity_type]:
                        self.blacklist[entity_type].add(entity_id)
                        result['blacklisted'] = True
                        result['message'] = (
                            f'⚠️ ALERT: Entity automatically blacklisted after {report_count} fraud reports. '
                            f'This {entity_type} will now be blocked for all users.'
                        )
                        logger.warning(
                            f"Automatic blacklist: {entity_type}:{entity_id} after {report_count} reports"
                        )
                    else:
                        result['blacklisted'] = True
                        result['message'] = (
                            f'Entity already blacklisted. Total reports: {report_count}'
                        )
                else:
                    logger.warning(f"Unknown entity type for blacklist: {entity_type}")
            
            # Save data periodically
            if len(self.fraud_reports) % 10 == 0:
                self.save_data()
            
            logger.info(
                f"Fraud report submitted by {user_id} for {entity_type}:{entity_id}. "
                f"Total reports: {report_count}"
            )
            
            return result
    
    def get_fraud_reports(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get fraud reports with optional filters
        
        Args:
            entity_id: Filter by specific entity
            entity_type: Filter by entity type
            limit: Maximum number of reports to return
            
        Returns:
            List of fraud reports
        """
        all_reports = []
        
        for eid, reports in self.fraud_reports.items():
            for report in reports:
                # Apply filters
                if entity_id and report['entity_id'] != entity_id:
                    continue
                if entity_type and report['entity_type'] != entity_type:
                    continue
                
                # Add report count for this entity
                report_with_count = report.copy()
                report_with_count['total_reports_for_entity'] = len(self.fraud_reports[eid])
                all_reports.append(report_with_count)
        
        # Sort by timestamp (newest first)
        all_reports.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_reports[:limit]
    
    def add_analysis_history(
        self,
        analysis_id: str,
        analysis_type: str,
        entity: str,
        risk_level: str,
        risk_score: float,
        is_safe: bool,
        fraud_indicators: List[str],
        user_id: str
    ) -> None:
        """
        Add an analysis to history
        
        Args:
            analysis_id: Unique identifier for this analysis
            analysis_type: Type of analysis (url, sms, transaction, qr_code)
            entity: Entity analyzed (URL, phone, UPI ID)
            risk_level: Risk level (low, medium, high, critical)
            risk_score: Risk score (0-100)
            is_safe: Whether entity is safe
            fraud_indicators: List of fraud indicators found
            user_id: User who performed the analysis
        """
        with self._lock:
            entry = {
                'id': analysis_id,
                'analysis_type': analysis_type,
                'entity': entity,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'is_safe': is_safe,
                'fraud_indicators': fraud_indicators,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'user_action': None
            }
            self.analysis_history.append(entry)
            
            # Keep only last 1000 analyses per user to prevent unlimited growth
            user_analyses = [a for a in self.analysis_history if a['user_id'] == user_id]
            if len(user_analyses) > 1000:
                # Remove oldest analyses for this user
                oldest_user_analysis = min(
                    (a for a in self.analysis_history if a['user_id'] == user_id),
                    key=lambda x: x['timestamp']
                )
                self.analysis_history.remove(oldest_user_analysis)
            
            # Save periodically
            if len(self.analysis_history) % 50 == 0:
                self.save_data()
    
    def get_analysis_history(
        self,
        user_id: str,
        analysis_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get analysis history for a user
        
        Args:
            user_id: User ID to filter by
            analysis_type: Optional filter by type
            risk_level: Optional filter by risk level
            limit: Maximum results to return
            
        Returns:
            List of analysis history entries
        """
        history = [a for a in self.analysis_history if a['user_id'] == user_id]
        
        # Apply filters
        if analysis_type:
            history = [h for h in history if h['analysis_type'] == analysis_type]
        if risk_level:
            history = [h for h in history if h['risk_level'] == risk_level]
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return history[:limit]
    
    def get_dashboard_stats(self, user_id: str) -> Dict[str, any]:
        """
        Get dashboard statistics for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with dashboard statistics
        """
        user_analyses = [a for a in self.analysis_history if a['user_id'] == user_id]
        
        # Calculate today's analyses
        today = datetime.utcnow().date()
        analyses_today = sum(
            1 for a in user_analyses
            if datetime.fromisoformat(a['timestamp']).date() == today
        )
        
        # Risk distribution
        risk_dist = defaultdict(int)
        for a in user_analyses:
            risk_dist[a['risk_level']] += 1
        
        # Analysis by type
        type_dist = defaultdict(int)
        for a in user_analyses:
            type_dist[a['analysis_type']] += 1
        
        # Recent high-risk alerts
        recent_alerts = [
            a for a in user_analyses
            if a['risk_level'] in ['high', 'critical']
        ][:5]
        
        # Blocked threats (high/critical that were not marked safe by user)
        blocked = sum(
            1 for a in user_analyses
            if a['risk_level'] in ['high', 'critical'] and not a['is_safe']
        )
        
        # Protection rate
        total_threats = sum(
            1 for a in user_analyses
            if a['risk_level'] in ['medium', 'high', 'critical']
        )
        protection_rate = (blocked / total_threats * 100) if total_threats > 0 else 100.0
        
        return {
            'total_analyses': len(user_analyses),
            'analyses_today': analyses_today,
            'blocked_threats': blocked,
            'active_alerts': len(recent_alerts),
            'risk_distribution': dict(risk_dist),
            'analysis_by_type': dict(type_dist),
            'recent_alerts': recent_alerts,
            'protection_rate': protection_rate
        }
    
    def get_user_settings(self, user_id: str) -> Dict[str, any]:
        """
        Get user settings
        
        Args:
            user_id: User ID
            
        Returns:
            User settings dictionary or default settings
        """
        return self.user_settings.get(user_id, {
            'risk_thresholds': {
                'low': 40.0,
                'medium': 70.0,
                'high': 100.0
            },
            'features': {
                'url_analysis': True,
                'sms_analysis': True,
                'transaction_analysis': True,
                'qr_code_scanning': True,
                'auto_blocking': True,
                'learning_mode': True,
                'notifications': True
            },
            'notification_preferences': {
                'email_alerts': True,
                'push_notifications': True,
                'sms_alerts': False
            },
            'auto_submit_feedback': False
        })
    
    def update_user_settings(self, user_id: str, settings: Dict[str, any]) -> None:
        """
        Update user settings
        
        Args:
            user_id: User ID
            settings: New settings to merge
        """
        with self._lock:
            if user_id not in self.user_settings:
                self.user_settings[user_id] = self.get_user_settings(user_id)
            
            # Deep merge settings
            for key, value in settings.items():
                if isinstance(value, dict) and key in self.user_settings[user_id]:
                    self.user_settings[user_id][key].update(value)
                else:
                    self.user_settings[user_id][key] = value
            
            self.save_data()
    
    def get_report_statistics(self) -> Dict[str, any]:
        """
        Get statistics about fraud reports
        
        Returns:
            Dictionary with fraud report statistics
        """
        stats = {
            'total_unique_entities_reported': len(self.fraud_reports),
            'total_reports': sum(len(reports) for reports in self.fraud_reports.values()),
            'entities_by_report_count': defaultdict(int),
            'reports_by_entity_type': defaultdict(int),
            'reports_by_category': defaultdict(int),
            'total_amount_lost': 0.0,
            'entities_reaching_threshold': 0,
            'auto_blacklisted_entities': []
        }
        
        for entity_id, reports in self.fraud_reports.items():
            report_count = len(reports)
            
            # Count by report count ranges
            if report_count >= self.fraud_report_threshold:
                stats['entities_by_report_count']['50+'] += 1
                stats['entities_reaching_threshold'] += 1
                stats['auto_blacklisted_entities'].append({
                    'entity_id': entity_id,
                    'report_count': report_count
                })
            elif report_count >= 20:
                stats['entities_by_report_count']['20-49'] += 1
            elif report_count >= 10:
                stats['entities_by_report_count']['10-19'] += 1
            elif report_count >= 5:
                stats['entities_by_report_count']['5-9'] += 1
            else:
                stats['entities_by_report_count']['1-4'] += 1
            
            # Analyze each report
            for report in reports:
                # Count by entity type
                entity_type = report.get('entity_type', 'unknown')
                stats['reports_by_entity_type'][entity_type] += 1
                
                # Count by fraud category
                category = report.get('fraud_category', 'uncategorized')
                stats['reports_by_category'][category] += 1
                
                # Sum amount lost
                if report.get('amount_lost'):
                    stats['total_amount_lost'] += report['amount_lost']
        
        # Convert defaultdicts to regular dicts for JSON serialization
        stats['entities_by_report_count'] = dict(stats['entities_by_report_count'])
        stats['reports_by_entity_type'] = dict(stats['reports_by_entity_type'])
        stats['reports_by_category'] = dict(stats['reports_by_category'])
        
        return stats
    
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
            
            # Save fraud reports
            reports_file = self.data_dir / 'fraud_reports.json'
            with open(reports_file, 'w') as f:
                json.dump(self.fraud_reports, f, indent=2)
            
            # Save analysis history
            history_file_analysis = self.data_dir / 'analysis_history.json'
            with open(history_file_analysis, 'w') as f:
                json.dump(self.analysis_history, f, indent=2)
            
            # Save user settings
            settings_file = self.data_dir / 'user_settings.json'
            with open(settings_file, 'w') as f:
                json.dump(self.user_settings, f, indent=2)
            
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
            
            # Load fraud reports
            reports_file = self.data_dir / 'fraud_reports.json'
            if reports_file.exists():
                with open(reports_file, 'r') as f:
                    self.fraud_reports = json.load(f)
            
            # Load analysis history
            history_file_analysis = self.data_dir / 'analysis_history.json'
            if history_file_analysis.exists():
                with open(history_file_analysis, 'r') as f:
                    self.analysis_history = json.load(f)
            
            # Load user settings
            settings_file = self.data_dir / 'user_settings.json'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    self.user_settings = json.load(f)
            
            logger.info(
                f"Learning data loaded: "
                f"{sum(len(v) for v in self.whitelist.values())} whitelisted, "
                f"{sum(len(v) for v in self.blacklist.values())} blacklisted, "
                f"{len(self.feedback_history)} feedbacks, "
                f"{sum(len(reports) for reports in self.fraud_reports.values())} fraud reports, "
                f"{len(self.analysis_history)} analyses, "
                f"{len(self.user_settings)} user settings"
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
            
            self.fraud_reports.clear()
            
            self.save_data()
            logger.warning("All learning data has been reset")


# Global learning engine instance
learning_engine = LearningEngine()
