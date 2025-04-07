"""
Enhanced authentication middleware for the AI Aggregation Platform.
This module handles user authentication and authorization with improved security and error handling.
"""

from flask import request, jsonify
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def generate_token(user_id):
    """
    Generate a JWT token for a user.
    
    Args:
        user_id (int): The user ID to encode in the token
        
    Returns:
        str: The generated JWT token
    """
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            os.getenv('SECRET_KEY', 'dev_secret_key'),
            algorithm='HS256'
        )
        
        logger.info(f"Generated token for user {user_id}")
        return token
    
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise

def token_required(f):
    """
    Decorator to protect routes with JWT authentication.
    
    Args:
        f (function): The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # Check if token is in cookies
        if not token and 'token' in request.cookies:
            token = request.cookies['token']
        
        if not token:
            logger.warning("Token missing in request")
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode the token
            payload = jwt.decode(
                token,
                os.getenv('SECRET_KEY', 'dev_secret_key'),
                algorithms=['HS256']
            )
            
            # Get the user from the database
            current_user = get_current_user(payload['user_id'])
            
            if not current_user:
                logger.warning(f"User not found for ID {payload['user_id']}")
                return jsonify({'message': 'User not found'}), 401
            
            logger.info(f"Authenticated user {current_user['id']}")
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Unexpected error in token validation: {str(e)}")
            return jsonify({'message': 'Authentication error'}), 500
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def get_current_user(user_id):
    """
    Get the current user from the database.
    
    Args:
        user_id (int): The user ID to look up
        
    Returns:
        dict: The user data or None if not found
    """
    # This is a placeholder. In a real application, you would query the database.
    # For demonstration purposes, we'll return a mock user.
    if user_id == 1:
        return {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'user',
            'tier': 'free'
        }
    elif user_id == 2:
        return {
            'id': 2,
            'username': 'admin',
            'email': 'admin@example.com',
            'role': 'admin',
            'tier': 'enterprise'
        }
    elif user_id == 3:
        return {
            'id': 3,
            'username': 'prouser',
            'email': 'pro@example.com',
            'role': 'user',
            'tier': 'pro'
        }
    else:
        return None

def admin_required(f):
    """
    Decorator to restrict routes to admin users.
    
    Args:
        f (function): The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'admin':
            logger.warning(f"User {current_user['id']} attempted to access admin-only route")
            return jsonify({'message': 'Admin privileges required'}), 403
        
        logger.info(f"Admin access granted for user {current_user['id']}")
        return f(current_user, *args, **kwargs)
    
    return decorated

def tier_required(required_tier):
    """
    Decorator to restrict routes based on subscription tier.
    
    Args:
        required_tier (str): The minimum tier required ('free', 'pro', 'enterprise')
        
    Returns:
        function: The decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            tier_levels = {
                'free': 0,
                'pro': 1,
                'enterprise': 2
            }
            
            user_tier = current_user.get('tier', 'free')
            
            if tier_levels.get(user_tier, 0) < tier_levels.get(required_tier, 0):
                logger.warning(f"User {current_user['id']} with tier {user_tier} attempted to access {required_tier} route")
                return jsonify({
                    'message': f'This feature requires {required_tier} tier or higher',
                    'current_tier': user_tier,
                    'required_tier': required_tier
                }), 403
            
            logger.info(f"Tier access granted for user {current_user['id']} ({user_tier} >= {required_tier})")
            return f(current_user, *args, **kwargs)
        
        return decorated
    
    return decorator
