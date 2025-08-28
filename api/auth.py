import os
import json
import webbrowser
import requests
from urllib.parse import urlparse, parse_qs

def handler(request):
    """Handle Upstox authentication setup"""
    
    if request.method == 'GET':
        # Return the authentication page
        client_id = os.environ.get('UPSTOX_CLIENT_ID')
        redirect_uri = os.environ.get('UPSTOX_REDIRECT_URI', 'https://your-vercel-app.vercel.app/api/auth')
        
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
    
    elif request.method == 'POST':
        # Handle the callback with authorization code
        try:
            body = json.loads(request.body) if request.body else {}
            code = body.get('code') or request.args.get('code')
            
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
            
            # Return success with token (in production, you'd save this to environment)
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
