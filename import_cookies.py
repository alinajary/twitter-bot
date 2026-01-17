#!/usr/bin/env python3
"""Import cookies into Chrome profile on Linux server"""
import json
import sqlite3
import os
from pathlib import Path

# Load exported cookies
with open('twitter_cookies.json', 'r') as f:
    cookies = json.load(f)

# Chrome cookie database on Linux
cookie_db = os.path.expanduser('~/.config/chromium/Default/Cookies')

# Create directory if it doesn't exist
os.makedirs(os.path.dirname(cookie_db), exist_ok=True)

# If database doesn't exist, we need to create it with proper schema
if not os.path.exists(cookie_db):
    print("Creating new Cookies database...")
    conn = sqlite3.connect(cookie_db)
    cursor = conn.cursor()
    
    # Create cookies table with proper schema
    cursor.execute('''
        CREATE TABLE cookies(
            creation_utc INTEGER NOT NULL,
            host_key TEXT NOT NULL,
            top_frame_site_key TEXT NOT NULL DEFAULT '',
            name TEXT NOT NULL,
            value TEXT NOT NULL,
            encrypted_value BLOB DEFAULT '',
            path TEXT NOT NULL,
            expires_utc INTEGER NOT NULL,
            is_secure INTEGER NOT NULL,
            is_httponly INTEGER NOT NULL,
            last_access_utc INTEGER NOT NULL,
            has_expires INTEGER NOT NULL DEFAULT 1,
            persistent INTEGER NOT NULL DEFAULT 1,
            priority INTEGER NOT NULL DEFAULT 1,
            samesite INTEGER NOT NULL DEFAULT -1,
            source_scheme INTEGER NOT NULL DEFAULT 0,
            source_port INTEGER NOT NULL DEFAULT -1,
            is_same_party INTEGER NOT NULL DEFAULT 0,
            last_update_utc INTEGER NOT NULL DEFAULT 0,
            UNIQUE (host_key, top_frame_site_key, name, path, source_scheme, source_port)
        )
    ''')
    conn.commit()
else:
    print("Opening existing Cookies database...")
    conn = sqlite3.connect(cookie_db)
    cursor = conn.cursor()
    
    # Clear existing Twitter/X cookies
    cursor.execute("DELETE FROM cookies WHERE host_key LIKE '%twitter.com%' OR host_key LIKE '%x.com%'")
    conn.commit()

# Insert cookies
print(f"Importing {len(cookies)} cookies...")
for cookie in cookies:
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO cookies 
            (creation_utc, host_key, top_frame_site_key, name, value, path, expires_utc, 
             is_secure, is_httponly, last_access_utc, has_expires, persistent)
            VALUES (?, ?, '', ?, ?, ?, ?, ?, ?, ?, 1, 1)
        ''', (
            cookie['expires'],  # creation_utc
            cookie['domain'],   # host_key
            cookie['name'],     # name
            cookie['value'],    # value
            cookie['path'],     # path
            cookie['expires'],  # expires_utc
            1 if cookie['secure'] else 0,      # is_secure
            1 if cookie['httpOnly'] else 0,    # is_httponly
            cookie['expires'],  # last_access_utc
        ))
    except Exception as e:
        print(f"Error importing cookie {cookie['name']}: {e}")

conn.commit()
conn.close()

print(f"✓ Successfully imported cookies to {cookie_db}")
print("✓ Chrome profile is now authenticated!")
