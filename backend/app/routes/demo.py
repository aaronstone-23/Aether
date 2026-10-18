import hmac
import re
import secrets

from flask import Blueprint, current_app, jsonify, request

from ..extension import get_supabase, limiter

from ..models import DemoRegisterRequest

bp = Blueprint("demo", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _is_admin() -> bool:
    key = current_app.config["ADMIN_KEY"]
    return bool(key) and hmac.compare_digest(request.headers.get("X-Admin-Key", ""), key)

@bp.post("/demo/option")
@limiter.limit("10 per minute")
def optin():
    try:
        p = DemoRegisterRequest(**(request.get_json(silent=True) or{}))
    except Exception:
        return jsonify({"error": "invalid_payload"}), 400

    email = p.email.strip().lower()
    if not p.consent or not EMAIL_RE.match(email):
        return jsonify({"error": "invalid",
                        "message": "Valid email and consent requried"}), 400
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "db_unavailable"}), 503
    sb.table("demo_registrations").upsert(
        {"email": email, 
         "token": secrets.token_urlsafe(16),
         "consent": True},
         on_conflict="email"
).execute()
    return jsonify({"ok": True}), 200


@bp.get("/demo/count")
def count():
    sb = get_supabase()
    if not sb:
        return jsonify({"count": 0}), 200
    r = sb.table("demo_registrations").select("id", count="exact").execute() # type: ignore[arg-type]
    return jsonify({"count": r.count or 0}), 200
@bp.delete("/demo/emails")
def wipe():
    if not _is_admin():
        return jsonify({
            "error": "forbidden"
        }), 403
    sb = get_supabase()
    if sb:
        sb.table("demo_registrations").delete().neq("id", 0).execute()
    return jsonify({"ok": True}), 200

