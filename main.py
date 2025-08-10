"""
Main entry point for the Discord bot with Flask web server for Replit hosting
"""
import os
import threading
from flask import Flask, jsonify
from bot import run_bot

# Flask app for keeping the bot alive on Replit
app = Flask(__name__)

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'Bot is running',
        'message': 'D&D Discord Bot is active'
    })

@app.route('/health')
def health():
    """Health check for uptime monitoring"""
    return jsonify({'status': 'healthy'})

def run_flask():
    """Run Flask server"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start the Discord bot
    run_bot()
