"""
Secure credentials storage for Twitter Bot
Uses environment variables or encrypted file storage
"""

import os
import json
from pathlib import Path

CREDENTIALS_FILE = "credentials.json"
CREDENTIALS_TEMPLATE = {
    "email": "",
    "password": "",
    "phone": ""  # For 2FA if needed
}

def setup_credentials():
    """Setup credentials interactively"""
    print("\n" + "="*70)
    print("CREDENTIALS SETUP")
    print("="*70)
    print("WARNING: Store credentials securely!")
    print("Option 1: Use environment variables (SAFER)")
    print("Option 2: Save to file (less safe)")
    print("="*70)
    
    choice = input("\nChoose option (1 or 2): ").strip()
    
    if choice == "1":
        print("\nSet environment variables:")
        print("  export TWITTER_EMAIL='your_email@example.com'")
        print("  export TWITTER_PASSWORD='your_password'")
        print("\nThen run the bot.")
        return None
    else:
        email = input("Enter X/Twitter email: ").strip()
        password = input("Enter X/Twitter password: ").strip()
        phone = input("Enter phone (optional, for 2FA): ").strip()
        
        credentials = {
            "email": email,
            "password": password,
            "phone": phone
        }
        
        # Save to file
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)
        
        # Set file permissions (read-only for user)
        os.chmod(CREDENTIALS_FILE, 0o600)
        
        print(f"\n✓ Credentials saved to {CREDENTIALS_FILE}")
        print("WARNING: Keep this file secure and don't share it!")
        return credentials

def get_credentials():
    """Get credentials from environment variables or file"""
    
    # Try environment variables first (safer)
    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")
    phone = os.getenv("TWITTER_PHONE", "")
    
    if email and password:
        print("✓ Using credentials from environment variables")
        return {
            "email": email,
            "password": password,
            "phone": phone
        }
    
    # Try credentials file
    if Path(CREDENTIALS_FILE).exists():
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    
    # No credentials found
    return None

def has_credentials():
    """Check if credentials are available"""
    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")
    
    if email and password:
        return True
    
    return Path(CREDENTIALS_FILE).exists()
