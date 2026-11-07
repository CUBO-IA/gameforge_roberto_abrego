"""Pruebas del sistema de partidas multi-ranura (Slots 1, 2, 3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from game.persistence.paths import save_file
from game.persistence.savegame import (
    RunSnapshot,
    delete_slot,
    list_save_slots,
    load_slot,
    save_slot,
)


def make_snapshot(score: int = 100, floor: int = 1) -> RunSnapshot:
    return RunSnapshot(
        seed=42,
        floor=floor,
        elapsed=60.0,
        score=score,
        kills=5,
        player_x=100.0,
        player_y=100.0,
        health=80.0,
        inventory={"shard": 2},
    )


def test_save_file_slot_bounds(tmp_path: Path) -> None:
    p1 = save_file(tmp_path, 1)
    p2 = save_file(tmp_path, 2)
    p3 = save_file(tmp_path, 3)

    assert p1.name == "slot1.json"
    assert p2.name == "slot2.json"
    assert p3.name == "slot3.json"

    with pytest.raises(ValueError):
        save_file(tmp_path, 0)
    with pytest.raises(ValueError):
        save_file(tmp_path, 10)


def test_save_slot_isolation_and_listing(tmp_path: Path) -> None:
    # Inicialmente todos los slots están vacíos
    slots_initial = list_save_slots(tmp_path, max_slots=3)
    assert slots_initial[1] is None
    assert slots_initial[2] is None
    assert slots_initial[3] is None

    # Guardar en slot 1 y slot 3
    snap1 = make_snapshot(score=150, floor=1)
    snap3 = make_snapshot(score=900, floor=3)

    save_slot(tmp_path, 1, snap1)
    save_slot(tmp_path, 3, snap3)

    # Listar slots
    slots = list_save_slots(tmp_path, max_slots=3)
    assert slots[1] is not None
    assert slots[1].run.score == 150
    assert slots[2] is None  # Slot 2 permanece vacío
    assert slots[3] is not None
    assert slots[3].run.score == 900
    assert slots[3].run.floor == 3

    # Cargar directamente slot 1 y slot 3
    data1 = load_slot(tmp_path, 1)
    assert data1.run.score == 150

    data3 = load_slot(tmp_path, 3)
    assert data3.run.score == 900

    # Borrar slot 1
    assert delete_slot(tmp_path, 1)
    assert not delete_slot(tmp_path, 1)  # Ya no existe

    slots_after = list_save_slots(tmp_path, max_slots=3)
    assert slots_after[1] is None
    assert slots_after[3] is not None
