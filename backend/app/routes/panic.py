from flask import Blueprint, jsonify

bp = Blueprint("panic", __name__)

MONEY_SENT = [
    {
        "step": 1,
        "title": "Call 1930 right now",
        "detail": (
            "India's cyber fraud helpline. Report the transaction as soon "
            "as possible."
        ),
    },
    {
        "step": 2,
        "title": "Call your bank",
        "detail": (
            "Use the number on your card or the bank's official website. "
            "Ask them to report and stop the transaction if possible."
        ),
    },
    {
        "step": 3,
        "title": "File a complaint",
        "detail": (
            "Report at cybercrime.gov.in. Keep screenshots, transaction "
            "details, and the scammer's contact information."
        ),
    },
    {
        "step": 4,
        "title": "Secure your accounts",
        "detail": (
            "Change any password or PIN you shared. Remove apps the scammer "
            "asked you to install."
        ),
    },
]

NO_MONEY = [
    {
        "step": 1,
        "title": "Stop responding",
        "detail": "Don't reply, click links, or share OTPs. Block the sender.",
    },
    {
        "step": 2,
        "title": "Secure any details you shared",
        "detail": (
            "If you entered a password, change it using the service's "
            "official app or website."
        ),
    },
    {
        "step": 3,
        "title": "Report the message",
        "detail": (
            "Report it at cybercrime.gov.in or use your phone or email "
            "app's reporting tools."
        ),
    },
]


@bp.get("/panic/<kind>")
def panic(kind):
    if kind == "money_sent":
        steps = MONEY_SENT
    elif kind == "no_money":
        steps = NO_MONEY
    else:
        return jsonify({"error": "unknown_panic_kind"}), 404

    return jsonify({"kind": kind, "steps": steps}), 200