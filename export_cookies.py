#!/usr/bin/env python3
"""Export X/Twitter cookies from Windows Chrome to transfer to server"""
import sqlite3
import json
import os
import shutil
from pathlib import Path

# Windows Chrome cookie location
chrome_cookie_path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies')

# Make a copy (Chrome locks the file)
cookie_copy = 'Cookies_copy'
try:
    shutil.copy2(chrome_cookie_path, cookie_copy)
except Exception as e:
    print(f"Error copying cookies: {e}")
    print("Make sure Chrome is closed!")
    exit(1)

# Connect and extract X/Twitter cookies
try:
    conn = sqlite3.connect(cookie_copy)
    cursor = conn.cursor()
    
    # Get all x.com and twitter.com cookies
    cursor.execute("""
        SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly
        FROM cookies 
        WHERE host_key LIKE '%twitter.com%' OR host_key LIKE '%x.com%'
    """)
    
    cookies = []
    for row in cursor.fetchall():
        cookies.append({
            'domain': row[0],
            'name': row[1],
            'value': row[2],
            'path': row[3],
            'expires': row[4],
            'secure': bool(row[5]),
            'httpOnly': bool(row[6])
        })
    
    conn.close()
    os.remove(cookie_copy)
    
    # Save to JSON
    with open('twitter_cookies.json', 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"✓ Exported {len(cookies)} cookies to twitter_cookies.json")
    print("Now upload this file to the server:")
    print(f"  scp twitter_cookies.json root@135.181.89.177:~/twitter-bot/")
    
except Exception as e:
    print(f"Error extracting cookies: {e}")
    if os.path.exists(cookie_copy):
        os.remove(cookie_copy)
