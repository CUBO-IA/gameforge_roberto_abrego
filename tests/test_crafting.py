"""Pruebas del sistema de fabricación (game.sim.crafting)."""

from __future__ import annotations

import pytest

from game.sim.crafting import CraftingError, Recipe, can_craft, craft, load_recipes
from game.systems.inventory import Inventory


def test_load_default_recipes() -> None:
    recipes = load_recipes()
    assert len(recipes) >= 3
    ids = {r.id for r in recipes}
    assert "recipe_potion" in ids
    assert "recipe_shard_infusion" in ids


def test_recipe_validation_invalid_data() -> None:
    with pytest.raises(CraftingError):
        Recipe.from_dict("no_es_dict")  # type: ignore[arg-type]

    with pytest.raises(CraftingError):
        Recipe.from_dict({"id": "", "result_item": "potion", "ingredients": {"coin": 1}})

    with pytest.raises(CraftingError):
        Recipe.from_dict({"id": "r1", "result_item": "potion", "ingredients": {}})

    with pytest.raises(CraftingError):
        Recipe.from_dict(
            {"id": "r1", "result_item": "potion", "ingredients": {"coin": 0}}
        )


def test_can_craft_checks_ingredients() -> None:
    recipe = Recipe(
        id="test_rec",
        name="Test",
        description="",
        ingredients={"shard": 2, "coin": 5},
        result_item="potion",
        result_quantity=1,
    )
    inv = Inventory(capacity=10)
    assert not can_craft(recipe, inv)

    inv.add("shard", 2)
    assert not can_craft(recipe, inv)

    inv.add("coin", 4)
    assert not can_craft(recipe, inv)

    inv.add("coin", 1)
    assert can_craft(recipe, inv)


def test_craft_success_consumes_and_adds() -> None:
    recipe = Recipe(
        id="test_rec",
        name="Poción",
        description="",
        ingredients={"shard": 1, "coin": 2},
        result_item="potion",
        result_quantity=1,
    )
    inv = Inventory(capacity=10)
    inv.add("shard", 2)
    inv.add("coin", 5)

    res = craft(recipe, inv)
    assert res.success
    assert res.result_item == "potion"
    assert res.result_quantity == 1
    assert inv.count("shard") == 1
    assert inv.count("coin") == 3
    assert inv.count("potion") == 1


def test_craft_rollback_on_inventory_full() -> None:
    recipe = Recipe(
        id="test_rec",
        name="Poción",
        description="",
        ingredients={"coin": 1},
        result_item="potion",
        result_quantity=1,
    )
    # Capacidad de 2 tipos de ítems.
    # Ocupamos ambos slots: 2 coins (slot 1) y 1 shard (slot 2).
    inv = Inventory(capacity=2)
    inv.add("coin", 2)
    inv.add("shard", 1)

    # Al intentar fabricar poción, se gasta 1 coin (queda 1 coin, slot 1 sigue ocupado).
    # Como shard ocupa el slot 2, potion requiere un 3er slot que no cabe.
    res = craft(recipe, inv)
    assert not res.success
    assert "Espacio insuficiente" in res.message
    # Los ingredientes deben permanecer intactos tras el rollback
    assert inv.count("coin") == 2
    assert inv.count("shard") == 1
    assert inv.count("potion") == 0
