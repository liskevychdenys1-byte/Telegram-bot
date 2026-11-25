
import ast
import json
import importlib
from pathlib import Path
from unittest.mock import patch

import pytest

FILES = [
    "bot.py",
    "steam.py",
    "epic.py",
    "handlers.py",
    "config.py"
]


def test_01_bot_exists():
    assert Path("bot.py").is_file()


def test_02_steam_exists():
    assert Path("steam.py").is_file()


def test_03_epic_exists():
    assert Path("epic.py").is_file()


def test_04_handlers_exists():
    assert Path("handlers.py").is_file()


def test_05_config_exists():
    assert Path("config.py").is_file()


def test_06_all_files_have_valid_syntax():
    for filename in FILES:
        path = Path(filename)
        assert path.exists()
        ast.parse(path.read_text(encoding="utf-8"))


def test_07_steam_import():
    assert importlib.import_module("steam")


def test_08_epic_import():
    assert importlib.import_module("epic")


def test_09_handlers_import():
    assert importlib.import_module("handlers")


def test_10_config_import():
    assert importlib.import_module("config")


def test_11_config_has_token_and_api_key():
    config = importlib.import_module("config")

    assert isinstance(config.TOKEN, str)
    assert config.TOKEN.strip() != ""

    assert isinstance(config.EGDATA_API_KEY, str)
    assert config.EGDATA_API_KEY.strip() != ""


def test_12_steam_has_functions():
    steam = importlib.import_module("steam")

    functions = [
        name for name in dir(steam)
        if callable(getattr(steam, name))
        and not name.startswith("_")
    ]

    assert len(functions) > 0


def test_13_epic_has_functions():
    epic = importlib.import_module("epic")

    functions = [
        name for name in dir(epic)
        if callable(getattr(epic, name))
        and not name.startswith("_")
    ]

    assert len(functions) > 0


def test_14_json_processing():
    data = {
        "game": "Test Game",
        "discount": 50
    }

    result = json.loads(json.dumps(data))

    assert result["game"] == "Test Game"
    assert result["discount"] == 50


def test_15_epic_api_error_handling():
    import epic

    import requests

    with patch(
        "epic.requests.get",
        side_effect=requests.exceptions.ConnectionError
    ):
        result = epic.get_epic_deals()

    assert result == []


def test_16_epic_extract_price():
    import epic

    item = {
        "price": {
            "currencyCode": "USD",
            "originalPrice": 10000,
            "discountPrice": 5000,
            "discount": 50
        }
    }

    result = epic.extract_price(item)

    assert result is not None
    assert result["old_price"] == 100
    assert result["new_price"] == 50
    assert result["discount"] == 50
    assert result["currency"] == "USD"
