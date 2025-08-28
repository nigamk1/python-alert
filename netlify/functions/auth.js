const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  return new Promise((resolve, reject) => {
    // Path to our Python auth script
    const pythonScript = path.join(__dirname, '../../auth.py');
    
    // Set environment variables for the Python script
    const env = {
      ...process.env,
      UPSTOX_API_KEY: process.env.UPSTOX_API_KEY,
      UPSTOX_API_SECRET: process.env.UPSTOX_API_SECRET,
      UPSTOX_REDIRECT_URI: process.env.UPSTOX_REDIRECT_URI,
      TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN,
      TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID
    };

    const python = spawn('python3', [pythonScript], { env });
    
    let stdout = '';
    let stderr = '';
    
    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve({
          statusCode: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          },
          body: JSON.stringify({
            message: 'Auth process completed',
            output: stdout
          })
        });
      } else {
        resolve({
          statusCode: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          },
          body: JSON.stringify({
            error: 'Auth process failed',
            details: stderr
          })
        });
      }
    });
  });
};
