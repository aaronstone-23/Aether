'''EMAIL HEADER FORENSICSS- SPD/DKIM/DMARC, IP geolocation, clock check'''
import re
import ipaddress
from email import policy
from email.parser import Parser
from email.utils import parsedate_to_datetime, parseaddr
from typing import Optional
from zoneinfo import ZoneInfo


import httpx


from .brands import brand_in_host, display_name_spoof
from .rules import score_text, describe_matches, verdict_from_score, build_actions

IP_API_BASE = "http://ip-api.com/json"


_BRACKET_IP = re.compile(r"\[(?:IPv6:)?([0-9a-fA-F:.]+)\]")
_PLAIN_V4 = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")

# ----------PARSSINGGGGGGGGGGGG--------------

def parse_email(raw: str):
    return  Parser(policy=policy.default).parsestr(raw)

def extract_headers(msg) -> dict:
    g = lambda k: str(msg.get(k, "") or "")
    return {
        "from": g("From"), 
        "reply_to": g("Reply-To"),
        "return_path": g("Return-Path"),
        "date": g("Date"),
        "subject": g("Subject"),
        "received": [str(h) for h in msg.get_all("Received", [])],
        "auth_results": g("Authentication-Results"),
        "received_spf": g("Received-SPF"),
        "dkim_signature": g("DKIM-Signature"), "message_id": g("Message-ID"),
    }

def get_body_text(msg) -> str:
    part = msg.get_body(preferencelist = ("plain", "html"))
    if part is None:
        return ""
    try:
        text = part.get_content()
    except Exception:
        return ""
    if part.get_content_type() == "text/html":
        hrefs = re.findall(r'href=["\']([^"\']+)', text)  #Keep the link targets
        text = "".join(hrefs) + " " + re.sub(r"<[^>]+>", " ", text)
    return text

def _addr_parts(value: str):
    name, addr = parseaddr(value or "")
    domain = addr.rsplit("@", 1)[1].lower() if "@" in addr else ""
    return name.strip(), addr.lower(), domain

# --------IP AND GEOOOO-----------

def _public_ip(text: str) -> Optional[str]:
    candidates = _BRACKET_IP.findall(text) or _PLAIN_V4.findall(text)
    for c in candidates:
        try:
            ip = ipaddress.ip_address(c)
        except ValueError:
            continue
        if ip.is_global:
            return str(ip)
    return None


def get_originating_ip(received: list[str]) -> Optional[str]:
    """Oldest hop first. Caveat: only hops added by servers YOU trust are reliable."""
    for header in reversed(received):
        ip = _public_ip(header)
        if ip:
            return ip
    return None


def geolocate_ip(ip: str)-> dict:
    try:
        r = httpx.get(f"{IP_API_BASE}/{ip}", timeout=5.0, params={
            "fields": "status, country, countryCode, regionName, city, isp, org, timezone"
        })
        data = r.json()
    except Exception:
        return{}
    if data.get("status") != "success":
        return {}
    return {"ip": ip,
            "country": data.get("country"),
            "region": data.get("regionName"),
            "city": data.get("city"),
            "isp": data.get("isp"),
            "timezone": data.get("timezone")}

#-------------CLOCKK---------GLOCKKKKKKKKK-------------

def _fmt_offset(h: float) -> str:
    sign, h = ("+" if h >= 0 else "-"), abs(h)
    return f"UTC{sign}{int(h):02d}:{int(round((h - int(h)) * 60)):02d}"

def sender_clock_offset(date_header: str) -> Optional[float]:
    try:
        off = parsedate_to_datetime(date_header).utcoffset()
    except (TypeError, ValueError):
        return None
    return None if off is None else off.total_seconds()/3600

def check_timezone_mismatch(headers: dict, geo: dict):
    """RETURNS (Mismatch, email offset hours and uh... yeah!! SERVER OFFSET HOURS)"""

    email_off = sender_clock_offset(headers.get("date", ""))
    tz_name = geo.get("timezone")

    # btw +0000 is what bulk mailers literally stamp on everything and *drumrolllsss THAT TELLS US NOTHING!! hmph, bad*

    if email_off is None or email_off == 0 or not tz_name:
        return False, email_off, None

    try:
        dt = parsedate_to_datetime(headers["date"])
        server_offset = dt.astimezone(ZoneInfo(tz_name)).utcoffset()

        if server_offset is None:
            return False, email_off, None

        server_off = server_offset.total_seconds() / 3600

    except Exception:
        return False, email_off, None

    return abs(email_off - server_off) >= 3, email_off, server_off


