"""
Enhanced usage tracking service for the AI Aggregation Platform.
This module handles tracking API usage for billing and analytics with improved functionality.
"""

import logging
from datetime import datetime
import sqlite3
import os
import stripe

logger = logging.getLogger(__name__)

# Database setup
from src.db import DB_PATH, get_user_tier

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_API_KEY')

def track_usage(user_id, provider, endpoint, response_time=None, status='success', tokens=None):
    """
    Track API usage for a user.
    
    Args:
        user_id (int): The user ID
        provider (str): The AI provider used
        endpoint (str): The API endpoint called
        response_time (float, optional): The response time in seconds
        status (str, optional): The status of the request
        tokens (int, optional): The number of tokens used
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert usage record
        cursor.execute('''
        INSERT INTO usage (user_id, provider, endpoint, timestamp, response_time, status, tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            provider,
            endpoint,
            datetime.now().isoformat(),
            response_time,
            status,
            tokens
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Tracked usage for user {user_id}: {provider}/{endpoint}")
    
    except Exception as e:
        logger.error(f"Error tracking usage: {str(e)}")

def get_user_usage(user_id, start_date=None, end_date=None):
    """
    Get usage statistics for a user.
    
    Args:
        user_id (int): The user ID
        start_date (str, optional): Start date for filtering (ISO format)
        end_date (str, optional): End date for filtering (ISO format)
        
    Returns:
        dict: Usage statistics
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = "SELECT provider, endpoint, COUNT(*) as count FROM usage WHERE user_id = ?"
        params = [user_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " GROUP BY provider, endpoint"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        usage_stats = {}
        for provider, endpoint, count in results:
            if provider not in usage_stats:
                usage_stats[provider] = {}
            
            usage_stats[provider][endpoint] = count
        
        conn.close()
        
        return usage_stats
    
    except Exception as e:
        logger.error(f"Error getting user usage: {str(e)}")
        return {}

def calculate_billing(user_id, month):
    """
    Calculate billing for a user for a specific month.
    
    Args:
        user_id (int): The user ID
        month (str): The month in YYYY-MM format
        
    Returns:
        dict: Billing information
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user's subscription tier
        tier = get_user_tier(user_id)
        
        # Get usage for the month
        start_date = f"{month}-01T00:00:00"
        if month.endswith('12'):
            next_year = str(int(month[:4]) + 1)
            end_date = f"{next_year}-01-01T00:00:00"
        else:
            next_month = str(int(month[-2:]) + 1).zfill(2)
            end_date = f"{month[:5]}{next_month}-01T00:00:00"
        
        cursor.execute('''
        SELECT COUNT(*) FROM usage 
        WHERE user_id = ? AND timestamp >= ? AND timestamp < ?
        ''', (user_id, start_date, end_date))
        
        total_usage = cursor.fetchone()[0]
        
        # Calculate amount based on tier and usage
        if tier == 'free':
            base_amount = 0
            included_calls = 50
            per_call_rate = 0.01
        elif tier == 'pro':
            base_amount = 25
            included_calls = 500
            per_call_rate = 0.005
        elif tier == 'enterprise':
            base_amount = 100
            included_calls = 5000
            per_call_rate = 0.002
        else:
            base_amount = 0
            included_calls = 0
            per_call_rate = 0.02
        
        # Calculate overage
        overage_calls = max(0, total_usage - included_calls)
        overage_amount = overage_calls * per_call_rate
        
        # Calculate total amount
        total_amount = base_amount + overage_amount
        
        # Insert billing record
        cursor.execute('''
        INSERT INTO billing (user_id, month, total_usage, amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            month,
            total_usage,
            total_amount,
            'pending',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'user_id': user_id,
            'month': month,
            'tier': tier,
            'total_usage': total_usage,
            'base_amount': base_amount,
            'overage_calls': overage_calls,
            'overage_amount': overage_amount,
            'total_amount': total_amount
        }
    
    except Exception as e:
        logger.error(f"Error calculating billing: {str(e)}")
        return {
            'error': f"Failed to calculate billing: {str(e)}"
        }

def bill_usage(user_id, month):
    """
    Bill a user for their usage in a specific month using Stripe.
    
    Args:
        user_id (int): The user ID
        month (str): The month in YYYY-MM format
        
    Returns:
        dict: Billing result
    """
    try:
        # Get billing information
        billing_info = calculate_billing(user_id, month)
        
        if 'error' in billing_info:
            return billing_info
        
        # Get customer ID from database (this is a placeholder)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT stripe_customer_id FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return {
                'error': "User does not have a Stripe customer ID"
            }
        
        customer_id = result[0]
        
        # Create a charge
        if billing_info['total_amount'] > 0:
            charge = stripe.Charge.create(
                amount=int(billing_info['total_amount'] * 100),  # Convert to cents
                currency='usd',
                customer=customer_id,
                description=f"AI Platform usage for {month}"
            )
            
            # Update billing status
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE billing SET status = ? WHERE user_id = ? AND month = ?",
                ('paid', user_id, month)
            )
            conn.commit()
            conn.close()
            
            return {
                'status': 'success',
                'charge_id': charge.id,
                'amount': billing_info['total_amount'],
                'month': month
            }
        else:
            return {
                'status': 'success',
                'message': "No charge needed (zero amount)",
                'amount': 0,
                'month': month
            }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return {
            'error': f"Payment processing error: {str(e)}"
        }
    
    except Exception as e:
        logger.error(f"Error billing usage: {str(e)}")
        return {
            'error': f"Failed to bill usage: {str(e)}"
        }

def check_usage_limits(user_id):
    """
    Check if a user has exceeded their usage limits.
    
    Args:
        user_id (int): The user ID
        
    Returns:
        bool: True if the user is within limits, False otherwise
    """
    try:
        # Get user's tier
        tier = get_user_tier(user_id)
        
        # Get current month's usage
        current_month = datetime.now().strftime('%Y-%m')
        start_date = f"{current_month}-01T00:00:00"
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM usage WHERE user_id = ? AND timestamp >= ?",
            (user_id, start_date)
        )
        usage_count = cursor.fetchone()[0]
        conn.close()
        
        # Check against tier limits
        if tier == 'free':
            return usage_count < 50
        elif tier == 'pro':
            return usage_count < 500
        elif tier == 'enterprise':
            return True  # Unlimited
        else:
            return usage_count < 10  # Default limit
    
    except Exception as e:
        logger.error(f"Error checking usage limits: {str(e)}")
        return False  # Fail closed
