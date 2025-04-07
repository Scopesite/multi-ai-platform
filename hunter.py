"""
Hunter.io provider integration for the AI Aggregation Platform.
This module handles communication with the Hunter.io API for finding lead emails.
"""

import requests
import os
import logging
from datetime import datetime

class HunterProvider:
    """
    Provider class for Hunter.io API integration.
    Handles authentication, request formatting, and response parsing.
    """
    
    def __init__(self):
        """Initialize the Hunter provider with API credentials."""
        self.api_key = os.getenv('HUNTER_API_KEY')
        self.base_url = 'https://api.hunter.io/v2/email-finder'
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging for the Hunter provider."""
        logging.basicConfig(
            filename='hunter.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('hunter_provider')
    
    def find_email(self, domain, name, timeout=10):
        """
        Find an email address for a person at a specific domain.
        
        Args:
            domain (str): The domain to search for emails
            name (str): The full name of the person
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The email information or error details
        """
        try:
            self.logger.info(f"Finding email for {name} at {domain}")
            
            # Split the name into first and last name
            name_parts = name.split()
            if len(name_parts) < 2:
                return {
                    'error': "Please provide a full name (first and last name)",
                    'provider': 'hunter',
                    'status': 'error'
                }
            
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            params = {
                'domain': domain,
                'first_name': first_name,
                'last_name': last_name,
                'api_key': self.api_key
            }
            
            start_time = datetime.now()
            response = requests.get(self.base_url, params=params, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Response received in {response_time} seconds")
            
            response.raise_for_status()
            result = response.json()
            
            if 'data' in result and 'email' in result['data']:
                return {
                    'email': result['data']['email'],
                    'confidence': result['data'].get('confidence', 0),
                    'provider': 'hunter',
                    'response_time': response_time,
                    'status': 'success'
                }
            else:
                return {
                    'email': None,
                    'message': "No email found",
                    'provider': 'hunter',
                    'response_time': response_time,
                    'status': 'not_found'
                }
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timed out after {timeout} seconds")
            return {
                'error': f"Request timed out after {timeout} seconds",
                'provider': 'hunter',
                'status': 'error',
                'response_time': timeout
            }
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            return {
                'error': f"API request failed: {str(e)}",
                'provider': 'hunter',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'error': f"Unexpected error: {str(e)}",
                'provider': 'hunter',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    def domain_search(self, domain, limit=10, timeout=10):
        """
        Find email addresses for a specific domain.
        
        Args:
            domain (str): The domain to search for emails
            limit (int): Maximum number of results to return
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The email information or error details
        """
        try:
            self.logger.info(f"Searching emails for domain {domain}")
            
            params = {
                'domain': domain,
                'limit': limit,
                'api_key': self.api_key
            }
            
            start_time = datetime.now()
            response = requests.get('https://api.hunter.io/v2/domain-search', params=params, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Response received in {response_time} seconds")
            
            response.raise_for_status()
            result = response.json()
            
            if 'data' in result and 'emails' in result['data']:
                return {
                    'emails': result['data']['emails'],
                    'domain': domain,
                    'total': result['data'].get('total', 0),
                    'provider': 'hunter',
                    'response_time': response_time,
                    'status': 'success'
                }
            else:
                return {
                    'emails': [],
                    'message': "No emails found",
                    'provider': 'hunter',
                    'response_time': response_time,
                    'status': 'not_found'
                }
        
        except Exception as e:
            self.logger.error(f"Error in domain search: {str(e)}")
            return {
                'error': f"Error in domain search: {str(e)}",
                'provider': 'hunter',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
