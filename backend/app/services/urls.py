'''URL REPUTATION VIA GOOGLE SAFE BROWSINIGGGG'''

import httpx
from flask import current_app

from .rules import extract_urls


SAFE_BROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

def check_urls(text: str) -> dict:
    urls = list(dict.fromkeys(extract_urls(text)))[:50]
    if not urls:
        return {"checked" : 0, 
                "malicious": [],
                "safe": []}

    api_key = current_app.config["SAFE_BROWSING_API_KEY"]
    if not api_key:
        return {
            "checked":0,
            "malicious": [],
            "safe": urls,
            "note": "no_api_key"
        }
    payload = {
        "client": {"clientId": "aether", 
                   "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": u} for u in urls],
        },
    }
    try:
        r = httpx.post(SAFE_BROWSING_URL,
                        params={"key": api_key}, 
                        json=payload, 
                        timeout=8.0)
        
        r.raise_for_status()
        matches = r.json().get("matches", [])
        malicious = list({m["threat"]["url"] for m in matches})
        return {"checked": len(urls), "malicious": malicious,
                "safe": [u for u in urls if u not in malicious]}
    except Exception as e:
        # Log it here, but NEVER send the error to the client (it contains MYY key)
        current_app.logger.warning("Safe Browsing failed: %s",
                                    type(e).__name__)
        return {"checked": len(urls), 
                "malicious": [], 
                "safe": urls, 
                "note": "check_unavailable"}
    