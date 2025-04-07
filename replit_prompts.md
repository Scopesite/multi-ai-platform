# Replit Prompts for AI Aggregation Platform

This document provides clear prompts and instructions for implementing the AI Aggregation Platform in Replit. These prompts are designed to guide the development process step-by-step, focusing on quality over speed.

## Initial Setup Prompts

### 1. Project Creation and Environment Setup

```
Create a new Python project in Replit for an AI aggregation platform. Set up a Flask application with the following structure:

/my-ai-platform
├── /static         # CSS, JS for frontend
├── /templates      # HTML files
├── /src
│   ├── /api
│   │   ├── /providers     # AI provider integrations
│   │   ├── /middleware    # Request processing, auth, logging
│   │   └── /routes        # API endpoints
│   ├── /services          # Business logic
│   ├── /models            # Data models
│   ├── /utils             # Helper functions
│   └── app.py             # Main Flask app
├── /tests                 # Test files
├── .env                   # Environment variables
└── README.md              # Project documentation

Install the following dependencies:
- Flask
- requests
- python-dotenv
- Flask-Login
- PyJWT
- pytest (for testing)
```

### 2. Basic Flask Application Setup

```
Create a basic Flask application in app.py with the following features:
- Load environment variables from .env file
- Set up basic routes for home page
- Configure the application to run on host='0.0.0.0' and port=8080
- Create a simple HTML template for the home page

Make sure the application runs correctly in Replit by clicking the Run button.
```

## Core Components Implementation

### 3. API Provider Integration

```
Implement the OpenAI provider integration in src/api/providers/openai.py with the following features:
- Create a class that handles authentication with the OpenAI API
- Implement methods to send requests to the API
- Handle responses and errors
- Log all API calls and errors
- Implement rate limiting to avoid exceeding API quotas

Test the integration by creating a simple endpoint that sends a request to the OpenAI API and returns the response.
```

### 4. Authentication System

```
Implement a user authentication system with the following features:
- User registration and login
- Secure password storage using bcrypt
- JWT token generation for API authentication
- User profile management
- API key storage (encrypted)
- Role-based access control

Create templates for login and registration pages.
```

### 5. Database Setup

```
Set up a SQLite database with the following tables:
- Users (id, username, email, password_hash, created_at, updated_at)
- ApiKeys (id, user_id, provider, api_key_encrypted, created_at, updated_at)
- Usage (id, user_id, provider, endpoint, timestamp, status, response_time)

Implement database models using SQLAlchemy or a similar ORM.
```

### 6. API Gateway Implementation

```
Create an API gateway that handles:
- Routing requests to the appropriate provider
- Authentication and authorization
- Rate limiting
- Request validation
- Response formatting
- Error handling
- Logging

Implement the gateway as a middleware that processes all API requests.
```

## Feature Implementation Prompts

### 7. User Interface Development

```
Create a user interface for the AI aggregation platform with the following features:
- Clean, responsive design using CSS
- Input form for sending prompts to AI providers
- Dropdown for selecting AI provider
- Display area for showing responses
- User authentication forms (login/register)
- User profile management
- API key management

Use HTML, CSS, and JavaScript for the frontend. Consider using a CSS framework like Bootstrap for responsive design.
```

### 8. Web Design Niche Features

```
Implement web design specific features:
- GitHub integration for pulling and pushing code
- AI-driven CSS generation from text descriptions
- Code snippet generation and management
- HTML/CSS/JS template library
- Design-to-code conversion using AI

Create specialized UI components for these features.
```

### 9. Sales Niche Features

```
Implement sales specific features:
- Email template generation
- Lead data extraction from websites
- CRM integration (HubSpot, Salesforce)
- Sales message personalization
- LinkedIn message generation
- Follow-up email scheduling

Create specialized UI components for these features.
```

### 10. Error Handling and Monitoring

```
Implement comprehensive error handling and monitoring:
- Client-side input validation
- Server-side request validation
- Detailed error logging
- User-friendly error messages
- Circuit breakers for failing APIs
- Fallback mechanisms when primary providers are unavailable
- Performance monitoring

Create a dashboard for monitoring system health and performance.
```

## Testing and Deployment Prompts

### 11. Testing Implementation

