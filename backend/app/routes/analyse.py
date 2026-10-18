'''UNIVERSAL check box: Sms, email, headers, anything!'''

from flask import Blueprint, request, jsonify

from ..extension import limiter
from ..models import AnalyzeRequest
from ..services.case_file import build_case_file, save_verdict

bp = Blueprint("analyse", __name__)

@bp.post("/analyse")
@limiter.limit("20 per minute")
def analyse():
    try:
        payload = AnalyzeRequest(**(request.get_json(silent=True) or {}))

    except Exception:
        return jsonify({"error": "invalid_payload",
                        "message": "Send {'text': '...'} (max 20,000 chars)"}),400
    case = build_case_file(payload.text, payload.channel)
    save_verdict(case)
    return jsonify(case), 200
    