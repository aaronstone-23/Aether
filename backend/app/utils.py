import json 
from pathlib import Path

def load_json(path: Path, default):
    # READ a Json as UTF-8. Never crashes the app if missing or broken
    try:
        return json.loads(path.read_text(ecoding = "utf-8"))
    except FileNotFoundError:
        return default
    except Exception as e:
        print(f"[warn] could not read {path.name}: {e}")
        return default
    