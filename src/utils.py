import json
from pathlib import Path


def load_location_terms(config_path: str = "config/location_terms.json") -> dict:
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Location config not found: {config_path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)