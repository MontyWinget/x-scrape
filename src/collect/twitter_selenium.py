"""
x_scraper.py

Selenium-based X (Twitter) scraper using Chrome for Testing.
Scrapes recent tweets related to Indian stock markets without
using the Twitter API.

IMPORTANT:
- Requires Chrome for Testing
- Requires manual login ONCE (cookies persist)
- Designed for robustness, not speed

NOTE:
Selenium-based scraping was implemented and tested using multiple Chrome variants
(Chrome 143, Chrome for Testing, and Chrome 120 standalone). Due to persistent
Chrome process creation failures on Windows, Selenium execution was disabled in
this environment. See README for detailed discussion.

"""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

from src.collect.queries import QUERIES

# -----------------------
# Config
# -----------------------

LOOKBACK_HOURS = 24
MAX_SCROLLS_PER_QUERY = 50
SCROLL_PAUSE = 2.5

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------
# Driver
# -----------------------

def get_driver():
    options = Options()

    # ✅ Standalone Chrome 120 binary
    options.binary_location = r"C:\chrome120\chrome.exe"

    # Chrome for Testing / standalone profile
    options.add_argument(
        r"--user-data-dir=C:\Users\marsh\AppData\Local\Google\Chrome for Testing\User Data"
    )
    options.add_argument("--profile-directory=Default")

    # Minimal stability flags
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-sync")
    options.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# -----------------------
# Tweet parsing
# -----------------------

def parse_tweet_element(tweet) -> Optional[Dict]:
    try:
        text_elem = tweet.find_elements(By.XPATH, ".//div[@data-testid='tweetText']")
        text = text_elem[0].text if text_elem else ""
        if not text:
            return None

        time_elem = tweet.find_elements(By.XPATH, ".//time")
        if not time_elem:
            return None

        created_at = time_elem[0].get_attribute("datetime")

        user_elem = tweet.find_elements(By.XPATH, ".//span[contains(text(), '@')]")
        username = user_elem[0].text if user_elem else None

        return {
            "tweet_id": None,  # X hides IDs in DOM
            "username": username,
            "text": text,
            "created_at": created_at,
            "scraped_at": datetime.utcnow().isoformat(),
        }

    except (StaleElementReferenceException, WebDriverException):
        return None


# -----------------------
# Scraping logic
# -----------------------

def scrape_query(driver, query: str) -> List[Dict]:
    print(f"\nScraping query: {query}")

    search_url = f"https://twitter.com/search?q={query}&f=live"
    driver.get(search_url)

    time.sleep(6)  # allow page to stabilize

    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    collected = []

    for scroll in range(MAX_SCROLLS_PER_QUERY):
        tweets = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")

        for tweet in tweets:
            data = parse_tweet_element(tweet)
            if not data:
                continue

            try:
                created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            except Exception:
                continue

            if created_at < cutoff:
                return collected

            data["query"] = query
            collected.append(data)

        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)

    return collected


# -----------------------
# Main entry
# -----------------------

def run():
    driver = get_driver()

    all_tweets: List[Dict] = []

    try:
        # Ensure login/session is valid
        driver.get("https://twitter.com/home")
        time.sleep(8)

        for query in QUERIES:
            tweets = scrape_query(driver, query)
            print(f"  Collected {len(tweets)} tweets")
            all_tweets.extend(tweets)

    finally:
        driver.quit()

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"tweets_raw_{ts}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_tweets, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(all_tweets)} tweets to {out_path}")


if __name__ == "__main__":
    run()
