'''PHONE NUMBER ANALYSIS via the phonenumber library'''

import phonenumbers
from phonenumbers import carrier

from .rules import extract_phones

def _number_type(number) -> str:
    kind = phonenumbers.number_type(number)
    type_names = {
        phonenumbers.PhoneNumberType.FIXED_LINE: "fixed_line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_line_or_mobile",
        phonenumbers.PhoneNumberType.MOBILE: "mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "toll_free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "premium_rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "shared_cost",
        phonenumbers.PhoneNumberType.VOIP: "voip",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "personal_number",
        phonenumbers.PhoneNumberType.PAGER: "pager",
        phonenumbers.PhoneNumberType.UAN: "uan",
        phonenumbers.PhoneNumberType.VOICEMAIL: "voicemail",
        phonenumbers.PhoneNumberType.UNKNOWN: "unknown",
    }
    return type_names.get(kind, "unknown")

def check_phones(text: str, default_region: str = "IN") -> dict:
    results, seen = [], set()
    for candidate in extract_phones(text):
        try:
            parsed = phonenumbers.parse(candidate, default_region)
            if not phonenumbers.is_valid_number(parsed):
                continue
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            if e164 in seen:
                continue
            seen.add(e164)
            results.append({
                "raw": candidate.strip(),
                "e164": e164,
                "country": phonenumbers.region_code_for_number(parsed),
                "carrier": carrier.name_for_number(parsed, "en") or "unknown",
                "type": _number_type(parsed), 
            })
        except phonenumbers.NumberParseException:
            continue
    return {"found": len(results), "numbers": results}

