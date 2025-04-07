"""
Google AI provider integration for the AI Aggregation Platform.
This module handles communication with the Google AI API.
"""

import requests
import os
import logging
from datetime import datetime
import google.generativeai as genai

class GoogleAIProvider:
    """
    Provider class for Google AI API integration.
    Handles authentication, request formatting, and response parsing.
    """
    
    def __init__(self):
        """Initialize the Google AI provider with API credentials."""
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        genai.configure(api_key=self.api_key)
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging for the Google AI provider."""
        logging.basicConfig(
            filename='google_ai.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('google_ai_provider')
    
    def process(self, prompt, model='gemini-pro', max_tokens=1000):
        """
        Process a prompt using the Google AI API.
        
        Args:
            prompt (str): The prompt to send to the API
            model (str): The model to use (default: gemini-pro)
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            dict: The processed result or error information
        """
        try:
            self.logger.info(f"Processing prompt with model {model}")
            
            start_time = datetime.now()
            
            # Configure the model
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40
            }
            
            # Create the model
            model_instance = genai.GenerativeModel(model_name=model, 
                                                  generation_config=generation_config)
            
            # Generate content
            response = model_instance.generate_content(prompt)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Response received in {response_time} seconds")
            
            return {
                'text': response.text,
                'model': model,
                'provider': 'google',
                'response_time': response_time,
                'status': 'success'
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'error': f"Unexpected error: {str(e)}",
                'provider': 'google',
                'status': 'error'
            }
    
    def get_models(self):
        """
        Get a list of available models from Google AI.
        
        Returns:
            dict: List of available models or error information
        """
        try:
            # List available models
            models = [
                'gemini-pro',
                'gemini-pro-vision',
                'gemini-ultra'
            ]
            
            return {
                'models': models,
                'provider': 'google',
                'status': 'success'
            }
        
        except Exception as e:
            self.logger.error(f"Error getting models: {str(e)}")
            return {
                'error': f"Failed to get models: {str(e)}",
                'provider': 'google',
                'status': 'error'
            }
