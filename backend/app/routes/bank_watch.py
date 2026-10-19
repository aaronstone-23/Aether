from ..utils import load_json
BREACHES = load_json(Path(__file__).parent.parent / "data" / "breach_incidents.json", {"banks": []})