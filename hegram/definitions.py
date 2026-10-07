import json
from pathlib import Path

# Verb definitions from the Strong's Hebrew dictionary, keyed by root without vowel points.
# Built by hegram.build_dataframes; the app only reads it.
DEFINITIONS_PATH = Path("data/definitions.json")


def load_definitions() -> dict:
    with open(DEFINITIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


definitions = load_definitions()
