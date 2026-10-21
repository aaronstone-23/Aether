"""Deterministic (non-LLM scam rules). Always run first"""
import re

from .brands import BRAND_DOMAINS, brand_in_host, host_of

URGENCY_PHRASES = [
    "urgent", "immediately", "act now", "act immediately", "within 24 hours",
    "last warning", "final warning", "account will be suspended",
    "account will be closed", "account will be blocked", "will be blocked",
    "update kyc", "kyc update", "final notice", "verify now", "click here",
    "limited time", "expires today", "expires soon", "right away",
    "failure to act", "last chance",
]
PAYMENT_PHRASES = [
    "upi", "bank transfer", "wire transfer", "pay", "payment", 
    "processing fee", "refund", "send money", "gift card", 
    "bitcoin", "crypto", "western union"
]
SECRECY_PHRASES = [
    "do not tell", "keep this confidential", "don't share with anyone",
    "between us", "do not inform", "keep this between us"
]
WIN_PHRASES = [
    "you have won", "you've won", "you are a winner", "lottery", "prize",
    "selected winner", "selected to win", "claim your", "congratulations",
    "congratulates you"
]
SUSPICIOUS_TLDS = (".xyz", ".top", ".click", ".tk", ".ml", ".ga", ".cf", ".gq", ".zip")
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

_URL_RE = re.compile(
    r"""(?ix)\b(?:
        https?://[^\s<>"']+
        | www\.[^\s<>"']+
        | (?<![@\w.-])(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}
          (?::\d{1,5})?(?:/[^\s<>"']*)?
    )"""
)

WEIGHTS = {
    "urgency": 8, "payment": 3, "secrecy": 20, "win": 15,
    "lookalike": 40, "tld": 20, "shortener": 20, "ip_host": 30, "upi": 12,
    "link_present": 18, "credential_request": 60, "account_threat": 35,
    "link_action": 30, "financial_request": 40, "remote_access": 50,
    "advance_fee": 35, "authority_claim": 20,
}

LABELS = {
    "urgency":"Pressure or urgency language", "payment":"Mentions payments or money transfer",
    "secrecy": "Asks you to keep it secret", "win": "Prize or lottery claim",
    "lookalike":"Link imitates a known brand", "tld": "Link uses a domain type common in scams",
    "shortener":"Shortened link hides the real destination",
    "ip_host": "Link points to a raw IP address", 
    "upi": "Contains a UPI ID",
    "link_present": "Contains a link whose destination should be checked",
    "credential_request": "Requests a password, OTP, identity, or financial details",
    "account_threat": "Threatens to suspend, block, or close an account",
    "link_action": "Pairs a link with a call to action",
    "financial_request": "Requests a payment or transfer",
    "remote_access": "Requests remote access or screen sharing",
    "advance_fee": "Requests an advance fee for a job or opportunity",
    "authority_claim": "Claims to represent an institution while requesting action",
}

def extract_urls(text: str) -> list[str]:
    """Find explicit, www, and bare domain links without treating email addresses as links."""
    urls = _URL_RE.findall(text or "")
    return [url.rstrip(".,);:!?]}>") for url in urls]

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


