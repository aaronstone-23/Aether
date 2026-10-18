'''MAP DATA: curated static state data + live anonymous reports'''
from pathlib import Path

from flask import Blueprint, jsonify, request

from ..extension import get_supabase, limiter
from ..utils import load_json

bp = Blueprint("map_data", __name__)
STATIC_DATA = load_json(Path(__file__).parent.parent / "data" / "map_data.json", {"region":[]})

# Must match the state names in the GeoJSON the frontend areas

STATES = {
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhatisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telengana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Puducherry", "Andaman and Nicobar Islands", "Lakshadweep", "Dadra and Nagar Haveli and Daman and Diu",
}
SCAM_TYPES = {"upi_fraud", "digital_arrest", "fake_loan_app", "kyc_fraud", "phishing", "other"}

@bp.get("/map/data")
def map_data():
    sb = get_supabase()
    by_state: dict[str, int] = {}
    by_origin: dict[str, int] = {}
    if sb:
        try:
            rows = sb.table("scam_reports").select("state").limit(5000).execute().data or []
            for r in rows:
                if isinstance(r, dict):
                    state = r.get("state")
                    if isinstance(state, str):
                        by_state[state] = by_state.get(state, 0) + 1
            rows = sb.table("verdicts").select("origin_country").limit(5000).execute().data or []
            for r in rows:
                if not isinstance(r, dict):
                    continue
                origin = r.get("origin_country")
                c = origin if isinstance(origin, str) and origin else "Unknown"
                by_origin[c] = by_origin.get(c, 0) + 1
        except Exception:
            pass
    return jsonify({
        "static": STATIC_DATA.get("regions", []),
        "live_reports": [{"state": k, "count": v} for k, v in by_state.items()],
        "sender_origins": [{"country": k, "count": v} for k, v in by_origin.items()],
    }), 200


@bp.post("/map/report")
@limiter.limit("5 per minute")
def report():
    data = request.get_json(silent=True) or {}
    state, scam_type = data.get("state"), data.get("scam_type")
    if state not in STATES or scam_type not in SCAM_TYPES:
        return jsonify({"error": "invalid_report"}), 400
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "db_unavailable"}), 503
    sb.table("scam_reports").insert({"state": state, "scam_type": scam_type}).execute()
    return jsonify({"ok": True}), 200