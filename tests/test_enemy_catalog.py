"""Pruebas del catálogo data-driven de enemigos."""

from __future__ import annotations

import json

import pytest

from game.entities.enemy_catalog import (
    CatalogError,
    EnemyDefinition,
    load_enemy_catalog,
)


def test_catalog_loads_three_known_kinds() -> None:
    catalog = load_enemy_catalog()
    assert set(catalog) >= {"slime", "wisp", "brute"}


def test_catalog_behaviors_are_known() -> None:
    catalog = load_enemy_catalog()
    assert catalog["slime"].behavior == "melee"
    assert catalog["wisp"].behavior == "ranged"
    assert catalog["brute"].behavior == "charger"


def test_catalog_names_are_readable() -> None:
    catalog = load_enemy_catalog()
    assert catalog["slime"].name == "Cieno"


def test_param_falls_back_to_behavior_default() -> None:
    definition = EnemyDefinition(kind="x", name="X", behavior="charger", params={})
    assert definition.param("windup_time") == 0.55


def test_invalid_schema_version_raises() -> None:
    with pytest.raises(CatalogError):
        _from_data({"schema_version": 9, "kinds": {}})


def test_unknown_behavior_raises() -> None:
    data = {
        "schema_version": 1,
        "kinds": {"ghost": {"name": "Espectro", "behavior": "teleport", "params": {}}},
    }
    with pytest.raises(CatalogError):
        _from_data(data)


def test_non_numeric_param_raises() -> None:
    data = {
        "schema_version": 1,
        "kinds": {
            "ghost": {
                "name": "Espectro",
                "behavior": "melee",
                "params": {"wobble_amplitude": "alto"},
            }
        },
    }
    with pytest.raises(CatalogError):
        _from_data(data)


def test_unknown_param_key_raises() -> None:
    data = {
        "schema_version": 1,
        "kinds": {
            "ghost": {
                "name": "Espectro",
                "behavior": "melee",
                "params": {"teleport_distance": 10},
            }
        },
    }
    with pytest.raises(CatalogError):
        _from_data(data)


def test_new_kind_can_reuse_existing_behavior() -> None:
    """Un tipo nuevo con comportamiento existente no exige código nuevo."""
    data = {
        "schema_version": 1,
        "kinds": {
            "ghost": {
                "name": "Espectro",
                "behavior": "ranged",
                "params": {"far_distance": 300.0},
            }
        },
    }
    catalog = _from_data(data)
    assert catalog["ghost"].behavior == "ranged"
    assert catalog["ghost"].param("far_distance") == 300.0
    assert catalog["ghost"].param("move_scale") == 0.55  # default del comportamiento


def _from_data(data: dict) -> dict[str, EnemyDefinition]:
    from game.entities import enemy_catalog

    return enemy_catalog._parse_catalog(json.loads(json.dumps(data)))
