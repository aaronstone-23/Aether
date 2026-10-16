'''Brand--> official Domains, it will catch lookalike domains and spoofed display names
 NOTE TO ME --> EXPAND THIS LIST TOO if u have to btw!!!'''

import re
from urllib.parse import urlparse

BRAND_DOMAINS ={
    "mircrosoft": ["microsoft.com", "office.com", "live.com", "outlook.com"],
    "google": ["google.com", "gmail.com", "youtbe.com"],
    "apple": ["apple.com", "icloud.com"],
    "amazon": ["amazon.com", "amazon.in", "amazonses.com"],
    "paypal": ["paypal.com"],
    "netflix": ["netflix.com"],
    "paytm": ["paytm.com"],
    "phonepe": ["phonepe.com"],
    "hdfc": ["hdfcbank.com", "hdfcbank.net"],
    "icici": ["icicibank.com"],
    "sbi": ["sbi.co.in", "onlinesbi.sbi"],
    "axis": ["axisbank.com"],
    "kotak": ["kotak.com"],
    "irctc": ["irctc.co.in"],
}

_LEET = str.maketrans("013", "ole") #micr0s0fT--> mircrosoft, poypal--> paypal

def host_of(url: str) -> str:
    return (urlparse(url if "//" in url else "//" + url).hostname or "").lower()

def is_official(host:str, brand:str) -> bool:
    return any(host == d or host.endswith("."+d) for d in BRAND_DOMAINS[brand])

def brand_in_host(host: str)-> str | None:
    '''Brand this hosts imitaes (basically it contains the name but it isnt and official domain so yeah)'''
    host = host.lower()
    tokens = re.split(r"[^a-z0-9]+", host.translate(_LEET))
    for brand in BRAND_DOMAINS:
        if is_official(host, brand):
            continue
        for t in tokens:
            if t == brand or (len(brand)>= 4 and t.startswith(brand)):
                return brand
        return None

def display_name_spoof(display: str, doamin: str)-> str | None:
    """DISPLAY NAME SAYS MICROSOFT BUT ADDRESS ISN'T A MICRSOFT DOMAIN"""
    d = (display or "").lower()
    for brand in BRAND_DOMAINS:
        if re.search(rf"\b{brand}\b",d) and not is_official(doamin or "", brand):
            return brand
    return None