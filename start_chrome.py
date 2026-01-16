import subprocess
import os
import time

# Your Chrome profile path
CHROME_PROFILE_PATH = r"C:\Users\Ali\AppData\Local\Google\Chrome\User Data"

# Chrome executable path
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Check if Chrome exists
if not os.path.exists(CHROME_EXE):
    print("ERROR: Chrome not found at:", CHROME_EXE)
    print("Please install Chrome or update the path in this script")
    exit(1)

# Start Chrome with remote debugging
print("="*70)
print("Starting Chrome with remote debugging...")
print("="*70)
print(f"Profile: {CHROME_PROFILE_PATH}")
print(f"Debugging port: 9222")
print("\nChrome will open in a new window...")
print("="*70 + "\n")

cmd = [
    CHROME_EXE,
    f'--user-data-dir={CHROME_PROFILE_PATH}',
    '--remote-debugging-port=9222'
]

try:
    subprocess.Popen(cmd)
    time.sleep(3)
    print("✓ Chrome started successfully!")
    print("\nNow:")
    print("1. Log into your X/Twitter account in the Chrome window")
    print("2. Then run: python twitter_bot.py")
    print("\n" + "="*70)
except Exception as e:
    print(f"ERROR starting Chrome: {e}")
    exit(1)
