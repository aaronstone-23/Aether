"""Deterministic (non-LLM scam rules). Always run first"""
import re

from .brands import brand_in_host, host_of

URGENCY_PHRASES = [
    "urgent", "immediately", "act now", "within 24 hours", "last warning", "account will be suspended", "account will be closed", "account will be blocked", "will be blocked", "update kyc", "kyc update", "final notice", "verify now", "click here", "limited time", "expires today",
]
PAYMENT_PHRASES = [
    "upi", "bank transfer", "wire transfer", "pay", "payment", 
    "processing fee", "refund", "send money", "gift card", 
    "bitcoin", "crypto", "western union"
]
SECRECY_PHRASES = [
    "do not tell", "keep this confidential", "don't share with anyone", "between us", "do not inform"
]
WIN_PHRASES = [
    "you have won", "lottery", "prize", "selected winner",
    "claim your", "congratulates you"
]
SUSPICIOUS_TLDS= (".xyz", ".top", ".click", "tk", ".ml", ".ga", ".cf", ".gq", ".zip")
SHORTERNERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rb.gy", "shorturl.at"}


def _compile(phrases):
    # \b = whole-word match, so "upi" no longer matches "stupid"
    return[(p, re.compile(r"\b" + re.escape(p)+ r"\b", re.I)) for p in phrases]

_PATTERNS = {
    "urgency": _compile(URGENCY_PHRASES),
    "payment": _compile(PAYMENT_PHRASES),
    "secrecy": _compile(SECRECY_PHRASES),
    "win": _compile(WIN_PHRASES),
}

WEIGHTS = {"urgency":8,
           "payment": 6,
           "secrecy": 15,
           "win": 12,
           "lookalike": 25,
           "tld": 10,
           "shortener": 8, 
           "ip_host":15,
           "upi":5}

LABELS = {
    "urgency":"Pressure or urgency language", "payment":"Mentions payments or money transfer",
    "secrecy": "Asks you to keep it secret", "win": "Prize or lottery claim",
    "lookalike":"Link imitates a known brand", "tld": "Link uses a domain type common in scams",
    "shortener":"Shortened link hides the real destination",
    "ip_host": "Link points to a raw IP address", 
    "upi": "Contains a UPI ID",
}

def extract_urls(text: str)-> list[str]:
    urls= re.findall(r"https?://[^\s<>\"']+", text)
    return [u.rstrip(".,);:!?]") for u in urls]

def extract_phones(text: str)-> list[str]:
    return re.findall(r"\+?\d[\d\s\-()]{8,}\d", text)

def extract_upi_ids(text:str)-> list[str]:
     # name@handle with no ".com" after it (that would be an email address)
     return re.findall(r"\b[\w.\-]{2,}@[a-zA-Z]{2,20}\b(?!\.[a-zA-Z])", text)

def analyse_links(urls: list[str]) -> dict:
    out = {"lookalike":[],
           "tld":[], 
           "shortener":[],
           "ip_host":[]
           }
    for u in urls:
        host = host_of(u)
        if not host:
            continue
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
            out["ip_host"].append(host)
        if host in SHORTERNERS:
            out["shortener"].append(host)
        if host.endswith(SUSPICIOUS_TLDS):
            out["tld"].append(host)
        brand = brand_in_host(host)
        if brand:
            out["lookalike"].append(f"{host} (imitates {brand})")
    return out

def score_text(text: str) -> dict:
     # Returns nice format from a blob of text
    matches = {k: [p for p, rx in pats if rx.search(text)] for k, pats in _PATTERNS.items()}
    matches.update(analyse_links(extract_urls(text)))
    matches["upi"] = extract_upi_ids(text)
    score = sum(min(len(matches[k]), 3) * w for k, w in WEIGHTS.items())
    return {"score": min(score, 60), "matches": matches}

def describe_matches(matches: dict) -> list[str]:
    return [f"{LABELS[k]}: {', '.join(map(str, v[:3]))}"
            for k, v in matches.items() if v and k in LABELS]

def verdict_from_score(score: int) -> tuple[str, str]:
    if score >= 70:
        return "fake", "high"
    if score >= 40:
        return "suspicious", "medium"
    return "likely_legit", "low"

def build_actions(verdict:str) -> list[str]:
    if verdict == "fake":
        return ["Do not click any links", "Do not reply or share OTP",
                "Report it (cybercrime.gov.in, or call 1930 if money is involved)", "If you entered credentials, change your password immediately"]
    if verdict == "suspicious":
        return ["Verify the sender through an official channel",
                "Do not click links until verified", "Contact your bank using the number on your card or official site"]
    return ["No immediate red flags found. Stay alert."]
    
    