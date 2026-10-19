import secrets
from threading import Lock

from flask import Blueprint, jsonify, request

from ..extension import limiter
from ..services.simulation_service import get_or_generate, score_answer

bp = Blueprint("simulation", __name__)

ACTIVE_SCENARIOS = {}
ACTIVE_SCENARIOS_LOCK = Lock()
MAX_ACTIVE_SCENARIOS = 500

ALLOWED_CATEGORIES = {
    "phishing_email",
    "sms_scam",
    "upi_request",
    "kyc_expiry",
    "lottery_prize",
    "job_offer_scam",
    "tech_support",
}

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_ANSWERS = {"scam", "legit"}


@bp.get("/simulation/next")
@limiter.limit("30 per minute")
def next_scenario():
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")

    if category and category not in ALLOWED_CATEGORIES:
        return jsonify({"error": "invalid_category"}), 400

    if difficulty and difficulty not in ALLOWED_DIFFICULTIES:
        return jsonify({"error": "invalid_difficulty"}), 400

    scenario = get_or_generate(category, difficulty)

    if "error" in scenario:
        return jsonify(scenario), 503

    scenario_id = secrets.token_urlsafe(24)

    with ACTIVE_SCENARIOS_LOCK:
        while len(ACTIVE_SCENARIOS) >= MAX_ACTIVE_SCENARIOS:
            oldest_id = next(iter(ACTIVE_SCENARIOS))
            ACTIVE_SCENARIOS.pop(oldest_id)

        ACTIVE_SCENARIOS[scenario_id] = scenario

    # Don't send the answer or explanation before the player responds.
    public_scenario = {
        key: value
        for key, value in scenario.items()
        if key not in {
            "correct_answer",
            "is_scam",
            "explanation",
            "red_flags",
        }
    }
    public_scenario["scenario_id"] = scenario_id

    return jsonify(public_scenario), 200


@bp.post("/simulation/score")
@limiter.limit("30 per minute")
def score_scenario():
    payload = request.get_json(silent=True) or {}
    scenario_id = payload.get("scenario_id")
    answer = payload.get("answer")

    if not isinstance(scenario_id, str):
        return jsonify({"error": "invalid_scenario_id"}), 400

    if not isinstance(answer, str) or answer.strip().lower() not in ALLOWED_ANSWERS:
        return jsonify({"error": "invalid_answer"}), 400

    with ACTIVE_SCENARIOS_LOCK:
        scenario = ACTIVE_SCENARIOS.pop(scenario_id, None)

    if scenario is None:
        return jsonify({
            "error": "scenario_not_found",
            "message": "Request a new scenario and try again.",
        }), 404

    result = score_answer(scenario, answer)
    return jsonify(result), 200