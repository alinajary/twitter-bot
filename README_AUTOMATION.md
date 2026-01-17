# Twitter Bot - Automated Long-Term Operation Guide

## Summary
After the first manual login via VNC, the bot saves your session cookies and runs fully automatically on subsequent runs. No VNC or manual intervention needed.

## First-Time Setup (One Time Only)

1. **Start Xvfb and VNC** (if not already running):
   ```bash
   Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
   x11vnc -display :99 -forever -shared -bg -passwd twitter123
   ```

2. **Run the bot**:
   ```bash
   cd ~/twitter-bot
   source venv/bin/activate
   export DISPLAY=:99
   python3 twitter_bot.py --headless
   ```

3. **Connect via VNC from Windows**:
   - VNC Viewer to `135.181.89.177:5900`
   - Password: `twitter123`

4. **Log in with Google OAuth** in the Chrome window you see

5. **Press ENTER** in the SSH terminal where the bot is waiting

6. **Done!** The bot will save your cookies to `twitter_cookies_live.json`

## Subsequent Runs (Fully Automated)

Just run the bot normally:
```bash
cd ~/twitter-bot
source venv/bin/activate
export DISPLAY=:99
python3 twitter_bot.py --headless
```

No VNC or manual login needed! The bot loads your saved cookies automatically.

## Automated Scheduling with Cron

Run the bot every hour:
```bash
crontab -e
```

Add this line:
```
0 * * * * cd /root/twitter-bot && /root/twitter-bot/venv/bin/python3 twitter_bot.py --headless >> /root/twitter-bot/bot.log 2>&1
```

This runs at minute 0 of every hour (1:00 AM, 2:00 AM, etc.)

### Alternative Schedules

**Every 6 hours:**
```
0 */6 * * * cd /root/twitter-bot && /root/twitter-bot/venv/bin/python3 twitter_bot.py --headless >> /root/twitter-bot/bot.log 2>&1
```

**Twice daily (9 AM and 9 PM):**
```
0 9,21 * * * cd /root/twitter-bot && /root/twitter-bot/venv/bin/python3 twitter_bot.py --headless >> /root/twitter-bot/bot.log 2>&1
```

**Every 30 minutes:**
```
*/30 * * * * cd /root/twitter-bot && /root/twitter-bot/venv/bin/python3 twitter_bot.py --headless >> /root/twitter-bot/bot.log 2>&1
```

## Maintenance

### Check Bot Logs
```bash
tail -f /root/twitter-bot/bot.log
```

### Check if Xvfb/VNC are Running
```bash
ps aux | grep -E 'Xvfb|x11vnc'
```

### Restart Xvfb/VNC if Needed
```bash
pkill -9 Xvfb x11vnc
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
x11vnc -display :99 -forever -shared -bg -passwd twitter123
```

### If Cookies Expire (Session Lost)

X/Twitter sessions can expire after weeks/months. If this happens:

1. Check logs for "NOT LOGGED IN" errors
2. Run bot manually with VNC again (follow First-Time Setup)
3. The bot will save fresh cookies automatically

### Stop VNC After First Setup

Once `twitter_cookies_live.json` is saved, you can stop VNC to save resources:
```bash
pkill x11vnc
```

**Keep Xvfb running** - the bot needs it even without VNC.

## Troubleshooting

### Bot says "NOT LOGGED IN - redirected to login page"

**Solution:** Cookies expired. Re-run First-Time Setup to log in again via VNC.

### Chrome crashes or "cannot connect to chrome"

**Solution:** 
```bash
pkill -9 chrome chromium
# Restart Xvfb if needed
pkill -9 Xvfb
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
```

### "DISPLAY not set" error

**Solution:** Make sure to export DISPLAY before running:
```bash
export DISPLAY=:99
```

Or add it to your cron job as shown above.

## Security Notes

1. **VNC Password:** Change `twitter123` to something secure if your server is exposed
2. **Firewall:** Block port 5900 externally after first setup:
   ```bash
   ufw deny 5900/tcp
   ```
3. **Cookies:** The `twitter_cookies_live.json` contains your session - keep it secure (0600 permissions)
4. **Logs:** Rotate logs periodically to avoid filling disk space

## Expected Behavior

**Step 1:** Posts 1 random tweet with 3 random hashtags  
**Step 2:** Searches random hashtag, likes/retweets 20 posts  
**Step 3:** Browses followings feed, retweets 10 posts matching Iran hashtags  

**Total runtime:** ~10-15 minutes per execution  
**Human-like delays:** 5-15 seconds between actions, random 30-60s pauses

## Cookie Lifespan

- **Google OAuth sessions:** Usually last 30-90 days
- **Bot will continue working until session expires**
- **When expired:** You'll see login page in logs, just re-run First-Time Setup once

## Files Created

- `twitter_cookies_live.json` - Your working session cookies (auto-created after first login)
- `bot.log` - Execution logs (if using cron with log redirect)
- `~/.config/google-chrome/` - Chrome profile data used by undetected_chromedriver

## Long-Term Stability Tips

1. **Monitor logs weekly** - Check for errors or session expiration
2. **Don't run too frequently** - Hourly is safe, every 10 minutes might trigger rate limits
3. **Vary your schedule** - Random times look more human than fixed intervals
4. **Keep server updated** - `apt update && apt upgrade` monthly
5. **Backup cookies** - Copy `twitter_cookies_live.json` somewhere safe after successful login

## Need to Switch Accounts?

1. Delete `twitter_cookies_live.json`
2. Run First-Time Setup again
3. Log in with different account via VNC
4. New cookies will be saved automatically
