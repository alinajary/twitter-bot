#!/bin/bash
# One-time setup script to manually log into X/Twitter on the server
# This establishes the session in the Chrome profile for future automated runs

echo "======================================================================"
echo "ONE-TIME X/TWITTER LOGIN SETUP"
echo "======================================================================"
echo "This script will start Chrome with a visible browser for you to log in."
echo "After logging in once, future bot runs will be fully automated."
echo ""

# Start Xvfb on display :99
echo "Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
XVFB_PID=$!
export DISPLAY=:99
sleep 2
echo "✓ Virtual display started on :99"

# Navigate to the bot directory
cd /root/twitter-bot
source venv/bin/activate

echo ""
echo "Starting Chrome for manual login..."
echo "The browser will open to x.com - please log in when prompted."
echo ""

# Run the bot - it will wait for manual login
python3 twitter_bot.py --headless

# Kill Xvfb when done
kill $XVFB_PID 2>/dev/null
echo ""
echo "✓ Setup complete! The bot can now run automatically."
echo "  Run with: ./run_bot_server.sh"
