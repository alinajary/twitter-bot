import time
import random
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
from credentials_manager import get_credentials, has_credentials, setup_credentials

# Import undetected_chromedriver for Linux servers (bypasses bot detection)
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

class TwitterBot:
    """
    A class to automate Twitter interactions using Selenium.
    """

    def __init__(self, chrome_profile_path, tweets_file="tweets.txt", hashtags_file="hashtags.txt", headless=False):
        """
        Initializes the TwitterBot.

        Args:
            chrome_profile_path (str): The path to your Chrome user profile.
            tweets_file (str): Path to file containing tweet texts (one per line).
            hashtags_file (str): Path to file containing hashtags to interact with (one per line).
            headless (bool): Run in headless mode (for servers without display). Default: False
        """
        # Load tweets from file
        self.tweets = self._load_tweets(tweets_file)
        if not self.tweets:
            print("WARNING: No tweets loaded. Using default tweet.")
            self.tweets = ["Free Iran! #Pahlavi #FreeIran #Iran"]
        
        # Load hashtags from file
        self.hashtags = self._load_hashtags(hashtags_file)
        if not self.hashtags:
            print("WARNING: No hashtags loaded. Using default hashtag.")
            self.hashtags = ["Iran"]
        
        # Instructions for the user
        print("\n" + "="*70)
        print("SETUP INSTRUCTIONS:")
        print("="*70)
        print("Starting Chrome with your profile...")
        print(f"Loaded {len(self.tweets)} different tweet texts")
        print(f"Loaded {len(self.hashtags)} different hashtags")
        print(f"Headless mode: {headless}")
        print("="*70 + "\n")
        
        # Find Chrome executable
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
        
        chrome_exe = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_exe = path
                print(f"Found Chrome at: {chrome_exe}")
                break
        
        if not chrome_exe:
            print("✗ ERROR: Google Chrome not found!")
            print("Install Chrome with: sudo apt-get install chromium-browser")
            raise Exception("Chrome not installed or not found at standard location")
        
        # Close all previous Chrome windows
        print("\nClosing any previous Chrome windows...")
        if sys.platform == "win32" or sys.platform == "cygwin":
            os.system("taskkill /F /IM chrome.exe 2>nul")
        else:
            os.system("pkill -9 chrome 2>/dev/null || true")
            os.system("pkill -9 chromium 2>/dev/null || true")
        
        time.sleep(2)  # Wait for Chrome processes to close
        print("✓ Previous Chrome windows closed")
        
        # Use undetected_chromedriver on Linux with Xvfb to bypass bot detection
        if (sys.platform == "linux" or sys.platform == "linux2") and headless and UC_AVAILABLE:
            print("Using undetected_chromedriver with virtual display for anti-bot protection...")
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            # DON'T pass user-data-dir to UC - it manages profiles itself
            
            # Set virtual display for Xvfb
            os.environ['DISPLAY'] = ':99'
            
            try:
                # Use system chromedriver with UC
                self.driver = uc.Chrome(
                    options=options, 
                    driver_executable_path="/usr/bin/chromedriver"
                )
                self.wait = WebDriverWait(self.driver, 20)
                print("✓ Successfully started undetected Chrome with virtual display!")
                
                # Load cookies from file and inject them
                # Prefer live cookies from previous successful logins
                live_cookie_file = os.path.join(os.path.dirname(__file__), 'twitter_cookies_live.json')
                cookie_file = live_cookie_file if os.path.exists(live_cookie_file) else os.path.join(os.path.dirname(__file__), 'twitter_cookies.json')
                
                if os.path.exists(cookie_file):
                    print("Loading authentication cookies...")
                    import json
                    with open(cookie_file, 'r') as f:
                        cookies = json.load(f)
                    
                    # Navigate to x.com first (required to set cookies)
                    self.driver.get("https://x.com")
                    time.sleep(2)
                    
                    # Add each cookie
                    for cookie in cookies:
                        try:
                            # Selenium add_cookie requires specific format
                            cookie_dict = {
                                'name': cookie['name'],
                                'value': cookie['value'],
                                'domain': cookie['domain'],
                                'path': cookie['path'],
                                'secure': cookie['secure'],
                                'httpOnly': cookie['httpOnly']
                            }
                            # Add expiry if present
                            if cookie.get('expires'):
                                # Convert Chrome timestamp to Unix timestamp (seconds)
                                cookie_dict['expiry'] = int(cookie['expires'] / 1000000 - 11644473600)
                            
                            self.driver.add_cookie(cookie_dict)
                        except Exception as e:
                            # Some cookies may fail to add, that's OK
                            pass
                    
                    print(f"✓ Loaded {len(cookies)} cookies")
                    # Refresh to apply cookies
                    self.driver.get("https://x.com/home")
                    time.sleep(3)
                else:
                    print("⚠ No cookie file found, will need to login manually")
                
            except Exception as e:
                print(f"✗ Error starting undetected Chrome: {e}")
                import traceback
                traceback.print_exc()
                raise
        else:
            # Original method for Windows or non-headless
            # Start Chrome with debugging port
            cmd = [
                chrome_exe,
                f'--user-data-dir={chrome_profile_path}',
                '--remote-debugging-port=9222'
            ]
            
            # Add headless options for server mode
            if headless:
                cmd.extend([
                    '--headless=new',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                ])
            
            try:
                subprocess.Popen(cmd)
                print("✓ Chrome started!")
                time.sleep(5)  # Wait for Chrome to fully load
            except Exception as e:
                print(f"✗ Error starting Chrome: {e}")
                raise
            
            # Connect to the running Chrome instance
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            try:
                # Use system chromedriver on Linux, webdriver-manager on Windows
                if sys.platform == "linux" or sys.platform == "linux2":
                    service = Service("/usr/bin/chromedriver")
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 20)
                print("✓ Successfully connected to Chrome!")
                print("Make sure Chrome started correctly and is logged into X")
            except Exception as e:
                print(f"✗ Error connecting to Chrome: {e}")
                print("Make sure Chrome started correctly and is logged into X")
                raise
        
        # Now attempt auto-login if credentials available
        if has_credentials():
            print("\n✓ Credentials found! Attempting auto-login...")
            credentials = get_credentials()
            
            if self._auto_login(credentials):
                print("✓ Auto-login successful!")
                self._human_like_delay(3, 5)
            else:
                print("\n⚠ Auto-login failed. Please log in manually:")
                print("1. Log into your X/Twitter account in the Chrome window")
                print("2. Press ENTER here once logged in...")
                print("="*70 + "\n")
                input("Press ENTER once logged into X...")
        else:
            # No credentials - manual login required
            print("\nNo credentials found. Manual login required.")
            print("To automate login next time, run: python twitter_bot.py --setup-credentials")
            print("\n1. Log into your X/Twitter account in the Chrome window that opened")
            print("2. Press ENTER here once you're logged in...")
            print("="*70 + "\n")
            input("Press ENTER once logged into X...")
        
        # Save cookies after successful manual login for future automated runs
        if (sys.platform == "linux" or sys.platform == "linux2") and UC_AVAILABLE:
            print("\nSaving session cookies for future automated runs...")
            try:
                import json
                # Get all cookies from the browser
                cookies = self.driver.get_cookies()
                cookie_file = os.path.join(os.path.dirname(__file__), 'twitter_cookies_live.json')
                with open(cookie_file, 'w') as f:
                    json.dump(cookies, f, indent=2)
                print(f"✓ Saved {len(cookies)} cookies to twitter_cookies_live.json")
                print("  Next run will be fully automated!\n")
            except Exception as e:
                print(f"⚠ Could not save cookies: {e}\n")
        
        print("✓ Ready to start automation!")
        print("="*70 + "\n")

    def _load_tweets(self, tweets_file):
        """Load tweets from a text file (one per line)."""
        try:
            with open(tweets_file, 'r', encoding='utf-8') as f:
                tweets = [line.strip() for line in f if line.strip()]
            return tweets
        except FileNotFoundError:
            print(f"Warning: {tweets_file} not found")
            return []
        except Exception as e:
            print(f"Error loading tweets: {e}")
            return []

    def _load_hashtags(self, hashtags_file):
        """Load hashtags from a text file (one per line)."""
        try:
            with open(hashtags_file, 'r', encoding='utf-8') as f:
                hashtags = [line.strip() for line in f if line.strip()]
            return hashtags
        except FileNotFoundError:
            print(f"Warning: {hashtags_file} not found")
            return []
        except Exception as e:
            print(f"Error loading hashtags: {e}")
            return []

    def _get_random_tweet(self):
        """Get a random tweet from the loaded list."""
        return random.choice(self.tweets)

    def _get_random_hashtag(self):
        """Get a random hashtag from the loaded list."""
        return random.choice(self.hashtags)

    def _auto_login(self, credentials):
        """
        Automatically log in to X/Twitter using email and password.
        First checks if already logged in, then only logs in if needed.
        
        Args:
            credentials (dict): Dictionary with 'email' and 'password' keys
        """
        try:
            print("\n" + "="*70)
            print("AUTO-LOGIN ATTEMPT")
            print("="*70)
            
            # First, check if already logged in
            self.driver.get("https://x.com/home")
            self._human_like_delay(3, 4)
            
            try:
                self.driver.find_element(By.XPATH, '//*[@data-testid="SideNav_NewTweet_Button"]')
                print("✓ Already logged in! Skipping login...")
                return True
            except:
                print("Not logged in yet, attempting login...")
            
            # Go to login page
            self.driver.get("https://x.com/login")
            self._human_like_delay(3, 5)
            
            # Try to find email field with multiple attempts
            try:
                print("Finding email input...")
                email_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]')), timeout=5)
            except:
                print("Email field not found. Checking if already logged in...")
                try:
                    self.driver.find_element(By.XPATH, '//*[@data-testid="SideNav_NewTweet_Button"]')
                    print("✓ Already logged in!")
                    return True
                except:
                    print("✗ Email field not found and not logged in")
                    return False
            
            email_input.send_keys(credentials['email'])
            print(f"✓ Entered email: {credentials['email']}")
            self._human_like_delay(2, 3)
            
            # Click Next button
            next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Next")]')))
            next_button.click()
            self._human_like_delay(2, 4)
            
            # Find and fill password field
            print("Finding password input...")
            password_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password"]')))
            password_input.send_keys(credentials['password'])
            print("✓ Entered password")
            self._human_like_delay(2, 3)
            
            # Click Login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Log in")]')))
            login_button.click()
            print("✓ Submitted login form")
            self._human_like_delay(5, 8)
            
            # Check if login successful
            try:
                self.driver.find_element(By.XPATH, '//*[@data-testid="SideNav_NewTweet_Button"]')
                print("✓ Login successful!")
                return True
            except:
                print("✗ Login may have failed or 2FA required")
                return False
                
        except Exception as e:
            print(f"✗ Auto-login error: {e}")
            return False

    def _human_like_delay(self, min_seconds=5, max_seconds=15):
        """Waits for a random amount of time to simulate human behavior."""
        delay = random.uniform(min_seconds, max_seconds)
        # Occasionally take a much longer break (10% chance for 30-60s)
        if random.random() < 0.1:
            delay += random.uniform(30, 60)
            print(f"Simulating 'reading' time... waiting {int(delay)}s")
        time.sleep(delay)
    
    def _is_post_recent(self, post_element, max_hours=48):
        """
        Checks if a post is recent (within max_hours).
        Returns True ONLY if verified recent, False if old OR unable to determine.
        STRICT MODE: If we can't verify age, skip it (safer approach).
        
        Args:
            post_element: The Selenium WebElement of the post/article
            max_hours: Maximum age in hours (default 48 hours)
        """
        try:
            # Try to find the timestamp element within the post
            time_selectors = [
                './/time',
                './/*[@datetime]',
                './/*[contains(@class, "time")]',
            ]
            
            time_element = None
            for selector in time_selectors:
                try:
                    time_element = post_element.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if not time_element:
                # Can't find timestamp - SKIP IT (strict mode)
                print(f"  ⏰ Skipping post - no timestamp found")
                return False
            
            # Get the timestamp text (e.g., "2h", "45m", "3d")
            time_text = time_element.text.lower().strip()
            
            # Also try datetime attribute (most reliable)
            datetime_attr = time_element.get_attribute('datetime')
            
            if datetime_attr:
                # Parse ISO datetime format
                from datetime import datetime, timezone
                try:
                    post_time = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    hours_diff = (current_time - post_time).total_seconds() / 3600
                    
                    is_recent = hours_diff <= max_hours
                    if not is_recent:
                        print(f"  ⏰ Skipping old post ({int(hours_diff)}h = {int(hours_diff/24)}d old)")
                    return is_recent
                except Exception as e:
                    # If datetime parsing fails, skip it
                    print(f"  ⏰ Skipping post - couldn't parse datetime")
                    return False
            
            # Parse relative time text (e.g., "2h", "45m", "3d")
            if not time_text:
                print(f"  ⏰ Skipping post - no time text")
                return False
                
            if 'm' in time_text or 'min' in time_text:
                # Minutes old - definitely recent
                return True
            elif 'h' in time_text or 'hour' in time_text:
                # Extract hours
                try:
                    hours = int(''.join(filter(str.isdigit, time_text)))
                    is_recent = hours <= max_hours
                    if not is_recent:
                        print(f"  ⏰ Skipping old post ({hours}h old)")
                    return is_recent
                except:
                    print(f"  ⏰ Skipping post - couldn't parse hours from '{time_text}'")
                    return False
            elif 'd' in time_text or 'day' in time_text:
                # Days old
                try:
                    days = int(''.join(filter(str.isdigit, time_text)))
                    hours = days * 24
                    is_recent = hours <= max_hours
                    if not is_recent:
                        print(f"  ⏰ Skipping old post ({days}d old)")
                    return is_recent
                except:
                    print(f"  ⏰ Skipping post - couldn't parse days from '{time_text}'")
                    return False
            
            # If format is unknown, SKIP IT (strict mode)
            print(f"  ⏰ Skipping post - unknown time format: '{time_text}'")
            return False
            
        except Exception as e:
            # If ANY error checking age, SKIP IT (strict mode)
            print(f"  ⏰ Skipping post - error checking age: {e}")
            return False

    def _get_batch_tweets(self, max_scroll=5, target_count=20):
        """
        Batch collection: Scroll to load multiple tweets, then return all article elements.
        Much faster than one-by-one approach.
        
        Args:
            max_scroll: Maximum number of scrolls to perform
            target_count: Target number of tweets to collect
        
        Returns:
            List of article WebElements
        """
        print(f"📦 Collecting batch of tweets (target: {target_count})...")
        tweets_collected = set()
        
        for scroll in range(max_scroll):
            # Find all article elements
            articles = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            # Add new articles to set (using element ID to avoid duplicates)
            for article in articles:
                try:
                    article_id = article.get_attribute('innerHTML')[:100]  # Use partial HTML as ID
                    tweets_collected.add((article_id, article))
                except:
                    continue
            
            current_count = len(tweets_collected)
            print(f"  Scroll {scroll+1}/{max_scroll}: {current_count} tweets collected")
            
            if current_count >= target_count:
                break
            
            # Scroll down
            scroll_amount = random.randint(600, 1000)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self._human_like_delay(2, 4)
        
        # Extract just the WebElements
        tweet_elements = [article for _, article in tweets_collected]
        print(f"✓ Collected {len(tweet_elements)} total tweets")
        return tweet_elements

    def _filter_recent_tweets(self, tweet_elements, max_hours=48):
        """
        Filter tweets to only include recent ones.
        
        Args:
            tweet_elements: List of article WebElements
            max_hours: Maximum age in hours
        
        Returns:
            List of recent tweet WebElements
        """
        recent_tweets = []
        for tweet in tweet_elements:
            if self._is_post_recent(tweet, max_hours=max_hours):
                recent_tweets.append(tweet)
        
        print(f"✓ Filtered to {len(recent_tweets)} recent tweets (within {max_hours}h)")
        return recent_tweets

    def _get_tweet_engagement(self, tweet_element):
        """
        Extract engagement metrics (likes, retweets) from a tweet.
        
        Args:
            tweet_element: The tweet article WebElement
        
        Returns:
            Tuple (likes_count, retweets_count) or (0, 0) if can't parse
        """
        try:
            import re
            # Find like button and extract count from aria-label
            like_button = tweet_element.find_element(By.CSS_SELECTOR, 'button[data-testid="like"]')
            like_label = like_button.get_attribute('aria-label') or ""
            
            likes = 0
            if 'like' in like_label.lower():
                numbers = re.findall(r'([\d,\.]+[KkMm]?)', like_label)
                if numbers:
                    num_str = numbers[0].replace(',', '')
                    if 'K' in num_str or 'k' in num_str:
                        likes = int(float(num_str.replace('K', '').replace('k', '')) * 1000)
                    elif 'M' in num_str or 'm' in num_str:
                        likes = int(float(num_str.replace('M', '').replace('m', '')) * 1000000)
                    else:
                        likes = int(float(num_str))
            
            # Find retweet button and extract count
            retweet_button = tweet_element.find_element(By.CSS_SELECTOR, 'button[data-testid="retweet"]')
            retweet_label = retweet_button.get_attribute('aria-label') or ""
            
            retweets = 0
            if 'retweet' in retweet_label.lower() or 'repost' in retweet_label.lower():
                numbers = re.findall(r'([\d,\.]+[KkMm]?)', retweet_label)
                if numbers:
                    num_str = numbers[0].replace(',', '')
                    if 'K' in num_str or 'k' in num_str:
                        retweets = int(float(num_str.replace('K', '').replace('k', '')) * 1000)
                    elif 'M' in num_str or 'm' in num_str:
                        retweets = int(float(num_str.replace('M', '').replace('m', '')) * 1000000)
                    else:
                        retweets = int(float(num_str))
            
            return (likes, retweets)
        except:
            return (0, 0)

    def _has_meaningful_content(self, tweet_element):
        """
        Check if tweet has meaningful text content (not just hashtags/links).
        
        Args:
            tweet_element: The tweet article element
        
        Returns:
            bool: True if has meaningful content, False otherwise
        """
        try:
            # Find tweet text
            text_selectors = [
                './/div[@data-testid="tweetText"]',
                './/div[@lang]',
                './/*[contains(@class, "tweet-text")]',
            ]
            
            tweet_text = ""
            for selector in text_selectors:
                try:
                    text_element = tweet_element.find_element(By.XPATH, selector)
                    tweet_text = text_element.text.strip()
                    if tweet_text:
                        break
                except:
                    continue
            
            if not tweet_text:
                return False
            
            # Remove hashtags, mentions, and URLs to get actual content
            import re
            clean_text = re.sub(r'#\w+', '', tweet_text)  # Remove hashtags
            clean_text = re.sub(r'@\w+', '', clean_text)  # Remove mentions
            clean_text = re.sub(r'http\S+', '', clean_text)  # Remove URLs
            clean_text = re.sub(r'pic\.twitter\.com\S+', '', clean_text)  # Remove pic links
            clean_text = clean_text.strip()
            
            # Check if has at least 20 characters of actual content (about 3-4 words)
            if len(clean_text) >= 20:
                return True
            
            return False
        except:
            return False
    
    def _has_minimum_engagement(self, tweet_element, min_likes=2, min_retweets=1):
        """
        Check if tweet has minimum engagement (likes/retweets).
        Filters out low-quality posts with few views and no engagement.
        
        Args:
            tweet_element: The tweet article element
            min_likes: Minimum likes required (default 2)
            min_retweets: Minimum retweets required (default 1)
        
        Returns:
            bool: True if meets minimum engagement, False otherwise
        """
        try:
            likes, retweets = self._get_tweet_engagement(tweet_element)
            
            # Must have at least min_likes OR min_retweets
            # This filters out posts with 5 views and 0 engagement
            if likes >= min_likes or retweets >= min_retweets:
                return True
            
            return False
        except:
            return False

    def _sort_by_engagement(self, tweet_elements, min_likes=0, min_retweets=0):
        """
        Sort tweets by engagement and filter by minimum thresholds.
        
        Args:
            tweet_elements: List of article WebElements
            min_likes: Minimum likes required
            min_retweets: Minimum retweets required
        
        Returns:
            List of tweets sorted by engagement
        """
        tweet_data = []
        for tweet in tweet_elements:
            likes, retweets = self._get_tweet_engagement(tweet)
            total_engagement = likes + (retweets * 2)
            
            if likes >= min_likes and retweets >= min_retweets:
                tweet_data.append({
                    'element': tweet,
                    'likes': likes,
                    'retweets': retweets,
                    'engagement': total_engagement
                })
        
        tweet_data.sort(key=lambda x: x['engagement'], reverse=True)
        
        if tweet_data:
            print(f"\n📊 Engagement Stats:")
            for i, data in enumerate(tweet_data[:5], 1):
                print(f"  #{i}: {data['likes']} likes, {data['retweets']} retweets (score: {data['engagement']})")
            
            if min_likes > 0 or min_retweets > 0:
                print(f"✓ Filtered to {len(tweet_data)} tweets with ≥{min_likes} likes, ≥{min_retweets} retweets")
        
        return [data['element'] for data in tweet_data]

    # High-quality Iranian activist accounts to monitor
    TARGET_ACCOUNTS = [
        "PahlaviReza",          # Reza Pahlavi - Crown Prince
        "IranIntl_En",          # Iran International English
        "IranIntl",             # Iran International Persian  
        "manoto_news",          # Manoto News
        "AlinejadMasih",        # Masih Alinejad - Activist
        "AliKarimi_AKA",        # Ali Karimi - Football legend
        "nahidtv",              # Nahid TV
        "VOAIran",              # Voice of America Persian
        "bbcpersian",           # BBC Persian
    ]

    def send_tweet(self, text=None):
        """
        Posts a new tweet.

        Args:
            text (str): The content of the tweet. If None, uses a random tweet from tweets.txt
        """
        # Use random tweet if not specified
        if text is None:
            text = self._get_random_tweet()
        
        # Randomly select 2-4 hashtags (more natural variation)
        num_hashtags = random.randint(2, min(4, len(self.hashtags)))
        random_hashtags = random.sample(self.hashtags, num_hashtags)
        hashtag_string = " ".join([f"#{tag}" for tag in random_hashtags])
        full_tweet = f"{text}\n\n{hashtag_string}"
        
        try:
            # Navigate to home
            self.driver.get("https://x.com/home")
            self._human_like_delay(4, 6)
            
            # Debug: Check current page
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"DEBUG: Current URL: {current_url}")
            print(f"DEBUG: Page title: {page_title}")
            
            # Check if we're actually logged in
            if "login" in current_url.lower() or "login" in page_title.lower():
                print("✗ NOT LOGGED IN - redirected to login page!")
                print("Please log in manually and run the bot again.")
                return
            
            # Scroll to top to make compose box visible
            self.driver.execute_script("window.scrollTo(0, 0);")
            self._human_like_delay(2, 3)

            # Try multiple selectors for the tweet compose box
            tweet_box = None
            selectors = [
                'div[role="textbox"][aria-placeholder*="post"]',
                'div[role="textbox"][aria-placeholder*="Post"]',
                'div[aria-label*="Post"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[role="textbox"]',
                'div[data-testid="tweetTextarea_0"]',
            ]
            
            print(f"Looking for tweet compose box...")
            for selector in selectors:
                try:
                    tweet_box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"Found compose box with selector: {selector}")
                    break
                except:
                    continue
            
            if not tweet_box:
                print("Could not find tweet compose box - trying alternative method")
                # Try clicking the compose area first
                try:
                    compose_area = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "post")]')))
                    compose_area.click()
                    self._human_like_delay(2, 3)
                except:
                    print("Could not find or click compose area")
                    return
            
            # Scroll to make sure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tweet_box) if tweet_box else None
            self._human_like_delay(1, 2)
            
            # Click the tweet box
            if tweet_box:
                self.driver.execute_script("arguments[0].click();", tweet_box)
            self._human_like_delay(1, 2)
            
            # Type the tweet
            # Remove emojis that ChromeDriver can't handle (non-BMP characters)
            import re
            # Remove all emojis and special characters outside BMP
            tweet_for_chromedriver = re.sub(r'[^\u0000-\uFFFF]', '', full_tweet)
            self.driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]').send_keys(tweet_for_chromedriver)
            print(f"Typed tweet: {full_tweet}")
            self._human_like_delay(2, 4)
            
            # Find and click the tweet button using JavaScript
            tweet_buttons = [
                'button[data-testid="tweetButtonInline"]',
                'button[aria-label*="Post"]',
                'button:contains("Post")',
            ]
            
            tweet_button = None
            for selector in tweet_buttons:
                try:
                    tweet_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"Found tweet button with selector: {selector}")
                    break
                except:
                    continue
            
            if not tweet_button:
                print("Could not find tweet button")
                return
                
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tweet_button)
            self._human_like_delay(1, 2)
            self.driver.execute_script("arguments[0].click();", tweet_button)
            
            print(f"✓ Successfully tweeted: {full_tweet}")
            self._human_like_delay(5, 10)
        except Exception as e:
            print(f"Error sending tweet: {e}")
            import traceback
            traceback.print_exc()

    def _get_batch_tweets(self, max_scroll=5, target_count=20):
        """
        Batch collection: Scroll to load multiple tweets, then return all article elements.
        Much faster than one-by-one approach.
        
        Args:
            max_scroll: Maximum number of scrolls to perform
            target_count: Target number of tweets to collect
        
        Returns:
            List of article WebElements
        """
        print(f"📦 Collecting batch of tweets (target: {target_count})...")
        tweets_collected = set()
        
        for scroll in range(max_scroll):
            # Find all article elements
            articles = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            # Add new articles to set (using element ID to avoid duplicates)
            for article in articles:
                try:
                    article_id = article.get_attribute('innerHTML')[:100]  # Use partial HTML as ID
                    tweets_collected.add((article_id, article))
                except:
                    continue
            
            current_count = len(tweets_collected)
            print(f"  Scroll {scroll+1}/{max_scroll}: {current_count} tweets collected")
            
            if current_count >= target_count:
                break
            
            # Scroll down
            scroll_amount = random.randint(600, 1000)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self._human_like_delay(2, 4)
        
        # Extract just the WebElements
        tweet_elements = [article for _, article in tweets_collected]
        print(f"✓ Collected {len(tweet_elements)} total tweets")
        return tweet_elements

    def _filter_recent_tweets(self, tweet_elements, max_hours=48):
        """
        Filter tweets to only include recent ones.
        
        Args:
            tweet_elements: List of article WebElements
            max_hours: Maximum age in hours
        
        Returns:
            List of recent tweet WebElements
        """
        recent_tweets = []
        for tweet in tweet_elements:
            if self._is_post_recent(tweet, max_hours=max_hours):
                recent_tweets.append(tweet)
        
        print(f"✓ Filtered to {len(recent_tweets)} recent tweets (within {max_hours}h)")
        return recent_tweets

    def interact_with_hashtag(self, hashtag, limit=10):
        """
        Searches for a hashtag, then likes and retweets a specific number of posts.
        Now uses batch collection + filtering for efficiency.

        Args:
            hashtag (str): The hashtag to search for (without the '#').
            limit (int): The maximum number of posts to interact with.
        """
        try:
            # 50% chance to use Top (popular) vs Live (latest)
            # Top = more engagement, Live = more recent
            use_top = random.random() < 0.5
            
            if use_top:
                search_url = f"https://x.com/search?q=%23{hashtag}&f=top"
                print(f"\n🔍 Searching for #{hashtag} (top/popular tweets)...")
            else:
                search_url = f"https://x.com/search?q=%23{hashtag}&f=live"
                print(f"\n🔍 Searching for #{hashtag} (latest tweets)...")
            self.driver.get(search_url)
            self._human_like_delay(3, 5)
            
            # Batch collect tweets
            all_tweets = self._get_batch_tweets(max_scroll=5, target_count=limit*3)
            
            # Filter to recent only
            recent_tweets = self._filter_recent_tweets(all_tweets, max_hours=48)
            
            if not recent_tweets:
                print(f"⚠ No recent tweets found for #{hashtag}")
                return
            
            # Temporarily disable engagement filtering for testing
            tweets_to_interact = recent_tweets[:limit]
            print(f"\n👍 Will interact with {len(tweets_to_interact)} tweets for #{hashtag}\n")

            # Interact with each tweet in the batch
            for i, tweet_element in enumerate(tweets_to_interact, 1):
                try:
                    # Scroll tweet into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet_element)
                    self._human_like_delay(1, 2)
                    
                    # Check if tweet has meaningful content
                    if not self._has_meaningful_content(tweet_element):
                        print(f"⏭ Skipping tweet #{i} - no meaningful content (only hashtags/links)")
                        continue
                    
                    # Check if tweet has minimum engagement
                    if not self._has_minimum_engagement(tweet_element, min_likes=2, min_retweets=1):
                        print(f"⏭ Skipping tweet #{i} - low engagement (less than 2 likes or 1 retweet)")
                        continue
                    
                    # Find like button within this specific tweet
                    like_button = None
                    like_selectors = [
                        'button[data-testid="like"]',
                        '[data-testid="like"]',
                        'button[aria-label*="Like"]',
                    ]
                    
                    for selector in like_selectors:
                        try:
                            like_button = tweet_element.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue
                    
                    if not like_button:
                        print(f"  Could not find like button for tweet #{i}")
                        continue
                    
                    # Click like button
                    self.driver.execute_script("arguments[0].click();", like_button)
                    print(f"✓ Liked tweet #{i} for hashtag '{hashtag}'")
                    self._human_like_delay(2, 5)

                    # Random chance to skip retweet (more human-like)
                    if random.random() < 0.9:
                        # Find retweet button within this specific tweet
                        retweet_button = None
                        retweet_selectors = [
                            'button[data-testid="retweet"]',
                            '[data-testid="retweet"]',
                            'button[aria-label*="Retweet"]',
                        ]
                        
                        for selector in retweet_selectors:
                            try:
                                retweet_button = tweet_element.find_element(By.CSS_SELECTOR, selector)
                                break
                            except:
                                continue
                        
                        if not retweet_button:
                            print(f"  Could not find retweet button for tweet #{i}")
                        else:
                            # Click retweet
                            self.driver.execute_script("arguments[0].click();", retweet_button)
                            self._human_like_delay(2, 3)
                            
                            # Confirm retweet
                            confirm_selectors = [
                                'button[data-testid="retweetConfirm"]',
                                '[data-testid="retweetConfirm"]',
                            ]
                            
                            confirm_retweet = None
                            for selector in confirm_selectors:
                                try:
                                    confirm_retweet = WebDriverWait(self.driver, 5).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                    break
                                except:
                                    continue
                            
                            if confirm_retweet:
                                try:
                                    confirm_retweet.click()
                                    print(f"✓ Retweeted tweet #{i} for hashtag '{hashtag}'")
                                except:
                                    self.driver.execute_script("arguments[0].click();", confirm_retweet)
                                    print(f"✓ Retweeted tweet #{i} for hashtag '{hashtag}'")
                            
                            self._human_like_delay(2, 4)
                    
                    # Small delay between tweets
                    self._human_like_delay(2, 4)

                except Exception as e:
                    print(f"Could not interact with tweet #{i+1}: {e}")
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    self._human_like_delay(2, 4)
        except Exception as e:
            print(f"Error interacting with hashtag {hashtag}: {e}")

    # High-quality Iranian activist accounts to monitor
    TARGET_ACCOUNTS = [
        "PahlaviReza",          # Reza Pahlavi - Crown Prince
        "IranIntl_En",          # Iran International English
        "IranIntl",             # Iran International Persian  
        "manoto_news",          # Manoto News
        "AlinejadMasih",        # Masih Alinejad - Activist
        "AliKarimi_AKA",        # Ali Karimi - Football legend
        "nahidtv",              # Nahid TV
        "VOAIran",              # Voice of America Persian
        "bbcpersian",           # BBC Persian
    ]

    def retweet_from_target_accounts(self, limit=5):
        """
        Retweets recent posts from high-quality targeted accounts.
        More reliable than random home feed scanning.
        
        Args:
            limit (int): Maximum number of posts to retweet
        """
        try:
            random_hashtag_filter = self._get_random_hashtag()
            print(f"\n🎯 Targeting specific accounts with hashtag filter: #{random_hashtag_filter}\n")
            
            retweet_count = 0
            # Randomly select 3-4 accounts to check
            accounts_to_check = random.sample(self.TARGET_ACCOUNTS, min(4, len(self.TARGET_ACCOUNTS)))
            
            for account in accounts_to_check:
                if retweet_count >= limit:
                    break
                
                try:
                    # Visit account profile
                    print(f"\n📱 Checking @{account}...")
                    self.driver.get(f"https://x.com/{account}")
                    self._human_like_delay(3, 5)
                    
                    # Batch collect their recent tweets
                    all_tweets = self._get_batch_tweets(max_scroll=3, target_count=10)
                    
                    # Filter to recent only
                    recent_tweets = self._filter_recent_tweets(all_tweets, max_hours=48)
                    
                    if not recent_tweets:
                        print(f"  No recent tweets from @{account}")
                        continue
                    
                    # Check which tweets contain our hashtag
                    for tweet in recent_tweets:
                        if retweet_count >= limit:
                            break
                        
                        try:
                            tweet_text = tweet.text.lower()
                            if random_hashtag_filter.lower() not in tweet_text:
                                continue
                            
                            # Check if tweet has meaningful content
                            if not self._has_meaningful_content(tweet):
                                print(f"  ⏭ Skipping @{account} tweet - no meaningful content")
                                continue
                            
                            # Check if tweet has minimum engagement
                            if not self._has_minimum_engagement(tweet, min_likes=2, min_retweets=1):
                                print(f"  ⏭ Skipping @{account} tweet - low engagement")
                                continue
                            
                            print(f"  ✓ Found quality matching tweet from @{account}")
                            
                            # Find retweet button
                            retweet_button = None
                            try:
                                retweet_button = tweet.find_element(By.CSS_SELECTOR, 'button[data-testid="retweet"]')
                            except:
                                continue
                            
                            # Scroll into view
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet)
                            self._human_like_delay(1, 2)
                            
                            # Click retweet
                            self.driver.execute_script("arguments[0].click();", retweet_button)
                            self._human_like_delay(2, 3)
                            
                            # Confirm retweet
                            try:
                                confirm_button = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="retweetConfirm"]'))
                                )
                                confirm_button.click()
                                retweet_count += 1
                                print(f"✓ Retweeted post from @{account} (#{retweet_count})")
                                self._human_like_delay(3, 6)
                            except:
                                print(f"  Could not confirm retweet from @{account}")
                                
                        except Exception as e:
                            print(f"  Error processing tweet from @{account}: {e}")
                            continue
                    
                except Exception as e:
                    print(f"Error checking account @{account}: {e}")
                    continue
            
            print(f"\n✓ Retweeted {retweet_count} posts from targeted accounts\n")
            
        except Exception as e:
            print(f"Error in retweet_from_target_accounts: {e}")

    def retweet_from_followings(self, limit=10):
        """
        Retweets posts from your followings that contain a random hashtag.
        Now uses batch collection and optionally targets specific high-quality accounts.

        Args:
            limit (int): The maximum number of posts to retweet.
        """
        try:
            # 70% chance to use targeted accounts, 30% use home feed
            if random.random() < 0.7:
                print("📊 Using targeted account strategy")
                self.retweet_from_target_accounts(limit=limit)
                return
            
            # Otherwise use home feed
            print("📊 Using home feed strategy")
            random_hashtag_filter = self._get_random_hashtag()
            print(f"\n🏠 Checking home feed with hashtag filter: #{random_hashtag_filter}\n")
            
            self.driver.get("https://x.com/home")
            self._human_like_delay(3, 5)
            
            # Batch collect tweets from home feed
            all_tweets = self._get_batch_tweets(max_scroll=5, target_count=limit*3)
            
            # Filter to recent only
            recent_tweets = self._filter_recent_tweets(all_tweets, max_hours=48)
            
            if not recent_tweets:
                print(f"⚠ No recent tweets found in home feed")
                return
            
            retweet_count = 0
            posts_checked = 0
            
            for tweet_element in recent_tweets:
                if retweet_count >= limit:
                    break
                
                posts_checked += 1
                print(f"Checking post #{posts_checked}")

                try:
                    # Get tweet text from this specific tweet element
                    tweet_text = tweet_element.text.lower()
                    
                    # Check if the tweet contains the target hashtag
                    if random_hashtag_filter.lower() not in tweet_text:
                        print(f"  Post #{posts_checked} doesn't contain #{random_hashtag_filter}, skipping...")
                        continue
                    
                    # Check if tweet has meaningful content
                    if not self._has_meaningful_content(tweet_element):
                        print(f"  ⏭ Skipping post #{posts_checked} - no meaningful content")
                        continue
                    
                    # Check if tweet has minimum engagement
                    if not self._has_minimum_engagement(tweet_element, min_likes=2, min_retweets=1):
                        print(f"  ⏭ Skipping post #{posts_checked} - low engagement")
                        continue
                    
                    print(f"  ✓ Found quality tweet with #{random_hashtag_filter}")
                    
                    # Find retweet button within this tweet
                    retweet_button = None
                    try:
                        retweet_button = tweet_element.find_element(By.CSS_SELECTOR, 'button[data-testid="retweet"]')
                    except:
                        print(f"  Could not find retweet button")
                        continue
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet_element)
                    self._human_like_delay(1, 2)
                    
                    # Click retweet
                    self.driver.execute_script("arguments[0].click();", retweet_button)
                    self._human_like_delay(2, 3)
                    
                    # Confirm retweet
                    try:
                        confirm_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="retweetConfirm"]'))
                        )
                        confirm_button.click()
                        retweet_count += 1
                        print(f"✓ Retweeted from followings #{retweet_count} (with #{random_hashtag_filter})")
                        self._human_like_delay(3, 6)
                    except:
                        print(f"  Could not confirm retweet")

                except Exception as e:
                    print(f"Error processing post #{posts_checked}: {e}")
            
            print(f"\n✓ Retweeted {retweet_count} posts from home feed\n")
                    
        except Exception as e:
            print(f"Error retweeting from followings: {e}")

    def close(self):
        """Closes the browser driver."""
        self.driver.quit()


