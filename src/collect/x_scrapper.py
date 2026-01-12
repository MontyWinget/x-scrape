"""
Search queries for scraping Indian stock market related tweets from X.

These queries are intentionally conservative:
- Focused on indices and intraday trading
- Mix of hashtags and plain text
- Designed to reach >=2000 tweets in 24h window
"""

QUERIES = [
    # Core index hashtags (explicit in assignment)
    "#nifty50",
    "#sensex",
    "#banknifty",
    "#intraday",

    # Index names without hashtag (many traders don’t use #)
    "NIFTY",
    "BANKNIFTY",
    "SENSEX",

    # Trading-focused phrases
    "Indian stock market",
    "stock market India",
    "intraday trading India",

    # Optional but high-signal additions
    "FII DII",
    "market opening India",
    "market closing India"
]

# Optional: hard cap per query to avoid over-scraping one topic
MAX_TWEETS_PER_QUERY = 500
