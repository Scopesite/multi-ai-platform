"""
Rate limiting middleware for the AI Aggregation Platform.
This module handles rate limiting for API requests.
"""

from flask import request, jsonify
from functools import wraps
import time
import logging
from datetime import datetime

# Simple in-memory rate limiting
# In production, use Redis or another distributed cache
rate_limit_store = {}

logger = logging.getLogger(__name__)

def rate_limit(f):
    """
    Decorator to apply rate limiting to routes.
    
    Args:
        f (function): The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        user_id = current_user['id']
        
        # Get the user's subscription tier
        # This would normally come from a database
        tier = get_user_tier(user_id)
        
        # Set rate limits based on tier
        if tier == 'free':
            max_requests = 50
            time_window = 3600  # 1 hour in seconds
        elif tier == 'pro':
            max_requests = 500
            time_window = 3600
        elif tier == 'enterprise':
            max_requests = 5000
            time_window = 3600
        else:
            max_requests = 10
            time_window = 3600
        
        # Check if user is in rate limit store
        if user_id not in rate_limit_store:
            rate_limit_store[user_id] = {
                'requests': 0,
                'window_start': time.time()
            }
        
        # Check if time window has reset
        current_time = time.time()
        if current_time - rate_limit_store[user_id]['window_start'] > time_window:
            rate_limit_store[user_id] = {
                'requests': 0,
                'window_start': current_time
            }
        
        # Check if user has exceeded rate limit
        if rate_limit_store[user_id]['requests'] >= max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': f'You have exceeded the rate limit of {max_requests} requests per hour for your {tier} tier.'
            }), 429
        
        # Increment request count
        rate_limit_store[user_id]['requests'] += 1
        
        # Log rate limit usage
        logger.info(f"User {user_id} has used {rate_limit_store[user_id]['requests']}/{max_requests} requests")
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def get_user_tier(user_id):
    """
    Get the subscription tier for a user.
    
    Args:
        user_id (int): The user ID to look up
        
    Returns:
        str: The user's subscription tier
    """
    # This is a placeholder. In a real application, you would query the database.
    # For demonstration purposes, we'll return mock tiers.
    if user_id == 1:
        return 'free'
    elif user_id == 2:
        return 'admin'  # Admins bypass rate limiting
    elif user_id == 3:
        return 'pro'
    elif user_id == 4:
        return 'enterprise'
    else:
        return 'free'
