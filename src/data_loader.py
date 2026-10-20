"""Reading EVA data from its source.

This is the only module that knows the data is stored as a JSON file.
"""
import json


def load_eva_data(path):
    """Return the raw EVA records stored in the JSON file at ``path``."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
