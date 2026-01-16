#!/usr/bin/env python3
"""
Linux Server Configuration for Twitter Bot
"""

import sys
import os

# Detect OS and set Chrome profile path
if sys.platform == "linux" or sys.platform == "linux2":
    # Linux
    CHROME_PROFILE_PATH = os.path.expanduser("~/.config/google-chrome")
elif sys.platform == "darwin":
    # macOS
    CHROME_PROFILE_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome")
elif sys.platform == "win32":
    # Windows
    CHROME_PROFILE_PATH = os.path.expanduser("~/.AppData/Local/Google/Chrome/User Data")
else:
    CHROME_PROFILE_PATH = os.path.expanduser("~/.config/google-chrome")

# Bot Configuration
BOT_CONFIG = {
    "chrome_profile_path": CHROME_PROFILE_PATH,
    "tweets_file": "tweets.txt",
    "hashtags_file": "hashtags.txt",
    
    # Interaction limits (per run)
    "hashtag_limit": 20,           # Number of posts to like/retweet per hashtag
    "retweet_limit": 10,           # Number of followings posts to retweet
    "hashtag_filter": "Iran",      # Only retweet followings posts with this hashtag
    
    # Delays (in seconds)
    "min_delay": 2,
    "max_delay": 7,
    "min_scroll_delay": 3,
    "max_scroll_delay": 7,
    
    # Scrolling
    "min_scroll_amount": 400,
    "max_scroll_amount": 800,
    
    # Random behavior
    "skip_retweet_chance": 0.1,    # 10% chance to skip retweet
    "pre_like_scroll_chance": 0.3, # 30% chance to scroll before liking
}

def get_config():
    """Get bot configuration"""
    return BOT_CONFIG

def is_headless():
    """Check if running in headless mode"""
    return "--headless" in sys.argv

def is_linux():
    """Check if running on Linux"""
    return sys.platform == "linux" or sys.platform == "linux2"

def is_windows():
    """Check if running on Windows"""
    return sys.platform == "win32"