```
Implement a comprehensive testing strategy:
- Unit tests for each module
- Integration tests for API connections
- Mock services for testing without API credits
- End-to-end tests for critical user flows
- Performance tests for API response times

Use pytest for writing and running tests.
```

### 12. Deployment Configuration

```
Configure the application for deployment in Replit:
- Set up environment variables in Replit Secrets
- Configure the application to use production settings
- Set up proper error handling for production
- Implement CORS for API access
- Configure rate limiting for production use

Test the deployment by accessing the Replit URL.
```

## Monetization Implementation

### 13. Subscription System

```
Implement a subscription system with the following features:
- Tiered subscription plans (Free, Pro, Enterprise)
- Payment processing using Stripe
- Usage tracking and billing
- Subscription management UI
- Access control based on subscription level

Create templates for subscription management pages.
```

### 14. Usage Tracking and Billing

```
Implement usage tracking and billing:
- Track API calls by user and provider
- Calculate costs based on usage
- Generate invoices
- Implement usage limits based on subscription tier
- Provide usage analytics to users

Create a dashboard for users to monitor their usage.
```

## Advanced Features Prompts

### 15. Chrome Extension Integration

```
Implement a Chrome extension that integrates with the platform:
- Authentication with the main platform
- Quick access to AI features from the browser
- Context-aware suggestions based on current webpage
- Web scraping capabilities for sales features
- Code analysis for web design features

Package the extension for Chrome Web Store submission.
```

### 16. Caching and Performance Optimization

```
Implement caching and performance optimizations:
- Cache frequent API responses
- Implement request batching for multiple API calls
- Optimize database queries
- Implement background processing for long-running tasks
- Use WebSockets for real-time updates

Measure and document performance improvements.
```

## Quality Assurance Prompts

### 17. Security Audit

```
Perform a security audit of the application:
- Check for common vulnerabilities (OWASP Top 10)
- Implement proper authentication and authorization
- Secure API key storage
- Implement rate limiting and DDOS protection
- Validate all user inputs
- Implement proper error handling that doesn't expose sensitive information

Document security measures and potential vulnerabilities.
```

### 18. Documentation

```
Create comprehensive documentation for the platform:
- API documentation using OpenAPI/Swagger
- User guides for different features
- Developer documentation for extending the platform
- Deployment and configuration guides
- Troubleshooting guides

Make documentation accessible through the platform UI.
```

## Implementation Examples

### Basic Flask App Example

```python
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    data = request.json
    prompt = data.get('prompt')
    provider = data.get('provider', 'openai')
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    # This would be replaced with actual provider logic
    result = f"Processed '{prompt}' with {provider}"
    
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### OpenAI Provider Example

```python
import requests
import os
import logging
from datetime import datetime

class OpenAIProvider:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = 'https://api.openai.com/v1/chat/completions'
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            filename='openai.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('openai_provider')
    
    def process(self, prompt, model='gpt-3.5-turbo'):
        try:
            self.logger.info(f"Processing prompt with model {model}")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}]
            }
            
            start_time = datetime.now()
            response = requests.post(self.base_url, json=data, headers=headers)
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Response received in {response_time} seconds")
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'text': result['choices'][0]['message']['content'],
                'model': model,
                'provider': 'openai',
                'response_time': response_time
            }
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            return {
                'error': f"API request failed: {str(e)}",
                'provider': 'openai'
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'error': f"Unexpected error: {str(e)}",
                'provider': 'openai'
            }
```

### User Authentication Example

```python
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Mock database for demonstration
users_db = []

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # Check if user already exists
    if any(user['email'] == data['email'] for user in users_db):
        return jsonify({'message': 'User already exists'}), 409
    
    # Create new user
    new_user = {
        'id': len(users_db) + 1,
        'name': data['name'],
        'email': data['email'],
        'password': generate_password_hash(data['password'])
    }
    
    users_db.append(new_user)
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    
    # Find user by email
    user = next((user for user in users_db if user['email'] == data['email']), None)
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    
    return jsonify({'token': token}), 200

# Middleware to protect routes
def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = next((user for user in users_db if user['id'] == data['user_id']), None)
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': f'Hello {current_user["name"]}!'}), 200
```

These prompts and examples provide a comprehensive guide for implementing the AI Aggregation Platform in Replit. They cover all aspects of the development process, from initial setup to advanced features, with a focus on quality and robustness.