if __name__ == "__main__":
    # Check for credentials setup argument
    if "--setup-credentials" in sys.argv:
        setup_credentials()
        sys.exit(0)
    
    # Check for headless mode argument
    headless_mode = "--headless" in sys.argv
    
    # IMPORTANT: Replace this with your actual Chrome profile path.
    # For Linux: ~/.config/google-chrome
    # For Windows: C:\Users\<Your-Username>\AppData\Local\Google\Chrome\User Data
    # For macOS: ~/Library/Application Support/Google/Chrome
    
    if sys.platform == "linux" or sys.platform == "linux2":
        CHROME_PROFILE_PATH = os.path.expanduser("~/.config/google-chrome")
    else:
        CHROME_PROFILE_PATH = r"C:\Users\Ali\AppData\Local\Google\Chrome\User Data\Default"

    try:
        bot = TwitterBot(chrome_profile_path=CHROME_PROFILE_PATH, headless=headless_mode)

        # Example usage:
        print("\n" + "="*70)
        print("STEP 1: Sending random tweets...")
        print("="*70)
        # 1. Send first tweet
        print("\n📝 Posting tweet #1...")
        bot.send_tweet()
        
        # Short break between tweets
        rest_time = random.uniform(30, 60)
        print(f"\nBrief pause for {int(rest_time)}s...")
        time.sleep(rest_time)
        
        # 2. Send second tweet
        print("\n📝 Posting tweet #2...")
        bot.send_tweet()
        
        # Rest period (simulate taking a break)
        rest_time = random.uniform(45, 90)
        print(f"\nTaking a break for {int(rest_time)}s (simulating human behavior)...")
        time.sleep(rest_time)

        print("\n" + "="*70)
        print("STEP 2: Interacting with hashtag posts...")
        print("="*70)
        # 2a. First hashtag - 40 interactions
        random_hashtag_1 = bot._get_random_hashtag()
        print(f"\n🔖 First hashtag for interaction: #{random_hashtag_1}")
        bot.interact_with_hashtag(random_hashtag_1, limit=40)
        
        # Brief pause between hashtags
        rest_time = random.uniform(30, 60)
        print(f"\nBrief pause for {int(rest_time)}s before next hashtag...")
        time.sleep(rest_time)
        
        # 2b. Second hashtag - 30 interactions
        random_hashtag_2 = bot._get_random_hashtag()
        # Make sure it's different from first one
        while random_hashtag_2 == random_hashtag_1:
            random_hashtag_2 = bot._get_random_hashtag()
        print(f"\n🔖 Second hashtag for interaction: #{random_hashtag_2}")
        bot.interact_with_hashtag(random_hashtag_2, limit=30)
        
        # Rest period (simulate taking a break)
        rest_time = random.uniform(60, 120)
        print(f"\nTaking a break for {int(rest_time)}s (simulating human behavior)...")
        time.sleep(rest_time)

        print("\n" + "="*70)
        print("STEP 3: Retweeting from followings (with random hashtag filter)...")
        print("="*70)
        # 3. Retweet posts from your followings/home feed that contain a random hashtag (limit: 20)
        bot.retweet_from_followings(limit=20)

        print("\n" + "="*70)
        print("✓ Automation finished successfully!")
        print("="*70)
        bot.close()
    except Exception as e:
        print(f"\n✗ ERROR during automation: {e}")
        import traceback
        traceback.print_exc()
                    