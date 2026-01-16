#!/bin/bash
# Linux Setup Script for Twitter Bot

echo "========================================================================"
echo "Twitter Bot - Linux Setup Guide"
echo "========================================================================"

# Step 1: Install Python
echo ""
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
else
    echo "✓ Python 3 already installed"
fi

# Step 2: Install Chromium
echo ""
echo "[2/6] Checking Chromium installation..."
if ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "Installing Chromium..."
    sudo apt-get install -y chromium-browser
else
    echo "✓ Chromium already installed"
fi

# Step 3: Install dependencies
echo ""
echo "[3/6] Installing Python dependencies..."
pip3 install -r requirements.txt

# Step 4: Create Chrome profile directory
echo ""
echo "[4/6] Setting up Chrome profile directory..."
CHROME_PROFILE_DIR="$HOME/.config/google-chrome"
mkdir -p "$CHROME_PROFILE_DIR"
echo "Chrome profile directory: $CHROME_PROFILE_DIR"

# Step 5: Create run script
echo ""
echo "[5/6] Creating run script..."
cat > run_bot.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
python3 twitter_bot.py --headless
EOF
chmod +x run_bot.sh
echo "✓ Created run_bot.sh"

# Step 6: Setup cron job (optional)
echo ""
echo "[6/6] Cron Job Setup (Optional)"
echo "To run the bot daily at 9 AM, add this to your crontab:"
echo ""
echo "  0 9 * * * cd /path/to/twitter-bot && bash run_bot.sh >> bot.log 2>&1"
echo ""
echo "Edit crontab with: crontab -e"

echo ""
echo "========================================================================"
echo "✓ Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "1. Login to Chrome profile once:"
echo "   chromium-browser --user-data-dir='$CHROME_PROFILE_DIR'"
echo ""
echo "2. Log into X/Twitter account manually"
echo ""
echo "3. Run the bot:"
echo "   ./run_bot.sh"
echo ""
echo "========================================================================"
