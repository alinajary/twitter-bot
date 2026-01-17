# Twitter Bot Strategy & Implementation

## Overview
Automated Twitter bot that posts tweets, engages with hashtag content, and retweets posts from followings. Designed to prioritize high-quality, high-engagement content while maintaining human-like behavior.

## Core Features

### 1. Tweet Posting
- Posts 2 random tweets per run
- Selects from 103 pre-written variations (emojis removed for ChromeDriver compatibility)
- Adds 2-4 random hashtags per tweet
- Simulates human reading delays (30-60s) before posting

### 2. Hashtag Interactions
- **Target**: 70 total interactions per run
  - 40 interactions for first hashtag
  - 30 interactions for second hashtag
- Randomly selects 2 hashtags from pool of 12

### 3. Followings Retweets
- **Target**: 20 retweets per run
  - 70% from targeted accounts (specific users you follow)
  - 30% from general home feed

## Critical Strategy: TOP vs LATEST Feed

### The Problem
Twitter has two main search feeds:
- **LATEST** (`f=live`): Shows newest posts chronologically, regardless of engagement
- **TOP** (`f=top`): Shows popular posts with high engagement (likes, retweets)

**Previous Issue**: Bot was randomly choosing between feeds (50/50 chance), often searching Latest where most posts have 0-2 likes. This meant missing high-engagement posts (100+ likes, 40+ retweets) that appear in Top feed.

### The Solution
**New Strategy (January 2026)**:
1. **Always search TOP feed first** to capture high-engagement content
2. **Supplement with LATEST if needed** - if Top doesn't provide enough recent tweets (< target count)
3. **Merge results** - combine both feeds, removing duplicates

```python
# Priority Flow:
TOP feed (f=top) → High-engagement posts (157 likes, 45 retweets, etc.)
   ↓ (if insufficient)
LATEST feed (f=live) → Fresh content backup
   ↓
Merged results → Best of both worlds
```

### Why This Matters
- **Visibility**: Top posts are seen by more users (trending content)
- **Credibility**: Engaging with popular posts increases bot's legitimacy
- **Network Effect**: High-engagement posts have active conversations
- **Targeted Reach**: These posts align with movement's goals (Iran freedom)

## Engagement Prioritization System

### Three-Tier Classification

#### Tier 1: HIGH ENGAGEMENT
- **Criteria**: ≥10 likes OR ≥5 retweets
- **Priority**: Interact with these first
- **Typical Source**: TOP feed

#### Tier 2: MEDIUM ENGAGEMENT
- **Criteria**: ≥2 likes OR ≥1 retweet
- **Priority**: Secondary choice if high-engagement unavailable
- **Typical Source**: TOP feed or recent LATEST

#### Tier 3: LOW ENGAGEMENT
- **Criteria**: Any engagement (1 like or 1 retweet)
- **Priority**: Fallback option
- **Typical Source**: LATEST feed

### Engagement Scoring Formula
```python
score = likes + (retweets × 2)
```
Retweets weighted 2x because they amplify reach more than likes.

## Content Quality Filtering

