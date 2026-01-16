#!/bin/bash
# Wrapper script to run Twitter bot with Xvfb on Linux server

# Start Xvfb on display :99
Xvfb :99 -screen 0 1920x1080x24 &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

# Run the bot
cd /root/twitter-bot
source venv/bin/activate
python3 twitter_bot.py --headless

# Kill Xvfb when done
kill $XVFB_PID 2>/dev/null
