import json
from pathlib import Path

API_KEYS_PATH = Path("config/api_keys.json")


def load_api_keys():
    if not API_KEYS_PATH.exists():
        return {}

    with API_KEYS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_valid_key(api_key):
    if not api_key:
        return False

    api_keys = load_api_keys()
    return api_key in api_keys


def get_plan(api_key):
    api_keys = load_api_keys()
    return api_keys.get(api_key, "free")
