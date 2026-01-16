# Twitter Selenium Bot (no Developer API)

Install requirements:

```bash
pip install -r requirements.txt
```

Usage:

- Edit `twitter_bot.py` and set `USER_DATA_DIR` and (optionally) `PROFILE_DIR` to your Chrome profile path.
- Run the script: `python "twitter_bot.py"` and call the functions you need from the `__main__` block or import the module.

Finding your Chrome profile path:

- Windows:
  - Default user data folder: `C:\Users\<YourUser>\AppData\Local\Google\Chrome\User Data`
  - To find the exact profile, open Chrome and visit `chrome://version` and copy the `Profile Path` value (e.g., `C:\Users\You\AppData\Local\Google\Chrome\User Data\Default`).

- macOS:
  - Default user data folder: `~/Library/Application Support/Google/Chrome`
  - Open Chrome and visit `chrome://version` and copy the `Profile Path` (e.g., `/Users/you/Library/Application Support/Google/Chrome/Default`).

Notes and safety:

- This script uses your existing Chrome profile (via `--user-data-dir`) so existing sessions/cookies are reused — do not share your profile path.
- Human-like delays are implemented with `human_like_delay()` to reduce automated action speed.
- Each UI action is wrapped with try/except so the script continues if elements change or are missing.
- Selectors used: tweet box (`div[aria-label='Tweet text']` or `div[data-testid='tweetTextarea_0']`), like button (`[data-testid='like']`), retweet button (`[data-testid='retweet']`) and retweet confirm (`[data-testid='retweetConfirm']`).

Legal and account risk:

- Automating interactions on Twitter can violate its terms of service and may risk account suspension. Use responsibly and test on secondary accounts.
