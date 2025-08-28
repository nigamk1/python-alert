import json
from datetime import datetime

def handler(request):
    """Status endpoint to check if the system is running"""
    
    try:
        status_data = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'message': 'Nifty 50 EMA Alert System is active',
            'version': '1.0.0',
            'endpoints': {
                'alerts': '/api/check_alerts',
                'auth': '/api/auth',
                'status': '/api/status'
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