### Meaningful Content Check
Tweets must have ≥20 characters of actual text after removing:
- Hashtags (#FreeIran, etc.)
- Mentions (@username)
- URLs (http://...)

**Purpose**: Avoid interacting with spam or hashtag-only posts like:
```
❌ #FreeIran #Iran #KingRezaPahlavi
✅ The people of Iran demand freedom and democracy #FreeIran
```

### Recent Posts Filter
Only interact with posts from **last 48 hours**:
- Ensures relevance
- Avoids old/stale conversations
- Maintains active engagement patterns

## Technical Implementation

### Engagement Parsing
Extracts like/retweet counts from Twitter's DOM:

```python
# Find buttons
like_button = tweet.find_element(By.CSS_SELECTOR, 'button[data-testid="like"]')
retweet_button = tweet.find_element(By.CSS_SELECTOR, 'button[data-testid="retweet"]')

# Parse aria-label
# Examples: "157 Likes", "45 Retweets", "1.2K Likes", "3.5M Retweets"
aria_label = like_button.get_attribute('aria-label')

# Regex extraction handles K/M suffixes
numbers = re.findall(r'([\d,\.]+[KkMm]?)', aria_label)
```

### Batch Collection Strategy
1. **Scroll & Collect**: 5 scroll iterations, collect all `<article data-testid="tweet">` elements
2. **Filter by Time**: Parse timestamps, keep only 48h recent
3. **Filter by Content**: Check for meaningful text (≥20 chars)
4. **Parse Engagement**: Extract likes/retweets from buttons
5. **Sort & Prioritize**: Group by engagement tier
6. **Select & Interact**: Choose best tweets, like + retweet

### Anti-Stale Element Protection
Twitter's infinite scroll can make elements stale. Solution:
- Collect all WebElements in batch first
- Process immediately before page changes
- Handle stale element exceptions gracefully

## Workflow Example

### Run Sequence
```
1. Start Chrome with user profile (logged in session)
2. Auto-login verification (skip if already logged in)
3. Post 2 tweets (30-60s delays between)
4. Wait 60s (simulate human browsing)
5. Hashtag #1 (e.g., #FreeIran):
   a. Search TOP feed
   b. Collect 120+ tweets
   c. Filter to 48h recent
   d. Check content quality
   e. Parse engagement
   f. Prioritize high → medium → low
   g. Interact with 40 tweets
6. Wait 30-60s
7. Hashtag #2 (e.g., #KingRezaPahlavi):
   a. Same process
   b. Interact with 30 tweets
8. Wait 30-60s
9. Followings retweets:
   a. Visit 70% targeted accounts (14 retweets)
   b. Visit home feed for 30% (6 retweets)
   c. Total: 20 retweets
10. Done - exit cleanly
```

### Human-Like Delays
- **Reading time**: 30-60s random per tweet
- **Action delays**: 2-5s between like and retweet
- **Between tweets**: 2-4s pause
- **Between sections**: 30-60s break

## Server Deployment

### Hetzner Ubuntu Server
- **IP**: 135.181.89.177
- **Path**: `/root/twitter-bot/`
- **Python**: 3.11
- **Chrome**: Chromium with undetected-chromedriver
- **Display**: Xvfb virtual display (headless mode)

### Cron Schedule
```bash
# Every 6 hours
0 */6 * * * cd /root/twitter-bot && /usr/bin/python3 twitter_bot.py --headless=true >> /var/log/twitter-bot.log 2>&1
```

**Times** (UTC):
- 00:00 (midnight)
- 06:00 (morning)
- 12:00 (noon)
- 18:00 (evening)

### Session Persistence
- Uses cookies saved in `twitter_cookies_live.json`
- Auto-login with saved credentials
- No manual intervention needed

## Configuration Files

### tweets.txt
- 103 tweet variations
- All emojis removed (ChromeDriver incompatibility)
- Focus: Iran freedom movement
- Format: One tweet per line

### hashtags.txt
- 12 hashtags
- Format: One hashtag per line (no # symbol)
- Examples: FreeIran, IranRevolution2026, KingRezaPahlavi

### credentials.json
- Encrypted Twitter login credentials
- Auto-generated by credentials_manager.py
- Used for auto-login on server

## Performance Metrics

### Per Run (Every 6 Hours)
- **Tweets Posted**: 2
- **Hashtag Interactions**: 70 (40 + 30)
- **Followings Retweets**: 20
- **Total Actions**: 92 per run

### Daily (4 Runs)
- **Tweets Posted**: 8
- **Hashtag Interactions**: 280
- **Followings Retweets**: 80
- **Total Actions**: 368 per day

### Engagement Quality (With TOP Feed Strategy)
- **High-Engagement**: 60-80% of interactions (≥10 likes or ≥5 retweets)
- **Medium-Engagement**: 15-30% of interactions (≥2 likes or ≥1 retweet)
- **Low-Engagement**: 5-10% fallback (any engagement)

## Recent Changes

### January 17, 2026
**Issue Identified**: Bot was searching LATEST feed, finding posts with 0-2 likes, while TOP feed had posts with 100+ likes.

**Changes Made**:
1. ✅ **Always prioritize TOP feed** - `f=top` parameter for high-engagement posts
2. ✅ **Fallback to LATEST** - supplements if TOP has insufficient recent tweets
3. ✅ **Merge strategy** - combines both feeds, removes duplicates by partial HTML comparison
4. ✅ **Debug logging** - added engagement detection debug output

**Expected Impact**:
- Higher quality interactions (engaging with popular posts)
- Better visibility (comments on trending tweets)
- Increased credibility (associated with high-engagement content)
- More effective reach (participating in active conversations)

## Troubleshooting

### Common Issues

#### 1. Bot finds 0 qualifying tweets
**Cause**: Searching wrong feed (Latest instead of Top)
**Fix**: Ensure TOP feed search is implemented (updated Jan 2026)

#### 2. Stale element errors during interactions
**Cause**: Page changed after batch collection
**Fix**: Collect all elements first, process immediately, handle exceptions

#### 3. Engagement parsing returns (0, 0)
**Cause**: Wrong CSS selectors or aria-label format
**Fix**: Check button selectors, verify aria-label format (could be localized)

#### 4. Chrome won't start on Windows
**Cause**: Unicode characters in print statements (PowerShell encoding)
**Fix**: Set `$env:PYTHONIOENCODING="utf-8"` before running

## Future Enhancements

### Potential Improvements
1. **Adaptive thresholds** - adjust engagement criteria based on hashtag popularity
2. **Time-based weighting** - prefer posts from last 6 hours over 48 hours
3. **Reply functionality** - add meaningful replies to high-engagement posts
4. **Sentiment analysis** - verify post alignment with movement goals
5. **Multi-account support** - rotate between accounts for broader reach
6. **Analytics dashboard** - track engagement metrics over time

### Risk Mitigation
- **Rate limiting**: Stay within Twitter's automation policies
- **Randomization**: Vary timing, order, and selection to avoid patterns
- **Human-like delays**: Mimic natural browsing behavior
- **Content quality**: Only engage with meaningful, relevant posts
- **Account safety**: Use cookies and avoid suspicious patterns

## Contact & Support

For issues or questions:
- Check logs: `/var/log/twitter-bot.log` (server) or terminal output (local)
- Verify Chrome is running: `ps aux | grep chrome`
- Test engagement parsing: Check debug output during hashtag interactions
- Review this documentation: `STRATEGY.md`

---

**Last Updated**: January 17, 2026  
**Version**: 2.0 (TOP Feed Priority Update)
