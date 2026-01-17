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
            options.add_argument(f'--user-data-dir={chrome_profile_path}')
            
            # Set virtual display for Xvfb
            os.environ['DISPLAY'] = ':99'
            
            try:
                # Use system chromedriver with UC (removed use_subprocess=False)
                self.driver = uc.Chrome(
                    options=options, 
                    driver_executable_path="/usr/bin/chromedriver"
                )
                self.wait = WebDriverWait(self.driver, 20)
                print("✓ Successfully started undetected Chrome with virtual display!")
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

    def send_tweet(self, text=None):
        """
        Posts a new tweet.

        Args:
            text (str): The content of the tweet. If None, uses a random tweet from tweets.txt
        """
        # Use random tweet if not specified
        if text is None:
            text = self._get_random_tweet()
        
        # Add random hashtags to the tweet
        random_hashtags = random.sample(self.hashtags, min(3, len(self.hashtags)))
        hashtag_string = " ".join([f"#{tag}" for tag in random_hashtags])
        full_tweet = f"{text} {hashtag_string}"
        
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
            self.driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]').send_keys(full_tweet)
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

    def interact_with_hashtag(self, hashtag, limit=10):
        """
        Searches for a hashtag, then likes and retweets a specific number of posts.

        Args:
            hashtag (str): The hashtag to search for (without the '#').
            limit (int): The maximum number of posts to interact with.
        """
        try:
            search_url = f"https://x.com/search?q={hashtag}&src=typed_query"
            self.driver.get(search_url)
            self._human_like_delay(3, 5)

            for i in range(limit):
                try:
                    # Random chance to scroll before liking (human behavior)
                    if random.random() < 0.3:
                        self.driver.execute_script("window.scrollBy(0, 200);")
                        self._human_like_delay(1, 3)
                    
                    # Like the tweet - try multiple selector strategies
                    like_button = None
                    like_selectors = [
                        'button[data-testid="like"]',
                        '[data-testid="like"]',
                        'button[aria-label*="Like"]',
                        'div[data-testid="like"]',
                    ]
                    
                    for selector in like_selectors:
                        try:
                            like_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                            print(f"Found like button with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if not like_button:
                        print(f"Could not find like button for tweet #{i+1}")
                        self.driver.execute_script("window.scrollBy(0, 300);")
                        self._human_like_delay(2, 4)
                        continue
                    
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", like_button)
                    self._human_like_delay(1, 2)
                    # Use JavaScript click to avoid interception
                    self.driver.execute_script("arguments[0].click();", like_button)
                    print(f"✓ Liked tweet #{i+1} for hashtag '{hashtag}'")
                    self._human_like_delay(2, 5)

                    # Random chance to skip retweet (more human-like)
                    if random.random() < 0.9:
                        # Retweet the tweet
                        retweet_button = None
                        retweet_selectors = [
                            'button[data-testid="retweet"]',
                            '[data-testid="retweet"]',
                            'button[aria-label*="Retweet"]',
                            'div[data-testid="retweet"]',
                        ]
                        
                        for selector in retweet_selectors:
                            try:
                                retweet_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                                print(f"Found retweet button with selector: {selector}")
                                break
                            except:
                                continue
                        
                        if not retweet_button:
                            print(f"Could not find retweet button for tweet #{i+1}")
                            self.driver.execute_script("window.scrollBy(0, 300);")
                            self._human_like_delay(2, 4)
                        else:
                            # Scroll element into view
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", retweet_button)
                            self._human_like_delay(1, 2)
                            # Use JavaScript click to avoid interception
                            self.driver.execute_script("arguments[0].click();", retweet_button)
                            self._human_like_delay(2, 4)
                            
                            # Confirm retweet - try multiple selectors and give more time
                            confirm_selectors = [
                                'button[data-testid="retweetConfirm"]',
                                'button[data-testid="confirmationSheetConfirm"]',
                                '[data-testid="retweetConfirm"]',
                                'button:has-text("Retweet")',
                                'div[role="dialog"] button[data-testid*="Confirm"]',
                            ]
                            
                            confirm_retweet = None
                            for selector in confirm_selectors:
                                try:
                                    # Wait longer for dialog to appear
                                    confirm_retweet = WebDriverWait(self.driver, 5).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                    print(f"Found confirm button with selector: {selector}")
                                    break
                                except:
                                    continue
                            
                            if confirm_retweet:
                                try:
                                    confirm_retweet.click()
                                    print(f"✓ Retweeted tweet #{i+1} for hashtag '{hashtag}'")
                                except:
                                    # Try JavaScript click as fallback
                                    self.driver.execute_script("arguments[0].click();", confirm_retweet)
                                    print(f"✓ Retweeted tweet #{i+1} for hashtag '{hashtag}'")
                            else:
                                print(f"Could not confirm retweet for tweet #{i+1} - dialog didn't appear")
                            
                            self._human_like_delay(2, 5)

                    # Scroll down to the next tweet with variable distance
                    scroll_amount = random.randint(400, 800)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    self._human_like_delay(3, 7)

                except Exception as e:
                    print(f"Could not interact with tweet #{i+1}: {e}")
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    self._human_like_delay(2, 4)
        except Exception as e:
            print(f"Error interacting with hashtag {hashtag}: {e}")

    def retweet_from_followings(self, limit=10):
        """
        Retweets posts from your followings that contain a random hashtag.

        Args:
            limit (int): The maximum number of posts to retweet.
        """
        try:
            # Go to home feed
            self.driver.get("https://x.com/home")
            self._human_like_delay(3, 5)

            retweet_count = 0
            posts_checked = 0
            for i in range(limit * 5):  # Try more times to find posts
                if retweet_count >= limit:
                    break
                
                posts_checked += 1
                
                # Select a new random hashtag for each post
                random_hashtag_filter = self._get_random_hashtag()
                print(f"Checking post #{posts_checked} with hashtag filter: #{random_hashtag_filter}")

                try:
                    # Random chance to scroll before retweeting
                    if random.random() < 0.4:
                        self.driver.execute_script("window.scrollBy(0, 200);")
                        self._human_like_delay(1, 3)
                    
                    # Get the current tweet text to check for hashtag
                    try:
                        tweet_text = self.driver.execute_script("""
                            const tweet = document.querySelector('[data-testid="tweet"]');
                            if (tweet) {
                                return tweet.innerText;
                            }
                            return '';
                        """)
                    except:
                        tweet_text = ""
                    
                    # Check if the tweet contains the target hashtag
                    if random_hashtag_filter.lower() not in tweet_text.lower():
                        print(f"Post #{posts_checked} doesn't contain #{random_hashtag_filter}, skipping...")
                        self.driver.execute_script("window.scrollBy(0, 300);")
                        self._human_like_delay(2, 4)
                        continue
                    
                    # Find retweet buttons
                    retweet_selectors = [
                        'button[data-testid="retweet"]',
                        '[data-testid="retweet"]',
                        'button[aria-label*="Retweet"]',
                    ]
                    
                    retweet_button = None
                    for selector in retweet_selectors:
                        try:
                            retweet_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                            break
                        except:
                            continue
                    
                    if not retweet_button:
                        print(f"No more posts found, stopping.")
                        break
                    
                    # Check if the post is already retweeted (skip if already retweeted)
                    retweet_label = retweet_button.get_attribute('aria-label')
                    if retweet_label and 'Undo' in retweet_label:
                        print(f"Post #{posts_checked} already retweeted, skipping...")
                        self.driver.execute_script("window.scrollBy(0, 300);")
                        self._human_like_delay(2, 4)
                        continue
                    
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", retweet_button)
                    self._human_like_delay(1, 2)
                    
                    # Use JavaScript click to avoid interception
                    self.driver.execute_script("arguments[0].click();", retweet_button)
                    self._human_like_delay(1, 3)
                    
                    # Confirm retweet
                    try:
                        confirm_selectors = [
                            '[data-testid="retweetConfirm"]',
                            'button[data-testid="retweetConfirm"]',
                        ]
                        confirm_retweet = None
                        for selector in confirm_selectors:
                            try:
                                confirm_retweet = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                                break
                            except:
                                continue
                        
                        if confirm_retweet:
                            confirm_retweet.click()
                            print(f"✓ Retweeted from followings #{retweet_count + 1} (with #{hashtag_filter})")
                            retweet_count += 1
                    except:
                        print(f"Could not confirm retweet #{retweet_count + 1}")
                    
                    self._human_like_delay(3, 6)

                    # Scroll down to the next tweet
                    scroll_amount = random.randint(400, 800)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    self._human_like_delay(3, 7)

                except Exception as e:
                    print(f"Error processing post #{posts_checked}: {e}")
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    self._human_like_delay(2, 4)
                    
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
        print("STEP 1: Sending a random tweet...")
        print("="*70)
        # 1. Send a random tweet from tweets.txt (with random hashtags appended)
        bot.send_tweet()
        
        # Rest period (simulate taking a break)
        rest_time = random.uniform(45, 90)
        print(f"\nTaking a break for {int(rest_time)}s (simulating human behavior)...")
        time.sleep(rest_time)

        print("\n" + "="*70)
        print("STEP 2: Interacting with hashtag posts...")
        print("="*70)
        # 2. Interact with a random hashtag from hashtags.txt (limit: 20)
        random_hashtag = bot._get_random_hashtag()
        print(f"Selected hashtag for interaction: #{random_hashtag}")
        bot.interact_with_hashtag(random_hashtag, limit=20)
        
        # Rest period (simulate taking a break)
        rest_time = random.uniform(60, 120)
        print(f"\nTaking a break for {int(rest_time)}s (simulating human behavior)...")
        time.sleep(rest_time)

        print("\n" + "="*70)
        print("STEP 3: Retweeting from followings (with random hashtag filter)...")
        print("="*70)
        # 3. Retweet posts from your followings/home feed that contain a random hashtag (limit: 10)
        bot.retweet_from_followings(limit=10)

        print("\n" + "="*70)
        print("✓ Automation finished successfully!")
        print("="*70)
        bot.close()
    except Exception as e:
        print(f"\n✗ ERROR during automation: {e}")
        import traceback
        traceback.print_exc()
                    