from pathlib import Path

from flask import Blueprint, jsonify, request

from ..extension import limiter
from ..services.news import fetch_bank_news
from ..utils import load_json

bp = Blueprint("bank_watch", __name__)

INCIDENTS_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "scenarios"
    / "breach_incidents.json"
)

INCIDENT_DATA = load_json(INCIDENTS_FILE, {"incidents": []})
INCIDENTS = INCIDENT_DATA.get("incidents", [])


@bp.get("/bank-watch")
@limiter.limit("20 per minute")
def bank_watch():
    bank = (request.args.get("bank") or "").strip()

    if not bank or len(bank) > 80:
        return jsonify({
            "error": "invalid_bank",
            "message": "Provide a bank name, up to 80 characters.",
        }), 400

    matching_incidents = [
        incident
        for incident in INCIDENTS
        if isinstance(incident, dict)
        and str(incident.get("bank", "")).casefold() == bank.casefold()
    ]

    return jsonify({
        "bank": bank,
        "incidents": matching_incidents,
        "news": fetch_bank_news(bank),
    }), 200