import json
from pathlib import Path

import pytest

from game.persistence.savegame import (
    MAX_SAVE_BYTES,
    RunSnapshot,
    SaveGameError,
    delete_save,
    load_run,
    save_run,
)


def make_snapshot(**overrides) -> RunSnapshot:
    values = {
        "seed": 12345,
        "floor": 1,
        "elapsed": 42.5,
        "score": 750,
        "kills": 9,
        "player_x": 640.0,
        "player_y": 480.0,
        "health": 87.5,
        "inventory": {"shard": 2, "potion": 1},
        "chests_opened": ("c0", "c1"),
        "defeated": ("e0", "e5"),
        "altar_activated": False,
    }
    values.update(overrides)
    return RunSnapshot(**values)


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "slot1.json"
    save_run(path, make_snapshot())
    data = load_run(path)
    assert data.schema_version == 1
    assert data.saved_at
    assert data.run == make_snapshot()


def test_save_is_written_atomically(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "slot1.json"
    save_run(path, make_snapshot(score=1))
    save_run(path, make_snapshot(score=2))
    assert load_run(path).run.score == 2
    assert not list(path.parent.glob("*.tmp"))


def test_missing_and_corrupt_files(tmp_path: Path) -> None:
    with pytest.raises(SaveGameError):
        load_run(tmp_path / "missing.json")

    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(SaveGameError):
        load_run(empty)

    broken = tmp_path / "broken.json"
    broken.write_text("{broken", encoding="utf-8")
    with pytest.raises(SaveGameError):
        load_run(broken)

    invalid_root = tmp_path / "root.json"
    invalid_root.write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(SaveGameError):
        load_run(invalid_root)


def test_oversized_save_is_rejected(tmp_path: Path) -> None:
    huge = tmp_path / "huge.json"
    huge.write_text("x" * (MAX_SAVE_BYTES + 1), encoding="utf-8")
    with pytest.raises(SaveGameError):
        load_run(huge)


def payload() -> dict:
    return {
        "schema_version": 1,
        "saved_at": "2026-01-01T00:00:00+00:00",
        "run": {
            "seed": 1,
            "floor": 1,
            "elapsed": 1.0,
            "score": 10,
            "kills": 1,
            "player": {"x": 10.0, "y": 20.0},
            "health": 50.0,
            "inventory": {"potion": 1},
            "chests_opened": [],
            "defeated": [],
            "altar_activated": False,
        },
    }


def write_payload(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.mark.parametrize("version", [0, 2, 99])
def test_unsupported_versions_are_rejected(tmp_path: Path, version: int) -> None:
    data = payload()
    data["schema_version"] = version
    with pytest.raises(SaveGameError):
        load_run(write_payload(tmp_path, data))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data["run"].pop("seed"),
        lambda data: data["run"].update(floor=0),
        lambda data: data["run"].update(health=-1),
        lambda data: data["run"].update(score=-10),
        lambda data: data["run"].update(inventory={"unknown": 1}),
        lambda data: data["run"].update(inventory={"potion": 0}),
        lambda data: data["run"].update(chests_opened=["a", "a"]),
        lambda data: data["run"].update(altar_activated="yes"),
        lambda data: data["run"].pop("player"),
        lambda data: data["run"]["player"].update(x="left"),
        lambda data: data.update(saved_at=5),
    ],
)
def test_invalid_payloads_are_rejected(tmp_path: Path, mutate) -> None:
    data = payload()
    mutate(data)
    with pytest.raises(SaveGameError):
        load_run(write_payload(tmp_path, data))


def test_invalid_snapshot_does_not_overwrite_good_save(tmp_path: Path) -> None:
    path = tmp_path / "slot1.json"
    save_run(path, make_snapshot(score=99))
    with pytest.raises(SaveGameError):
        save_run(path, make_snapshot(seed=-1))
    assert load_run(path).run.score == 99
    assert not path.with_name(path.name + ".tmp").exists()


def test_too_many_inventory_slots_rejected(tmp_path: Path) -> None:
    data = payload()
    data["run"]["inventory"] = {f"item{index}": 1 for index in range(21)}
    with pytest.raises(SaveGameError):
        load_run(write_payload(tmp_path, data))


def test_delete_save(tmp_path: Path) -> None:
    path = tmp_path / "slot1.json"
    assert delete_save(path) is False
    save_run(path, make_snapshot())
    assert delete_save(path) is True
    assert not path.exists()
