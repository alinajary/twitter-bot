# Twitter Bot - Linux Server Deployment Guide

## Overview
This guide shows how to deploy the Twitter bot on a Linux server (Ubuntu/Debian) using Xvfb virtual display and undetected-chromedriver for anti-bot protection.

## Prerequisites
- Ubuntu 18.04+ or Debian 10+
- 2GB RAM minimum
- Internet connection

## Quick Setup (Automated)

```bash
# 1. Clone the project
git clone https://github.com/alinajary/twitter-bot.git
cd twitter-bot

# 2. Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv chromium-browser chromium-chromedriver xvfb

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python packages
pip install -r requirements.txt
pip install undetected-chromedriver

# 5. Setup credentials
python3 -c "from credentials_manager import setup_credentials; setup_credentials()"

# 6. ONE-TIME: Manual login to establish session
chmod +x setup_login.sh
./setup_login.sh
# When Chrome opens, log into X/Twitter, then press ENTER

# 7. Run the bot (fully automated after first login)
chmod +x run_bot_server.sh
./run_bot_server.sh
```

## Important: First-Time Login

**You must log into X/Twitter once manually** to establish the session. After that, all future runs are fully automated.

```bash
# Run one-time setup
./setup_login.sh
```

This will:
1. Start virtual display (Xvfb)
2. Open Chrome for manual login
3. Save your session for future automated runs
4. Press ENTER after logging in

## Manual Setup

### 1. Install Python 3
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

### 2. Install Chromium Browser
```bash
sudo apt-get install -y chromium-browser
# OR
sudo apt-get install -y chromium
```

### 3. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 4. Setup Chrome Profile (One-time)

First, login to X/Twitter manually:

```bash
# Start Chrome with a profile directory
chromium-browser --user-data-dir=$HOME/.config/google-chrome &

# In the Chrome window:
# 1. Go to https://x.com
# 2. Log in with your account
# 3. Close Chrome
```

### 5. Run the Bot

**Test run (interactive):**
```bash
python3 twitter_bot.py
```

**Production run (headless - no display needed):**
```bash
python3 twitter_bot.py --headless
```

## Scheduling (Automated Runs)

### Option A: Using Crontab (Recommended)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM:
0 9 * * * cd /path/to/twitter-bot && python3 twitter_bot.py --headless >> bot.log 2>&1

# Run every 6 hours:
0 */6 * * * cd /path/to/twitter-bot && python3 twitter_bot.py --headless >> bot.log 2>&1

# Run every day at 3 AM and 3 PM:
0 3,15 * * * cd /path/to/twitter-bot && python3 twitter_bot.py --headless >> bot.log 2>&1
```

View cron logs:
```bash
tail -f bot.log
```

### Option B: Using Systemd Timer

Create service file:
```bash
sudo nano /etc/systemd/system/twitter-bot.service
```

Paste this:
```ini
[Unit]
Description=Twitter Bot Automation
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/twitter-bot
ExecStart=/usr/bin/python3 /path/to/twitter-bot/twitter_bot.py --headless
StandardOutput=append:/path/to/twitter-bot/bot.log
StandardError=append:/path/to/twitter-bot/bot.log
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create timer file:
```bash
sudo nano /etc/systemd/system/twitter-bot.timer
```

Paste this:
```ini
[Unit]
Description=Twitter Bot Timer
Requires=twitter-bot.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=6h
AccuracySec=1min

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable twitter-bot.timer
sudo systemctl start twitter-bot.timer
sudo systemctl status twitter-bot.timer
```

## Monitoring

### Check bot logs:
```bash
tail -f bot.log
```

### Check if Chromium is running:
```bash
ps aux | grep chromium
```

### Kill stuck Chromium processes:
```bash
pkill -f chromium
```

## Troubleshooting

### "Chrome not found"
```bash
# Install it
sudo apt-get install chromium-browser

# Or try the other variant
sudo apt-get install chromium
```

### "Cannot connect to Chrome"
```bash
# Kill any stuck processes
pkill -f chromium
pkill -f chrome

# Check if port 9222 is in use
lsof -i :9222

# Wait a few seconds and try again
sleep 5
python3 twitter_bot.py --headless
```

### Sandboxing issues
```bash
# If you see sandbox errors, add this to chrome command
--no-sandbox --disable-dev-shm-usage
```
(Already included in the bot code)

### Out of memory
```bash
# Check available memory
free -h

# If running out of memory, reduce interaction limits in main script:
# Change limit=20 to limit=10
```

## Customization

Edit these files to customize:

- **tweets.txt** - Your tweet messages (one per line)
- **hashtags.txt** - Hashtags to interact with (one per line)
- **twitter_bot.py** - Change limits and delays

## File Structure

```
twitter-bot/
├── twitter_bot.py          # Main bot script
├── tweets.txt              # Tweet messages
├── hashtags.txt            # Hashtags to use
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── setup_linux.sh         # Automated setup script
├── README_LINUX.md        # This file
├── bot.log                # Log file (created after first run)
└── start_chrome.py        # Helper script
```

## Security Notes

⚠️ **Important:**
- Never share your Chrome profile or login credentials
- Use a dedicated X/Twitter account for automation
- Monitor your account regularly for unusual activity
- Review X/Twitter's Terms of Service to ensure compliance

## Support

If you encounter issues:

1. Check `bot.log` for error messages
2. Test Chrome manually: `chromium-browser --user-data-dir=$HOME/.config/google-chrome`
3. Verify internet connection
4. Check Python version: `python3 --version` (should be 3.7+)

## License

Use responsibly and in compliance with X/Twitter's Terms of Service.
