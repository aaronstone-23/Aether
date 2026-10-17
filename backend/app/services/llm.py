# ALL LLM CALLS ARE HERE

import json

import httpx
from flask import current_app

def _post(model, messages, max_tokens, temperature, timeout, response_format) -> str:
    cfg = current_app.config
    payload = {"model": model,
               "messages": messages,
               "max_tokens": max_tokens,
               "temperature": temperature}
    if response_format:
        payload["response_format"] = response_format
    resp = httpx.post(
        cfg["OPENROUTER_URL"],
        headers={"Authorization": f"Bearer {cfg['OPENROUTER_KEY']}",
                 "Content-type": "application/json",
                 "HTTP-Referer": "https://aether.local", 
                 "X-Title": "Aether"},
        json=payload, 
        timeout=timeout,
    )
    if resp.status_code !=200:
        current_app.logger.warning("LLM %s -> HTTP %s: %s", model, resp.status_code, resp.text[:200])
        return ""
    content = resp.json()["choices"][0]["message"].get("content") or ""
    return content.strip()


def chat_completion(messages, max_tokens=500, temperature=0.3,
                    timeout=12.0, response_format = None)-> str:
    # Try the main model, then the fall back. Returns '' if both fail
    cfg = current_app.config
    if not cfg["OPENROUTER_API_KEY"]:
        return ""
    for model in (cfg["OPENROUTER_MODEL"], cfg["OPENROUTER_FALLBACK_MODEL"]):
        if not model:
            continue
        try:
            out = _post(model, messages, max_tokens, temperature, timeout, response_format)
            if out:
                return out
        except Exception as e:
            current_app.logger.warning("LLM CALL FAILED (%s): %s", model, type(e).__name__)
    return ""

def _extract_json(raw: str):
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return None

def chat_completetion_json(messages, max_tokens=600, temperature=0.5)-> dict | None:
    raw = chat_completion(messages, max_tokens, temperature, 
                          response_format={"type": "json_object"})
    if not raw:
        raw = chat_completion(messages, max_tokens, temperature)
    return _extract_json(raw) if raw else None