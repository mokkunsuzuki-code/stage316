import json

def load_keys():
    with open("config/api_keys.json", "r") as f:
        return json.load(f)["valid_keys"]

def is_valid_key(key):
    return key in load_keys()
