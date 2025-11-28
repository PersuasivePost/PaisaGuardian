"""
Local database for tracking payee history and detecting new payees
Uses SQLite for persistent storage
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import threading
import json

logger = logging.getLogger(__name__)


class PayeeDatabase:
    """
    Local database to track user transaction history with payees
    Helps detect new/unknown payees for fraud prevention
    """
    
    def __init__(self, db_path: str = "./learning_data/payee_history.db"):
        """
        Initialize payee database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self._lock = threading.Lock()
        self._init_database()
        logger.info(f"PayeeDatabase initialized at {self.db_path}")
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Payee history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payee_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    payee_upi TEXT NOT NULL,
                    payee_name TEXT,
                    first_transaction_date TEXT NOT NULL,
                    last_transaction_date TEXT NOT NULL,
                    transaction_count INTEGER DEFAULT 1,
                    total_amount REAL DEFAULT 0.0,
                    average_amount REAL DEFAULT 0.0,
                    max_amount REAL DEFAULT 0.0,
                    is_trusted BOOLEAN DEFAULT 0,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, payee_upi)
                )
            """)
            
            # Transaction log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    payee_upi TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_note TEXT,
                    risk_score REAL,
                    was_blocked BOOLEAN DEFAULT 0,
                    transaction_date TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_payee 
                ON payee_history(user_id, payee_upi)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transaction_user 
                ON transaction_log(user_id, transaction_date)
            """)
            
            conn.commit()
            conn.close()
    
    def is_new_payee(self, user_id: str, payee_upi: str) -> bool:
        """
        Check if this is a new payee for the user
        
        Args:
            user_id: User ID
            payee_upi: Payee UPI ID
            
        Returns:
            True if new payee, False if known
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM payee_history 
                WHERE user_id = ? AND payee_upi = ?
            """, (user_id, payee_upi))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is None
    
    def add_transaction(
        self,
        user_id: str,
        payee_upi: str,
        amount: float,
        payee_name: Optional[str] = None,
        transaction_note: Optional[str] = None,
        risk_score: Optional[float] = None,
        was_blocked: bool = False
    ) -> Dict[str, any]:
        """
        Record a transaction and update payee history
        
        Args:
            user_id: User ID
            payee_upi: Payee UPI ID
            amount: Transaction amount
            payee_name: Payee display name
            transaction_note: Transaction note
            risk_score: Risk score of the transaction
            was_blocked: Whether transaction was blocked
            
        Returns:
            Dictionary with transaction info and flags
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            result = {
                'is_new_payee': False,
                'transaction_count': 0,
                'average_amount': 0.0,
                'is_amount_anomaly': False
            }
            
            # Check if payee exists
            cursor.execute("""
                SELECT transaction_count, total_amount, average_amount, max_amount 
                FROM payee_history 
                WHERE user_id = ? AND payee_upi = ?
            """, (user_id, payee_upi))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing payee
                tx_count, total, avg, max_amt = existing
                new_tx_count = tx_count + 1
                new_total = total + amount
                new_avg = new_total / new_tx_count
                new_max = max(max_amt, amount)
                
                # Check for amount anomaly (3x average)
                if avg > 0 and amount > (avg * 3):
                    result['is_amount_anomaly'] = True
                
                cursor.execute("""
                    UPDATE payee_history 
                    SET transaction_count = ?,
                        total_amount = ?,
                        average_amount = ?,
                        max_amount = ?,
                        last_transaction_date = ?,
                        updated_at = ?
                    WHERE user_id = ? AND payee_upi = ?
                """, (new_tx_count, new_total, new_avg, new_max, now, now, user_id, payee_upi))
                
                result['transaction_count'] = new_tx_count
                result['average_amount'] = new_avg
                
            else:
                # New payee
                result['is_new_payee'] = True
                
                cursor.execute("""
                    INSERT INTO payee_history (
                        user_id, payee_upi, payee_name,
                        first_transaction_date, last_transaction_date,
                        transaction_count, total_amount, average_amount, max_amount,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                """, (user_id, payee_upi, payee_name, now, now, amount, amount, amount, now, now))
                
                result['transaction_count'] = 1
                result['average_amount'] = amount
            
            # Log transaction
            cursor.execute("""
                INSERT INTO transaction_log (
                    user_id, payee_upi, amount, transaction_note,
                    risk_score, was_blocked, transaction_date, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, payee_upi, amount, transaction_note, risk_score, was_blocked, now, now))
            
            conn.commit()
            conn.close()
            
            return result
    
    def get_payee_info(self, user_id: str, payee_upi: str) -> Optional[Dict]:
        """
        Get payee information
        
        Args:
            user_id: User ID
            payee_upi: Payee UPI ID
            
        Returns:
            Dictionary with payee info or None
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT payee_upi, payee_name, first_transaction_date,
                       last_transaction_date, transaction_count, total_amount,
                       average_amount, max_amount, is_trusted
                FROM payee_history 
                WHERE user_id = ? AND payee_upi = ?
            """, (user_id, payee_upi))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'payee_upi': row[0],
                    'payee_name': row[1],
                    'first_transaction_date': row[2],
                    'last_transaction_date': row[3],
                    'transaction_count': row[4],
                    'total_amount': row[5],
                    'average_amount': row[6],
                    'max_amount': row[7],
                    'is_trusted': bool(row[8])
                }
            return None
    
    def mark_as_trusted(self, user_id: str, payee_upi: str, trusted: bool = True):
        """
        Mark a payee as trusted or untrusted
        
        Args:
            user_id: User ID
            payee_upi: Payee UPI ID
            trusted: Whether to mark as trusted
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            cursor.execute("""
                UPDATE payee_history 
                SET is_trusted = ?, updated_at = ?
                WHERE user_id = ? AND payee_upi = ?
            """, (1 if trusted else 0, now, user_id, payee_upi))
            
            conn.commit()
            conn.close()
    
    def get_transaction_history(
        self,
        user_id: str,
        payee_upi: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get transaction history
        
        Args:
            user_id: User ID
            payee_upi: Optional payee UPI to filter
            limit: Maximum number of transactions
            
        Returns:
            List of transaction dictionaries
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if payee_upi:
                cursor.execute("""
                    SELECT payee_upi, amount, transaction_note, risk_score,
                           was_blocked, transaction_date
                    FROM transaction_log 
                    WHERE user_id = ? AND payee_upi = ?
                    ORDER BY transaction_date DESC
                    LIMIT ?
                """, (user_id, payee_upi, limit))
            else:
                cursor.execute("""
                    SELECT payee_upi, amount, transaction_note, risk_score,
                           was_blocked, transaction_date
                    FROM transaction_log 
                    WHERE user_id = ?
                    ORDER BY transaction_date DESC
                    LIMIT ?
                """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'payee_upi': row[0],
                    'amount': row[1],
                    'transaction_note': row[2],
                    'risk_score': row[3],
                    'was_blocked': bool(row[4]),
                    'transaction_date': row[5]
                }
                for row in rows
            ]
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """
        Get user's transaction statistics
        
        Args:
            user_id: User ID
            
        Returns:
            Statistics dictionary
        """
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Total payees
            cursor.execute("""
                SELECT COUNT(*) FROM payee_history WHERE user_id = ?
            """, (user_id,))
            total_payees = cursor.fetchone()[0]
            
            # Trusted payees
            cursor.execute("""
                SELECT COUNT(*) FROM payee_history WHERE user_id = ? AND is_trusted = 1
            """, (user_id,))
            trusted_payees = cursor.fetchone()[0]
            
            # Total transactions
            cursor.execute("""
                SELECT COUNT(*), SUM(amount), AVG(amount)
                FROM transaction_log WHERE user_id = ?
            """, (user_id,))
            tx_stats = cursor.fetchone()
            total_transactions = tx_stats[0] or 0
            total_amount = tx_stats[1] or 0.0
            avg_amount = tx_stats[2] or 0.0
            
            # Blocked transactions
            cursor.execute("""
                SELECT COUNT(*) FROM transaction_log WHERE user_id = ? AND was_blocked = 1
            """, (user_id,))
            blocked_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_payees': total_payees,
                'trusted_payees': trusted_payees,
                'total_transactions': total_transactions,
                'total_amount': total_amount,
                'average_amount': avg_amount,
                'blocked_transactions': blocked_count
            }


# Global instance
payee_db = PayeeDatabase()
