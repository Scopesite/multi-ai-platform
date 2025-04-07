document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    const aiForm = document.getElementById('ai-form');
    const resultContainer = document.getElementById('result-container');
    
    if (aiForm) {
        aiForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const provider = document.getElementById('provider').value;
            const prompt = document.getElementById('prompt').value;
            
            if (!prompt) {
                showError('Please enter a prompt');
                return;
            }
            
            // Show loading indicator
            resultContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p>Processing your request...</p></div>';
            
            // Send request to API
            fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getToken()}`
                },
                body: JSON.stringify({
                    provider: provider,
                    prompt: prompt
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    showResult(data);
                }
            })
            .catch(error => {
                showError(`Error: ${error.message}`);
            });
        });
    }
    
    // Helper functions
    function showResult(data) {
        let html = '<div class="alert alert-success">';
        html += `<h4>Response from ${data.provider}</h4>`;
        html += `<p>${data.text}</p>`;
        html += `<small class="text-muted">Response time: ${data.response_time ? data.response_time.toFixed(2) + 's' : 'N/A'}</small>`;
        html += '</div>';
        
        resultContainer.innerHTML = html;
    }
    
    function showError(message) {
        resultContainer.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
    
    function getToken() {
        // Get token from localStorage or cookies
        return localStorage.getItem('token') || getCookie('token') || '';
    }
    
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    }
    
    // Provider selection
    const providerSelect = document.getElementById('provider');
    if (providerSelect) {
        // Fetch available providers
        fetch('/api/providers')
            .then(response => response.json())
            .then(data => {
                if (data.providers && data.providers.length > 0) {
                    // Clear existing options
                    providerSelect.innerHTML = '';
                    
                    // Add new options
                    data.providers.forEach(provider => {
                        const option = document.createElement('option');
                        option.value = provider;
                        option.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
                        providerSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching providers:', error);
            });
    }
});
