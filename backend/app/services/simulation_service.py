'''So basically LLM-GENERATED scam scenarios
1. CACHE FIRST 
2. seeds secon
3. live at the last
ik completely useless feature but... whatever it is'''

import random
import threading
from collections import deque
from pathlib import Path

from flask import current_app

from ..schemas import ScenarioSchema
from ..utils import load_json
from .llm import chat_completetion_json

SEED_DIR = Path(__file__).parent.parent / "data" / "scenarios"
SEED_SCENARIOS: list[dict] = []
if SEED_DIR.exists():
    for f in sorted(SEED_DIR.glob("*.json")):
        SEED_SCENARIOS.extend(load_json(f, {}).get("scenarios", []))

CACHE = deque(maxlen=50)
LOCK = threading.Lock()

SYSTEM_PROMPT = """You are a financial scam scenario generator for a cybersecurity training app in India.

Generate ONE realistic message a real user might receive. The user will judge whether it is a scam.

RULES:
1. Output ONLY valid JSON. No prose, no markdown fences.
2. Use FICTIONAL brand names only (e.g. "Nova Bank", "QuickPay", "ShopKart"). NEVER real banks or companies.
3. Every URL must end in ".example". Legit messages use the plain brand domain (novabank.example).
   Scam messages use a lookalike (novabank-verify.example, nova-bank-kyc.example).
4. Phone numbers: use +91-00000-00000 only. No real UPI IDs, account numbers or IFSC codes.
5. Vary across: phishing_email, sms_scam, upi_request, kyc_expiry, lottery_prize, job_offer_scam, tech_support.
6. About 40percent of scenarios should be LEGIT messages (a real alert, an OTP notice, a receipt).

OUTPUT JSON (strict schema):
{
  "category": "phishing_email",
  "difficulty": "easy|medium|hard",
  "channel": "email|sms|whatsapp",
  "sender": "sender name + fake address/number",
  "subject": "subject line or null",
  "body": "2-6 sentences",
  "is_scam": true,
  "correct_answer": "scam" or "legit",
  "explanation": "1-3 sentences explaining the signals",
  "red_flags": ["flag1", "flag2"] or []
}

Generate ONE scenario now. JSON only."""

def generate_scenario(category=None, difficulty=None) -> dict| None:
    prompt = "Generate one scenario now."
    if category:
        prompt+= f"Category:{category}."

    if difficulty:
        prompt+= f"Difficulty: {difficulty}."

    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT
    },
    {
        "role": "user",
        "content": prompt
    }]

    for _ in range(2):
        data = chat_completetion_json(messages, max_tokens=600, temperature=0.9)
        if not data:
            continue
        try:
            scenario = ScenarioSchema(**data)

        except Exception:
            continue
        if not scenario.is_safe():
            continue
        out = scenario.model_dump()
        out["id"] = f"gen_{random.randint(100000, 999999)}"
        out["generated"] = True
        return out
    return None

def _matches(s, cat, diff) -> bool:
    return not((cat and s.get("category") != cat) or (diff and s.get("difficulty") != diff))

def _warm_one(category = None, difficulty=None):
    if len(CACHE) >= 20:
        return
    s = generate_scenario(category, difficulty)
    if s:
        with LOCK:
            CACHE.append(s)

def _warm_async(category, difficulty):
    '''BACKGROUND thread needs its own APPP context'''
    if len(CACHE) >= 10:
        return
    app = current_app._get_current_object()  # type: ignore[attr-defined]


    def run():
        with app.app_context():
            try:
                _warm_one(category, difficulty)
            except Exception:
                app.logger.exception("background scenario generation failed")

    threading.Thread(target=run, daemon=True).start()

def warm_cache(app, n: int = 5):
    cats = [
        "phishing_email", "sms_scam", "upi_request", "kyc_expiry", "lottery_prize", "job_offer_scam"
    ]
    with app.app_context():
        for _ in range(n):
            try:
                _warm_one(random.choice(cats), random.choice(["easy", "medium", "hard"]))
            except Exception:
                app.logger.exception("cache warm failed")
                return

def get_or_generate(category=None, difficulty=None) -> dict:
    '''NEVER makes the user wait ON the LLM if we have anything ready'''
    with LOCK:
        pool = [s for s in CACHE if _matches(s, category, difficulty)]
        chosen = random.choice(pool) if pool else None
        if chosen:
            CACHE.remove(chosen)

    if chosen:
        _warm_async(category, difficulty)
        return chosen

    seeds = [s for s in SEED_SCENARIOS if _matches(s, category, difficulty)]
    if seeds:
        _warm_async(category, difficulty)
        s = dict(random.choice(seeds))
        s.setdefault("id", f"seed_{random.randint(1000, 9999)}")
        s["generated"] = False
        return s

    s = generate_scenario(category, difficulty)
    return s or {
        "error": "no_scenarios",
        "message": "Could not generate a scenario. Please try again"
    }

def score_answer(scenario: dict, user_answer: str) -> dict:
    correct = scenario.get("correct_answer")
    return {
        "correct": (user_answer or "").strip().lower()== correct,
        "correct_answer": correct,
        "explanation": scenario.get("explanation", ""),
        "red_flags": scenario.get("red_flags", []),
    }




