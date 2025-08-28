import json
from datetime import datetime

def handler(event, context):
    """Status endpoint to check if the system is running"""
    
    try:
        status_data = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'message': 'Nifty 50 EMA Alert System is active on Netlify',
            'version': '1.0.0',
            'platform': 'Netlify Functions',
            'endpoints': {
                'alerts': '/.netlify/functions/check_alerts',
                'auth': '/.netlify/functions/auth',
                'status': '/.netlify/functions/status'
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(status_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
