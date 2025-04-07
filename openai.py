"""
Enhanced OpenAI provider integration for the AI Aggregation Platform.
This module handles communication with the OpenAI API with improved error handling and timeouts.
"""

import requests
import os
import logging
from datetime import datetime

class OpenAIProvider:
    """
    Provider class for OpenAI API integration.
    Handles authentication, request formatting, and response parsing.
    """
    
    def __init__(self):
        """Initialize the OpenAI provider with API credentials."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = 'https://api.openai.com/v1/chat/completions'
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging for the OpenAI provider."""
        logging.basicConfig(
            filename='openai.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('openai_provider')
    
    def process(self, prompt, model='gpt-3.5-turbo', max_tokens=1000, timeout=10):
        """
        Process a prompt using the OpenAI API.
        
        Args:
            prompt (str): The prompt to send to the API
            model (str): The model to use (default: gpt-3.5-turbo)
            max_tokens (int): Maximum number of tokens to generate
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The processed result or error information
        """
        try:
            self.logger.info(f"Processing prompt with model {model}")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
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
                'text': result['choices'][0]['message']['content'],
                'model': model,
                'provider': 'openai',
                'response_time': response_time,
                'status': 'success'
            }
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timed out after {timeout} seconds")
            return {
                'error': f"Request timed out after {timeout} seconds",
                'provider': 'openai',
                'status': 'error',
                'response_time': timeout
            }
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            return {
                'error': f"API request failed: {str(e)}",
                'provider': 'openai',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'error': f"Unexpected error: {str(e)}",
                'provider': 'openai',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    def process_web_design(self, prompt, model='gpt-3.5-turbo', max_tokens=1000, timeout=10):
        """
        Process a web design prompt using the OpenAI API.
        
        Args:
            prompt (str): The prompt to send to the API
            model (str): The model to use (default: gpt-3.5-turbo)
            max_tokens (int): Maximum number of tokens to generate
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The processed result or error information
        """
        enhanced_prompt = f"Generate {prompt} using Tailwind CSS and clean HTML. Provide well-structured, responsive code that works across devices."
        return self.process(enhanced_prompt, model, max_tokens, timeout)
    
    def get_models(self):
        """
        Get a list of available models from OpenAI.
        
        Returns:
            dict: List of available models or error information
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
            response.raise_for_status()
            
            models = response.json()['data']
            gpt_models = [model['id'] for model in models if 'gpt' in model['id']]
            
            return {
                'models': gpt_models,
                'provider': 'openai',
                'status': 'success'
            }
        
        except Exception as e:
            self.logger.error(f"Error getting models: {str(e)}")
            return {
                'error': f"Failed to get models: {str(e)}",
                'provider': 'openai',
                'status': 'error'
            }
