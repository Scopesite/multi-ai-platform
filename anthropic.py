"""
Enhanced Anthropic provider integration for the AI Aggregation Platform.
This module handles communication with the Anthropic API with improved error handling and timeouts.
"""

import requests
import os
import logging
from datetime import datetime

class AnthropicProvider:
    """
    Provider class for Anthropic API integration.
    Handles authentication, request formatting, and response parsing.
    """
    
    def __init__(self):
        """Initialize the Anthropic provider with API credentials."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.base_url = 'https://api.anthropic.com/v1/messages'
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging for the Anthropic provider."""
        logging.basicConfig(
            filename='anthropic.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('anthropic_provider')
    
    def process(self, prompt, model='claude-3-sonnet-20240229', max_tokens=1000, timeout=10):
        """
        Process a prompt using the Anthropic API.
        
        Args:
            prompt (str): The prompt to send to the API
            model (str): The model to use (default: claude-3-sonnet-20240229)
            max_tokens (int): Maximum number of tokens to generate
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The processed result or error information
        """
        try:
            self.logger.info(f"Processing prompt with model {model}")
            
            headers = {
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_tokens
            }
            
            start_time = datetime.now()
            response = requests.post(self.base_url, json=data, headers=headers, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Response received in {response_time} seconds")
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'text': result['content'][0]['text'],
                'model': model,
                'provider': 'anthropic',
                'response_time': response_time,
                'status': 'success'
            }
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timed out after {timeout} seconds")
            return {
                'error': f"Request timed out after {timeout} seconds",
                'provider': 'anthropic',
                'status': 'error',
                'response_time': timeout
            }
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            return {
                'error': f"API request failed: {str(e)}",
                'provider': 'anthropic',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'error': f"Unexpected error: {str(e)}",
                'provider': 'anthropic',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    def process_sales(self, prompt, model='claude-3-sonnet-20240229', max_tokens=1000, timeout=10):
        """
        Process a sales-related prompt using the Anthropic API.
        
        Args:
            prompt (str): The prompt to send to the API
            model (str): The model to use (default: claude-3-sonnet-20240229)
            max_tokens (int): Maximum number of tokens to generate
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The processed result or error information
        """
        enhanced_prompt = f"Write a professional, friendly {prompt} for sales outreach. Make it persuasive but not pushy, personalized, and with a clear call to action."
        return self.process(enhanced_prompt, model, max_tokens, timeout)
    
    def get_models(self):
        """
        Get a list of available models from Anthropic.
        
        Returns:
            dict: List of available models or error information
        """
        # Anthropic doesn't have a models endpoint, so we return a static list
        models = [
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307',
            'claude-2.1',
            'claude-2.0',
            'claude-instant-1.2'
        ]
        
        return {
            'models': models,
            'provider': 'anthropic',
            'status': 'success'
        }
