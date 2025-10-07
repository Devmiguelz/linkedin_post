# utils/cache.py
import os
import json
import re
import time
from pathlib import Path

CACHE_DIR = os.getenv("CACHE_DIR", "./.cache")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

def sanitize_filename(name):
    # Reemplaza todos los caracteres inválidos por "_"
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def save_cache(key, data):
    name_file = sanitize_filename(key)
    path = os.path.join(CACHE_DIR, f"{name_file}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"ts": time.time(), "data": data}, f, ensure_ascii=False, indent=2)

def load_cache(key, ttl_seconds=None):
    name_file = sanitize_filename(key)
    path = os.path.join(CACHE_DIR, f"{name_file}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if ttl_seconds:
        if time.time() - obj.get("ts",0) > ttl_seconds:
            return None
    return obj.get("data")
