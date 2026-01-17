#!/usr/bin/env python3
import undetected_chromedriver as uc
import os

os.environ['DISPLAY'] = ':99'

print("Testing undetected_chromedriver...")
print(f"UC version: {uc.__version__}")

try:
    driver = uc.Chrome(driver_executable_path="/usr/bin/chromedriver")
    print("✓ Chrome started successfully!")
    driver.get("https://x.com")
    print(f"✓ Navigated to x.com, current URL: {driver.current_url}")
    driver.quit()
    print("✓ Test completed!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
