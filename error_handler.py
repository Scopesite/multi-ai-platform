"""
Error handling middleware for the AI Aggregation Platform.
This module provides centralized error handling for the application.
"""

from flask import jsonify
import logging
import traceback
import requests

logger = logging.getLogger(__name__)

def handle_error(error):
    """
    Handle different types of errors and return appropriate responses.
    
    Args:
        error (Exception): The error to handle
        
    Returns:
        tuple: A Flask response tuple (response, status_code)
    """
    if isinstance(error, requests.exceptions.RequestException):
        # Handle API request errors
        logger.error(f"API request error: {str(error)}")
        return jsonify({
            'error': 'API request failed',
            'message': str(error),
            'status': 'error'
        }), 502
    
    elif isinstance(error, requests.exceptions.Timeout):
        # Handle timeout errors
        logger.error(f"API timeout error: {str(error)}")
        return jsonify({
            'error': 'API request timed out',
            'message': 'The request to the AI provider timed out. Please try again later.',
            'status': 'error'
        }), 504
    
    elif isinstance(error, ValueError):
        # Handle validation errors
        logger.error(f"Validation error: {str(error)}")
        return jsonify({
            'error': 'Validation error',
            'message': str(error),
            'status': 'error'
        }), 400
    
    elif isinstance(error, KeyError):
        # Handle missing key errors
        logger.error(f"Key error: {str(error)}")
        return jsonify({
            'error': 'Missing required field',
            'message': f"Missing required field: {str(error)}",
            'status': 'error'
        }), 400
    
    else:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(error)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.',
            'status': 'error'
        }), 500

class CircuitBreaker:
    """
    Circuit breaker pattern implementation to prevent cascading failures.
    """
    
    def __init__(self, name, failure_threshold=5, reset_timeout=60):
        """
        Initialize the circuit breaker.
        
        Args:
            name (str): Name of the service being protected
            failure_threshold (int): Number of failures before opening the circuit
            reset_timeout (int): Time in seconds before attempting to close the circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.state = 'closed'  # closed, open, half-open
        self.last_failure_time = 0
    
    def execute(self, func, *args, **kwargs):
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func (function): The function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function or an error
        """
        if self.state == 'open':
            # Check if it's time to try again
            if time.time() - self.last_failure_time > self.reset_timeout:
                logger.info(f"Circuit {self.name} transitioning from open to half-open")
                self.state = 'half-open'
            else:
                logger.warning(f"Circuit {self.name} is open, fast-failing")
                return {
                    'error': 'Service unavailable',
                    'message': f'The {self.name} service is currently unavailable. Please try again later.',
                    'status': 'error'
                }
        
        try:
            result = func(*args, **kwargs)
            
            # If we're in half-open and the call succeeded, close the circuit
            if self.state == 'half-open':
                logger.info(f"Circuit {self.name} transitioning from half-open to closed")
                self.state = 'closed'
                self.failures = 0
            
            return result
        
        except Exception as e:
            # Record the failure
            self.failures += 1
            self.last_failure_time = time.time()
            
            # If we've hit the threshold, open the circuit
            if self.failures >= self.failure_threshold:
                logger.warning(f"Circuit {self.name} transitioning to open after {self.failures} failures")
                self.state = 'open'
            
            # Re-raise the exception
            raise e
