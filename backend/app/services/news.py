# FETCHING BANK news via GOOGLE NEWS RSS will cache it for 1 hour

import re
from time import time
from urllib.parse import quote

import feedparser
import httpx

_cache: dict = {}

CACHE_TTL = 3600

def fetch_bank_news(bank_name: str, limit: int = 8) -> list[dict]:
    key = f"news:{bank_name.lower()}"
    if key in _cache and time() - _cache[key][0] < CACHE_TTL:
        return _cache[key][1]

    query = f'"{bank_name}" (fraud OR breach OR scam OR security)'
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        # feedparser has no timeout of its own okay? so fetching with httpx and like uh.... hand it the bytes
        resp = httpx.get(url, timeout=8.0, follow_redirects= True)
        feed = feedparser.parse(resp.content)

    except Exception:
        return _cache.get(key, (0, []))[1] 
    # something is better than nothing OKAY!!

    articles = [{
        "title": e.get("title", ""),
        "url": e.get("link", ""),
        "source": (e.get("source") or {}).get("title", ""),
        "published": e.get("published", ""),
        "summary": re.sub(r"<[^>]+>", "", e.get("summary", ""))[:300],
    } for e in feed.enteries[:limit]]

    if articles:
        _cache[key] = (time(), articles)

    return articles

