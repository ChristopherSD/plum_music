import json
from pathlib import Path


def get_constants_dict() -> dict:
    """
    Reads the constants config file to return as a dict.
    :return: A dict of constant names (key) and their values.
    """
    with (Path(__file__).parent.absolute() / "constants.json").open('r') as f:
        return json.load(f)
