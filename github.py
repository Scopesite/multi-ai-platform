"""
GitHub API integration for the AI Aggregation Platform.
This module handles communication with the GitHub API for code management.
"""

import requests
import os
import base64
import logging
from datetime import datetime

class GitHubProvider:
    """
    Provider class for GitHub API integration.
    Handles authentication, request formatting, and response parsing.
    """
    
    def __init__(self):
        """Initialize the GitHub provider with API credentials."""
        self.api_key = os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging for the GitHub provider."""
        logging.basicConfig(
            filename='github.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('github_provider')
    
    def push_to_github(self, content, repo, path, message="Add AI-generated code", timeout=10):
        """
        Push content to a GitHub repository.
        
        Args:
            content (str): The content to push
            repo (str): The repository in format 'username/repo'
            path (str): The file path in the repository
            message (str): The commit message
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The response information or error details
        """
        try:
            self.logger.info(f"Pushing content to {repo}/{path}")
            
            url = f"{self.base_url}/repos/{repo}/contents/{path}"
            headers = {
                'Authorization': f'token {self.api_key}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Check if file already exists
            start_time = datetime.now()
            response = requests.get(url, headers=headers, timeout=timeout)
            
            data = {
                'message': message,
                'content': base64.b64encode(content.encode()).decode()
            }
            
            # If file exists, we need to include the sha
            if response.status_code == 200:
                data['sha'] = response.json()['sha']
                self.logger.info(f"File {path} already exists, updating")
            else:
                self.logger.info(f"Creating new file {path}")
            
            # Push the content
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Response received in {response_time} seconds")
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'content_url': result.get('content', {}).get('html_url', ''),
                'commit_url': result.get('commit', {}).get('html_url', ''),
                'provider': 'github',
                'response_time': response_time,
                'status': 'success'
            }
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timed out after {timeout} seconds")
            return {
                'error': f"Request timed out after {timeout} seconds",
                'provider': 'github',
                'status': 'error',
                'response_time': timeout
            }
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            return {
                'error': f"API request failed: {str(e)}",
                'provider': 'github',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'error': f"Unexpected error: {str(e)}",
                'provider': 'github',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    def get_repository_contents(self, repo, path="", timeout=10):
        """
        Get contents of a GitHub repository.
        
        Args:
            repo (str): The repository in format 'username/repo'
            path (str): The directory path in the repository
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: The repository contents or error details
        """
        try:
            self.logger.info(f"Getting contents of {repo}/{path}")
            
            url = f"{self.base_url}/repos/{repo}/contents/{path}"
            headers = {
                'Authorization': f'token {self.api_key}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            start_time = datetime.now()
            response = requests.get(url, headers=headers, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Response received in {response_time} seconds")
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'contents': result,
                'provider': 'github',
                'response_time': response_time,
                'status': 'success'
            }
        
        except Exception as e:
            self.logger.error(f"Error getting repository contents: {str(e)}")
            return {
                'error': f"Error getting repository contents: {str(e)}",
                'provider': 'github',
                'status': 'error',
                'response_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