_SENSITIVE_TERMS = (
    r"(?:one[\s-]?time(?:\s+(?:password|passcode|code))?|otp|password|passcode|"
    r"pin(?:\s+code)?|cvv|cvc|security\s+code|verification\s+code|"
    r"(?:four|six|eight|4|6|8)[ -]?digit(?:\s+verification)?\s+code|"
    r"card\s+(?:details|number)|bank\s+(?:details|account(?:\s+number)?)|"
    r"account\s+number|credentials|aadhaar|aadhar|pan(?:\s+card)?|"
    r"social\s+security\s+number|passport(?:\s+number)?|"
    r"identity\s+(?:document|number|details)|date\s+of\s+birth)"
)
_REQUEST_VERBS = (
    r"(?:ask(?:ing)?(?:\s+you)?\s+for|request(?:ing)?(?:\s+you)?\s+for|"
    r"need|require|collect|obtain|share|send|text|email|provide|submit|enter|"
    r"type|reply\s+(?:with|to)|give|tell|read(?:\s+out)?|upload|disclose|"
    r"supply|confirm|verify|validate|forward)"
)
_SENSITIVE_REQUEST_RE = re.compile(
    r"\b" + _REQUEST_VERBS + r"\b[\w\s,:.'-]{0,60}\b(?:your\s+)?"
    + _SENSITIVE_TERMS + r"\b",
    re.I,
)
_SENSITIVE_ACTION_AFTER_RE = re.compile(
    r"\b" + _SENSITIVE_TERMS + r"\b[\w\s,:.'-]{0,45}\b"
    r"(?:send|text|email|share|forward|reply|read|tell|provide|enter|submit)\b",
    re.I,
)
_NEGATED_REQUEST_RE = re.compile(
    r"\b(?:never|don't|do not|doesn't|does not|won't|will not|"
    r"shouldn't|should not|cannot|can't|avoid|without)\b[\w\s,:.'-]{0,70}$",
    re.I,
)
_ACCOUNT_THREAT_RE = re.compile(
    r"\b(?:your\s+)?(?:bank\s+)?(?:account|card|access|service|wallet)\b"
    r"[\w\s,:.'-]{0,40}\b(?:suspend\w*|block\w*|clos\w*|terminat\w*|"
    r"restrict\w*|deactivat\w*|lock\w*)\b"
    r"|\b(?:suspend\w*|block\w*|clos\w*|terminat\w*|restrict\w*|"
    r"deactivat\w*|lock\w*)\b[\w\s,:.'-]{0,35}"
    r"\b(?:your\s+)?(?:account|card|access|service|wallet)\b",
    re.I,
)
_LINK_ACTION_RE = re.compile(
    r"\b(?:click|tap|visit|open|follow|go\s+to|review|track|claim|download|"
    r"install|continue)\b"
    r"|\b(?:login|log\s+in|sign\s+in|verify|update|confirm|restore|unlock|"
    r"renew|submit|complete|reset|"
    r"check)\b[\w\s,:.'-]{0,40}\b(?:your\s+)?"
    r"(?:account|bank\s+details|card|details|identity|credentials|kyc|password|otp)\b",
    re.I,
)
_SENSITIVE_LINK_ACTION_RE = re.compile(
    r"\b(?:login|log\s+in|sign\s+in|verify|update|confirm|restore|unlock|"
    r"renew|submit|complete|reset|enter|provide)\b[\w\s,:.'-]{0,40}\b"
    r"(?:account|identity|kyc|password|otp|card|bank\s+details|credentials)\b"
    r"|\b(?:account|identity|kyc|password|otp|card|bank\s+details|credentials)\b"
    r"[\w\s,:.'-]{0,40}\b(?:login|log\s+in|sign\s+in|verify|update|confirm|"
    r"restore|unlock|renew|submit|complete|reset|enter|provide)\b",
    re.I,
)
_KYC_ACTION_RE = re.compile(
    r"\b(?:update|renew|complete|submit|verify)\b[\w\s,:.'-]{0,40}\bkyc\b"
    r"|\bkyc\b[\w\s,:.'-]{0,40}\b(?:update|renew|complete|submit|verify)\b",
    re.I,
)
_FINANCIAL_REQUEST_RE = re.compile(
    r"\b(?:send|transfer|wire|pay|deposit|purchase|buy|load|top\s+up)\b"
    r"[\w\s,:.'-]{0,45}\b(?:money|payment|funds|fee|deposit|gift\s+cards?|"
    r"vouchers?|bitcoin|crypto(?:currency)?|upi|bank\s+account)\b"
    r"|\b(?:processing|verification|release|claim|registration|application|"
    r"training|customs|delivery|activation|clearance)\s+(?:fee|charge|deposit)\b"
    r"|\b(?:fee|charge|deposit)\b[\w\s,:.'-]{0,35}"
    r"\b(?:release|claim|prize|job|offer|package|parcel|account|refund)\b",
    re.I,
)
_REMOTE_ACCESS_RE = re.compile(
    r"\b(?:install|download|open|use|connect|allow|grant|share|start)\b"
    r"[\w\s,:.'-]{0,55}\b(?:anydesk|teamviewer|quick\s*support|quicksupport|"
    r"rustdesk|remote\s+access|screen\s*share|screen\s*sharing)\b"
    r"|\b(?:anydesk|teamviewer|quick\s*support|quicksupport|rustdesk|"
    r"remote\s+access|screen\s*share|screen\s*sharing)\b"
    r"[\w\s,:.'-]{0,55}\b(?:install|download|open|use|connect|allow|grant|share)\b",
    re.I,
)
_ADVANCE_FEE_RE = re.compile(
    r"\b(?:job|employment|recruitment|interview|placement|work[ -]from[ -]home|"
    r"position|offer)\b[\w\s,:.'-]{0,65}\b"
    r"(?:registration|training|security|processing|application|placement|visa)\s+"
    r"(?:fee|charge|deposit)\b"
    r"|\b(?:registration|training|security|application|placement|visa)\s+"
    r"(?:fee|charge|deposit)\b[\w\s,:.'-]{0,65}"
    r"\b(?:job|employment|recruitment|interview|placement|work[ -]from[ -]home|"
    r"position|offer)\b",
    re.I,
)
_AUTHORITY_CLAIM_RE = re.compile(
    r"\b(?:bank|banking|customer\s+service|customer\s+support|support\s+team|"
    r"security\s+team|fraud\s+team|police|customs|tax\s+department|government|"
    r"courier|delivery\s+service|"
    + "|".join(re.escape(brand) for brand in BRAND_DOMAINS)
    + r")\b",
    re.I,
)


