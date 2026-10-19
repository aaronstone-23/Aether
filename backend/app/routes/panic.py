'''I've been scammed, recovery steps'''
from flask import Blueprint, jsonify

bp = Blueprint("panic", __name__)

MONEY_SENT = [
    {"step": 1, "title": "Call 1930 right now", "detail": "India's cyber fraud helpline. The first hour matters most; fast reports can sometimes freeze the money."},
    {"step": 2, "title": "Call your bank", "detail": "Use the number on your card or the official website. Ask them to block the transaction and your card/UPI."},
    {"step": 3, "title": "File a complaint", "detail": "Report at cybercrime.gov.in with screenshots, transaction IDs, and the scammer's number or UPI ID."},
    {"step": 4, "title": "Secure your accounts", "detail": "Change passwords and PINs. Remove any app the scammer asked you to install."},
]
NO_MONEY = [
    {"step": 1, "title": "Stop responding", "detail": "Don't reply, click, or share OTPs. Block the sender."},
    {"step": 2, "title": "If you clicked or entered details", "detail": "Change that password now and enable two-factor login."},
    {"step": 3, "title": "Report it", "detail": "cybercrime.gov.in, or forward SMS scams to 1909 / report in your mail app."},
]

@bp.get("/panic/<kind>")
def panic(kind):
    if kind == "money_sent":
        steps =  MONEY_SENT
    elif kind == "no_money":
        steps = NO_MONEY
    else:
        return jsonify({
            "error": "unknown_panic_kind"
        }), 404

