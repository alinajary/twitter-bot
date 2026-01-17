#!/bin/bash
# Automated cron script to run Twitter bot with proper environment
# This ensures Xvfb is running and sets up all needed environment variables

# Set display for Xvfb
export DISPLAY=:99

# Check if Xvfb is running, start if not
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "Starting Xvfb on display :99..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    sleep 2
fi

# Navigate to bot directory
cd /root/twitter-bot

# Activate virtual environment and run bot
source venv/bin/activate
python3 -u twitter_bot.py --headless

# Exit with bot's exit code
exit $?
