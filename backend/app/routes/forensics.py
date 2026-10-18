# Upload a .eml/ .txt file of an email

from flask import Blueprint, request, jsonify

from ..extension import limiter
from ..services.case_file import build_case_file, save_verdict

bp = Blueprint("forensics", __name__)

@bp.post("/analyze/eml")
@limiter.limit("10 per minute")
def analyse_eml():
    f = request.files.get("file")
    if not f or not f.filename or not f.filename.lower().endswith((".eml", ".txt")):
        return jsonify({"error" : "invalid_file", "message": "Upload a .eml or .txt file"}), 400

    raw = f.read(1024 * 1024).decode("utf-8", errors="replace")
    case = build_case_file(raw, "email")
    save_verdict(case)
    return jsonify(case), 200