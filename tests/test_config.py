import json
from pathlib import Path

import pytest

from game.core.config import ConfigError, GameConfig, load_config


def test_defaults_are_complete() -> None:
    config = GameConfig.from_dict({})
    assert config.window.width == 1280
    assert config.player.max_health == 100.0
    assert config.dungeon.shards_required == 3
    assert set(config.enemies) == {"slime", "wisp", "brute"}
    assert config.enemies["wisp"].attack_range > 0


def test_overrides_are_applied() -> None:
    config = GameConfig.from_dict(
        {
            "window": {"width": 800, "height": 600, "fps": 30},
            "player": {"speed": 100},
            "dungeon": {"chests": 6, "shards_required": 4},
            "enemies": {"slime": {"health": 10, "speed": 20}},
        }
    )
    assert config.window.width == 800
    assert config.player.speed == 100
    assert config.dungeon.chests == 6
    assert config.enemies["slime"].health == 10
    assert config.enemies["brute"].health == 110


def test_packaged_config_loads() -> None:
    config = load_config()
    assert config.window.title
    assert config.player.attack_range > 0


@pytest.mark.parametrize(
    "raw",
    [
        {"window": {"width": 10}},
        {"player": {"speed": -5}},
        {"dungeon": {"min_room": 12, "max_room": 8}},
        {"dungeon": {"chests": 2, "shards_required": 5}},
        {"enemies": {"dragon": {}}},
        {"audio": {"master_volume": 2}},
        {"window": "no"},
    ],
)
def test_invalid_values_raise(raw: dict) -> None:
    with pytest.raises(ConfigError):
        GameConfig.from_dict(raw)


def test_load_invalid_json_and_missing_file(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(broken)
    with pytest.raises(ConfigError):
        load_config(tmp_path / "missing.json")
    wrong_root = tmp_path / "root.json"
    wrong_root.write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(wrong_root)
