exports.handler = async (event, context) => {
  try {
    const statusData = {
      status: '✅ Online',
      timestamp: new Date().toISOString(),
      message: 'Nifty 50 EMA Alert System is operational',
      platform: 'Netlify Functions (Node.js)',
      environment: {
        UPSTOX_API_KEY: process.env.UPSTOX_API_KEY ? '✅ Set' : '❌ Missing',
        UPSTOX_API_SECRET: process.env.UPSTOX_API_SECRET ? '✅ Set' : '❌ Missing',
        TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN ? '✅ Set' : '❌ Missing',
        TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID ? '✅ Set' : '❌ Missing'
      },
      monitoring: 'GitHub Actions every 5 minutes during market hours',
      alerts: 'Bullish EMA signals sent to Telegram',
      endpoints: {
        status: '/.netlify/functions/status',
        auth: '/.netlify/functions/auth'
      }
    };

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify(statusData, null, 2)
    };

  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        status: '❌ Error',
        error: error.message,
        timestamp: new Date().toISOString()
      })
    };
  }
};
