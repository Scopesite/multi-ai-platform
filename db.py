"""
Database setup for the AI Aggregation Platform.
This module initializes the SQLite database with required tables.
"""

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/usage.db')

def init_db():
    """
    Initialize the database with required tables.
    Creates the database directory if it doesn't exist.
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            tier TEXT DEFAULT 'free'
        )
        ''')
        
        # Create API keys table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            api_key_encrypted TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create usage table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            response_time REAL,
            status TEXT,
            tokens INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create billing table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            total_usage INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def check_usage(user_id):
    """
    Check the usage for a user in the current month.
    
    Args:
        user_id (int): The user ID to check
        
    Returns:
        int: The number of API calls made in the current month
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT COUNT(*) FROM usage 
        WHERE user_id = ? AND timestamp > datetime('now', '-1 month')
        """, (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
        
    except Exception as e:
        logger.error(f"Error checking usage: {str(e)}")
        return 0

def get_user_tier(user_id):
    """
    Get the subscription tier for a user.
    
    Args:
        user_id (int): The user ID to look up
        
    Returns:
        str: The user's subscription tier
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT tier FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return 'free'
            
    except Exception as e:
        logger.error(f"Error getting user tier: {str(e)}")
        return 'free'

def is_within_limits(user_id):
    """
    Check if a user is within their usage limits based on their tier.
    
    Args:
        user_id (int): The user ID to check
        
    Returns:
        bool: True if the user is within limits, False otherwise
    """
    tier = get_user_tier(user_id)
    usage_count = check_usage(user_id)
    
    if tier == 'free':
        return usage_count < 50
    elif tier == 'pro':
        return usage_count < 500
    elif tier == 'enterprise':
        return True  # Unlimited
    else:
        return usage_count < 10  # Default limit
