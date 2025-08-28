exports.handler = async (event, context) => {
  try {
    const { httpMethod, queryStringParameters } = event;
    
    if (httpMethod === 'GET') {
      // Check if this is a callback with auth code
      if (queryStringParameters && queryStringParameters.code) {
        const authCode = queryStringParameters.code;
        
        return {
          statusCode: 200,
          headers: {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
          },
          body: `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authentication Success</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
                    .success { color: #28a745; font-size: 24px; margin-bottom: 20px; }
                    .code { background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; word-break: break-all; }
                    .note { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="success">✅ Authentication Successful!</div>
                <p><strong>Authorization Code Received:</strong></p>
                <div class="code">${authCode}</div>
                <div class="note">
                    <strong>✅ Setup Complete!</strong><br>
                    Your Nifty 50 EMA Alert System is now authenticated and ready.<br>
                    GitHub Actions will handle monitoring automatically every 5 minutes during market hours.<br>
                    Bullish EMA signals will be sent to your Telegram.
                </div>
                <p><a href="https://github.com/nigamk1/python-alert/actions" target="_blank">📊 View Monitoring Status</a></p>
            </body>
            </html>
          `
        };
      }
      
      // Show auth setup page
      const clientId = process.env.UPSTOX_API_KEY;
      const redirectUri = process.env.UPSTOX_REDIRECT_URI || 'https://nifty50-ema-alerts.netlify.app/.netlify/functions/auth';
      
      if (!clientId) {
        return {
          statusCode: 500,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ error: 'UPSTOX_API_KEY not configured' })
        };
      }
      
      const authUrl = `https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}`;
      
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'text/html',
          'Access-Control-Allow-Origin': '*'
        },
        body: `
          <!DOCTYPE html>
          <html>
          <head>
              <title>Upstox Authentication</title>
              <style>
                  body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                  .auth-container { text-align: center; padding: 30px; background: #f8f9fa; border-radius: 10px; }
                  .auth-button { display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-size: 18px; margin: 20px 0; }
                  .auth-button:hover { background: #0056b3; }
                  .info { background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0; }
              </style>
          </head>
          <body>
              <div class="auth-container">
                  <h1>🚀 Nifty 50 EMA Alerts</h1>
                  <h2>One-Time Authentication Setup</h2>
                  
                  <div class="info">
                      <strong>📝 Setup Instructions:</strong><br>
                      1. Click the button below to login to Upstox<br>
                      2. Authorize the application<br>
                      3. You'll be redirected back here automatically<br>
                      4. Your system will be ready for lifetime alerts!
                  </div>
                  
                  <a href="${authUrl}" class="auth-button">🔐 Login to Upstox</a>
                  
                  <div class="info">
                      <strong>⚡ After Authentication:</strong><br>
                      • GitHub Actions will monitor Nifty 50 every 5 minutes<br>
                      • Bullish EMA signals sent to Telegram: ${process.env.TELEGRAM_CHAT_ID}<br>
                      • System runs automatically during market hours<br>
                      • No further setup required!
                  </div>
              </div>
          </body>
          </html>
        `
      };
    }
    
    return {
      statusCode: 405,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Method not allowed' })
    };
    
  } catch (error) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: error.message })
    };
  }
};
