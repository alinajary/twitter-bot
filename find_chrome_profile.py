import os
import json

# Common Chrome profile locations on Windows
common_paths = [
    r"C:\Users\Ali\AppData\Local\Google\Chrome\User Data\Default",
    r"C:\Users\Ali\AppData\Local\Google\Chrome\User Data\Profile 1",
    r"C:\Users\Ali\AppData\Local\Google\Chrome\User Data\Profile 2",
]

print("Looking for Chrome profiles...\n")

base_path = r"C:\Users\Ali\AppData\Local\Google\Chrome\User Data"

if os.path.exists(base_path):
    profiles = os.listdir(base_path)
    print(f"Found Chrome profiles at: {base_path}\n")
    print("Available profiles:")
    for profile in profiles:
        profile_path = os.path.join(base_path, profile)
        if os.path.isdir(profile_path):
            print(f"  - {profile_path}")
            # Check if this profile has login data
            prefs_file = os.path.join(profile_path, "Preferences")
            if os.path.exists(prefs_file):
                print(f"    ✓ Has Preferences file (likely active)")
else:
    print(f"Chrome data not found at: {base_path}")

print("\n" + "="*70)
print("IMPORTANT: Copy the profile path you see above that contains your")
print("Twitter account and paste it in twitter_bot.py line 156")
print("="*70)