def _has_non_negated_match(pattern: re.Pattern, text: str) -> bool:
    """Ignore a signal only when its own sentence clearly negates it."""
    for match in pattern.finditer(text):
        clause_start = max(
            text.rfind(".", 0, match.start()),
            text.rfind("!", 0, match.start()),
            text.rfind("?", 0, match.start()),
            text.rfind(";", 0, match.start()),
            text.rfind(",", 0, match.start()),
            text.rfind("\n", 0, match.start()),
        ) + 1
        prefix = text[max(clause_start, match.start() - 90):match.end()]
        if not _NEGATED_REQUEST_RE.search(prefix):
            return True
    return False


def _has_non_negated_sensitive_request(text: str) -> bool:
    for match in _SENSITIVE_REQUEST_RE.finditer(text):
        clause_start = max(
            text.rfind(".", 0, match.start()),
            text.rfind("!", 0, match.start()),
            text.rfind("?", 0, match.start()),
            text.rfind(";", 0, match.start()),
            text.rfind("\n", 0, match.start()),
        ) + 1
        prefix = text[max(clause_start, match.start() - 80):match.start()]
        if not _NEGATED_REQUEST_RE.search(prefix):
            return True
    return False


def score_text(text: str) -> dict:
     # Returns nice format from a blob of text
    text = text or ""
    matches = {
        key: [phrase for phrase, pattern in patterns
              if _has_non_negated_match(pattern, text)]
        for key, patterns in _PATTERNS.items()
    }
    urls = extract_urls(text)
    matches.update(analyse_links(urls))
    matches["upi"] = extract_upi_ids(text)

    if urls:
        matches["link_present"] = urls[:3]

    sensitive_request = (
        _has_non_negated_match(_SENSITIVE_REQUEST_RE, text)
        or _has_non_negated_match(_SENSITIVE_ACTION_AFTER_RE, text)
    )
    if sensitive_request:
        matches["credential_request"] = ["Requests sensitive or identity information"]
    if _has_non_negated_match(_ACCOUNT_THREAT_RE, text):
        matches["account_threat"] = ["Threatens account access"]
    if urls and (
        _has_non_negated_match(_LINK_ACTION_RE, text)
        or _has_non_negated_match(_KYC_ACTION_RE, text)
    ):
        matches["link_action"] = ["Link paired with an account or credential action"]
    sensitive_link_action = urls and _has_non_negated_match(
        _SENSITIVE_LINK_ACTION_RE, text
    )
    if _has_non_negated_match(_FINANCIAL_REQUEST_RE, text):
        matches["financial_request"] = ["Requests a payment or transfer"]
    if _has_non_negated_match(_REMOTE_ACCESS_RE, text):
        matches["remote_access"] = ["Requests remote access or screen sharing"]
    if _has_non_negated_match(_ADVANCE_FEE_RE, text):
        matches["advance_fee"] = ["Requests an advance fee for a job or opportunity"]
    if (
        _AUTHORITY_CLAIM_RE.search(text)
        and (
            sensitive_request
            or "financial_request" in matches
            or "remote_access" in matches
            or sensitive_link_action
        )
    ):
        matches["authority_claim"] = ["Claims to represent an institution while requesting action"]

    score = sum(min(len(matches.get(k, [])), 3) * w for k, w in WEIGHTS.items())
    return {"score": min(score, 100), "matches": matches}

def describe_matches(matches: dict) -> list[str]:
    return [f"{LABELS[k]}: {', '.join(map(str, v[:3]))}"
            for k, v in matches.items() if v and k in LABELS]

def verdict_from_score(score: int) -> tuple[str, str]:
    if score >= 55:
        return "fake", "high"
    if score >= 18:
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