def local_time_at(date_header: str, tz_name: Optional[str]) -> Optional[str]:
    if not tz_name:
        return None

    try:
        dt = parsedate_to_datetime(date_header)
        return dt.astimezone(ZoneInfo(tz_name)).strftime(
            "%a %d %b %Y, %I:%M %p"
        )
    except Exception:
        return None

# ----------authenticateeeeeeee-------------

def check_auth(headers: dict) -> dict:
    auth = headers["auth_results"].lower()
    rspf = headers["received_spf"].lower()

    spf = "unknown"
    if "spf=pass" in auth or rspf.startswith("pass"):
        spf = "pass"
    elif "spf=softfail" in auth or rspf.startswith("softfail"):
        spf = "softfail"
    elif "spf=fail" in auth or rspf.startswith("fail"):
        spf = "fail"

    dkim = "unknown"
    if "dkim=pass" in auth:
        dkim = "pass"
    elif "dkim=fail" in auth:
        dkim = "fail"
    elif not headers["dkim_signature"]:
        dkim = "missing"

    dmarc = "unknown"
    if "dmarc=pass" in auth:
        dmarc = "pass"
    elif "dmarc=fail" in auth:
        dmarc = "fail"

    return {"spf": spf, "dkim": dkim, "dmarc": dmarc}



# --------FULLLLLLLLL ANALYSISSS--------

def analyze_headers(raw_email: str)-> dict:
    msg = parse_email(raw_email)
    h = extract_headers(msg)
    name, from_addr, from_domain = _addr_parts(h["from"])
    _, reply_addr, reply_domain = _addr_parts(h["reply_to"])

    ip = get_originating_ip(h["received"])
    geo = geolocate_ip(ip) if ip else {}
    auth = check_auth(h)
    reply_mismatch = bool(from_domain and reply_domain and from_domain != reply_domain)
    spoofed = display_name_spoof(name, from_domain)
    lookalike = brand_in_host(from_domain) if from_domain else None
    tz_mismatch, email_off, server_off = check_timezone_mismatch(h, geo)

    body = get_body_text(msg)
    body_score = score_text(f"{h['subject']}\n{body}")

    flags = []
    score = 0
    if auth["spf"] == "fail":
        flags.append("SPF failed: this server is not allowed to send for that domain"); score +=25
    if auth["spf"]== "softfail":
        flags.append("SPF softfail: sender is suspiciously outside the domain"); score += 10
    if auth["dkim"] == "missing":
        flags.append("No DKIM signature: email is not cryptographically signed"); score += 15
    if auth["dkim"] == "fail":
        flags.append("DKIM signature failed verification"); score += 20
    if auth["dmarc"] == "fail":
        flags.append("DMARC failed: the domain's own policy was violated"); score += 20
    if reply_mismatch:
        flags.append(f"Reply-To ({reply_addr}) differs from the From address"); score += 15
    if spoofed:
        flags.append(f"Display name says `{spoofed}` but the address is {from_domain}"); score += 15
    if lookalike:
        flags.append(f"Sender domain {from_domain} imitates {lookalike}"); score += 20
    
    if tz_mismatch and email_off is not None and server_off is not None:
        flags.append(
        f"Sender's clock says {_fmt_offset(email_off)} but the "
        f"sending server is in "
        f"{geo.get('country', 'an unknown country')} "
        f"({_fmt_offset(server_off)})"
    )
        score += 10
    

    flags += describe_matches(body_score["matches"])
    score = min(score + body_score["score"], 100)

    verdict, confidence = verdict_from_score(score)
    evidence = {
        "originating_ip": ip, "originating_region": geo.get("country"),
        "originating_city": geo.get("city"), "originating_isp": geo.get("isp"),
        "local_time_at_origin": local_time_at(h["date"], geo.get("timezone")),
        **auth,
        "reply_to_mismatch": reply_mismatch, "display_name_spoofed": bool(spoofed),
        "lookalike_domain": lookalike,
        "date_header_timezone": _fmt_offset(email_off) if email_off is not None else None,
        "server_offset_hours": server_off, "timezone_mismatch": tz_mismatch,
        "from_address": from_addr, "reply_to_address": reply_addr, "subject": h["subject"],
        "body_rule_score": body_score["score"], "body_rule_matches": body_score["matches"],
    }
    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk-score": score,
        "claimed_identity": name,
        "technical_evidence": evidence,
        "red_flags":flags,
        "recommended_actions": build_actions(verdict),
        "body_text": body #case_file.py uses this and then removes it
    }