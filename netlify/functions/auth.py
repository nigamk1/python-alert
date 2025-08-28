import json
import os
import sys
import webbrowser
import urllib.parse

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import requests
except ImportError as e:
    print(f"Import error: {e}")

def handler(event, context):
    """Handle Upstox authentication setup for Netlify"""
    
    http_method = event.get('httpMethod', 'GET')
    
    if http_method == 'GET':
        # Return the authentication page
        client_id = os.environ.get('UPSTOX_CLIENT_ID')
        redirect_uri = os.environ.get('UPSTOX_REDIRECT_URI', 'https://your-netlify-app.netlify.app/.netlify/functions/auth')
        
        if not client_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'UPSTOX_CLIENT_ID not configured'})
            }
        
        login_url = (
            f"https://api.upstox.com/v2/login/authorization/dialog?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}"
        )
        
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nifty 50 EMA Alerts - Setup</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .button {{ background: #0070f3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>🚀 Nifty 50 EMA Alerts Setup</h1>
            <p>Click the button below to authenticate with Upstox:</p>
            <a href="{login_url}" class="button">Login to Upstox</a>
            <p><small>After login, you'll be redirected back to complete the setup.</small></p>
        </body>
        </html>
        """
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_response
        }
    
    elif http_method == 'POST':
        # Handle the callback with authorization code
        try:
            body = json.loads(event.get('body', '{}'))
            query_params = event.get('queryStringParameters', {}) or {}
            
            code = body.get('code') or query_params.get('code')
            
            if not code:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Authorization code not provided'})
                }
            
            # Exchange code for access token
            client_id = os.environ.get('UPSTOX_CLIENT_ID')
            client_secret = os.environ.get('UPSTOX_CLIENT_SECRET')
            redirect_uri = os.environ.get('UPSTOX_REDIRECT_URI')
            
            if not all([client_id, client_secret, redirect_uri]):
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Missing Upstox configuration'})
                }
            
            # Token exchange
            token_url = "https://api.upstox.com/v2/login/authorization/token"
            token_data = {
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            }
            
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            token_result = response.json()
            access_token = token_result.get('access_token')
            
            if not access_token:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Failed to get access token'})
                }
            
            # Return success with token
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Authentication successful! Add this token to your environment variables:',
                    'access_token': access_token,
                    'instruction': 'Set UPSTOX_ACCESS_TOKEN environment variable with this token'
                })
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Authentication failed: {str(e)}'})
            }
