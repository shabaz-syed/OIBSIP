"""Load and save the assistant's JSON config (custom commands, contacts, knowledge base)."""
import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")

DEFAULT_CONFIG = {"custom_commands": {}, "contacts": {}, "knowledge_base": {}}

WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
EMAIL_ADDR = os.getenv("ASSISTANT_EMAIL")
EMAIL_PASS = os.getenv("ASSISTANT_EMAIL_PASSWORD")


def load_config():
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)
    for key, value in DEFAULT_CONFIG.items():
        data.setdefault(key, value)
    return data


def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
