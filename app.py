"""
Enhanced main application file for the AI Aggregation Platform.
This file initializes the Flask application and sets up routes with improved error handling and provider integration.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from dotenv import load_dotenv
import os
import logging
import json
from datetime import datetime

# Import provider modules
from api.providers.openai import OpenAIProvider
from api.providers.anthropic import AnthropicProvider
from api.providers.google import GoogleAIProvider
from api.providers.hunter import HunterProvider
from api.providers.github import GitHubProvider

# Import middleware
from api.middleware.auth import token_required, generate_token, admin_required, tier_required
from api.middleware.rate_limiter import rate_limit
from api.middleware.error_handler import handle_error, CircuitBreaker

# Import services
from services.usage_tracker import track_usage, get_user_usage, calculate_billing, bill_usage, check_usage_limits

# Import database
from db import init_db, get_user_tier

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['DEBUG'] = os.getenv('FLASK_ENV', 'development') == 'development'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Initialize providers
openai_provider = OpenAIProvider()
anthropic_provider = AnthropicProvider()
google_provider = GoogleAIProvider()
hunter_provider = HunterProvider()
github_provider = GitHubProvider()

# Provider mapping
PROVIDERS = {
    'openai': openai_provider,
    'anthropic': anthropic_provider,
    'google': google_provider,
    'hunter': hunter_provider,
    'github': github_provider
}

# Circuit breakers for each provider
circuit_breakers = {
    'openai': CircuitBreaker('openai'),
    'anthropic': CircuitBreaker('anthropic'),
    'google': CircuitBreaker('google'),
    'hunter': CircuitBreaker('hunter'),
    'github': CircuitBreaker('github')
}

# Routes
@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    """Render the user dashboard."""
    return render_template('dashboard.html', user=current_user)

@app.route('/api/process', methods=['POST'])
@token_required
@rate_limit
def process_prompt(current_user):
    """Process a prompt using the selected AI provider."""
    try:
        # Check if user is within usage limits
        if not check_usage_limits(current_user['id']):
            return jsonify({
                "error": "Usage limit exceeded",
                "message": "You have exceeded your usage limit for this month. Please upgrade your plan or wait until next month."
            }), 429
        
        data = request.json
        prompt = data.get('prompt')
        provider_name = data.get('provider', 'openai')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        if provider_name not in PROVIDERS:
            return jsonify({"error": f"Provider '{provider_name}' not supported"}), 400
        
        # Get the provider and circuit breaker
        provider = PROVIDERS[provider_name]
        circuit_breaker = circuit_breakers[provider_name]
        
        # Process the prompt with circuit breaker
        try:
            result = circuit_breaker.execute(lambda: provider.process(prompt))
        except Exception as e:
            # If primary provider fails, try fallback (OpenAI)
            if provider_name != 'openai':
                logger.warning(f"{provider_name} failed, falling back to OpenAI")
                result = circuit_breakers['openai'].execute(lambda: openai_provider.process(prompt))
            else:
                raise e
        
        # Track usage
        track_usage(
            current_user['id'], 
            provider_name, 
            'process', 
            result.get('response_time', 0),
            result.get('status', 'error')
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        return handle_error(e)

@app.route('/api/web-design', methods=['POST'])
@token_required
@tier_required('pro')
@rate_limit
def web_design(current_user):
    """Process a web design prompt using OpenAI."""
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Process with OpenAI's web design method
        result = openai_provider.process_web_design(prompt)
        
        # Track usage
        track_usage(
            current_user['id'], 
            'openai', 
            'web-design', 
            result.get('response_time', 0),
            result.get('status', 'error')
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing web design prompt: {str(e)}")
        return handle_error(e)

@app.route('/api/sales', methods=['POST'])
@token_required
@tier_required('pro')
@rate_limit
def sales(current_user):
    """Process a sales prompt using Anthropic."""
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Process with Anthropic's sales method
        result = anthropic_provider.process_sales(prompt)
        
        # Track usage
        track_usage(
            current_user['id'], 
            'anthropic', 
            'sales', 
            result.get('response_time', 0),
            result.get('status', 'error')
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing sales prompt: {str(e)}")
        return handle_error(e)

@app.route('/api/find-email', methods=['POST'])
@token_required
@tier_required('pro')
@rate_limit
def find_email(current_user):
    """Find an email using Hunter.io."""
    try:
        data = request.json
        domain = data.get('domain')
        name = data.get('name')
        
        if not domain or not name:
            return jsonify({"error": "Domain and name are required"}), 400
        
        # Find email with Hunter
        result = hunter_provider.find_email(domain, name)
        
        # Track usage
        track_usage(
            current_user['id'], 
            'hunter', 
            'find-email', 
            result.get('response_time', 0),
            result.get('status', 'error')
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error finding email: {str(e)}")
        return handle_error(e)

@app.route('/api/push-to-github', methods=['POST'])
@token_required
@tier_required('pro')
@rate_limit
def push_to_github(current_user):
    """Push content to GitHub."""
    try:
        data = request.json
        content = data.get('content')
        repo = data.get('repo')
        path = data.get('path')
        message = data.get('message', 'Add AI-generated code')
        
        if not content or not repo or not path:
            return jsonify({"error": "Content, repo, and path are required"}), 400
        
        # Push to GitHub
        result = github_provider.push_to_github(content, repo, path, message)
        
        # Track usage
        track_usage(
            current_user['id'], 
            'github', 
            'push-to-github', 
            result.get('response_time', 0),
            result.get('status', 'error')
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error pushing to GitHub: {str(e)}")
        return handle_error(e)

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get a list of available providers."""
    providers = list(PROVIDERS.keys())
    return jsonify({"providers": providers})

@app.route('/api/usage', methods=['GET'])
@token_required
def get_usage(current_user):
    """Get usage statistics for the current user."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        usage = get_user_usage(current_user['id'], start_date, end_date)
        return jsonify({"usage": usage})
    
    except Exception as e:
        logger.error(f"Error getting usage: {str(e)}")
        return handle_error(e)

@app.route('/api/billing', methods=['GET'])
@token_required
def get_billing(current_user):
    """Get billing information for the current user."""
    try:
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))
        
        billing = calculate_billing(current_user['id'], month)
        return jsonify(billing)
    
    except Exception as e:
        logger.error(f"Error getting billing: {str(e)}")
        return handle_error(e)

@app.route('/api/billing/pay', methods=['POST'])
@token_required
def pay_billing(current_user):
    """Pay billing for the current user."""
    try:
        data = request.json
        month = data.get('month', datetime.now().strftime('%Y-%m'))
        
        result = bill_usage(current_user['id'], month)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error paying billing: {str(e)}")
        return handle_error(e)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        # Login logic would be implemented here
        # For demonstration, we'll return a mock token
        token = generate_token(1)
        
        # Set token in cookie
        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie('token', token, httponly=True, secure=True)
        
        return response
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        # Registration logic would be implemented here
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Handle user logout."""
    response = make_response(redirect(url_for('home')))
    response.delete_cookie('token')
    return response

# Admin routes
@app.route('/admin/dashboard')
@token_required
@admin_required
def admin_dashboard(current_user):
    """Render the admin dashboard."""
    return render_template('admin/dashboard.html', user=current_user)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(error)}")
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # Run the app
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
