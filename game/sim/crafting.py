"""Sistema de fabricación (Crafting) dirigido por datos.

Permite consultar recetas disponibles, verificar viabilidad y transmutar
ítems de forma atómica y segura en el inventario.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from game.systems.inventory import Inventory


class CraftingError(Exception):
    """Excepción para errores de recetas o fabricación."""


@dataclass(frozen=True, slots=True)
class Recipe:
    id: str
    name: str
    description: str
    ingredients: dict[str, int]
    result_item: str
    result_quantity: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Recipe:
        if not isinstance(data, dict):
            raise CraftingError("La receta debe ser un objeto JSON.")
        recipe_id = data.get("id")
        if not isinstance(recipe_id, str) or not recipe_id.strip():
            raise CraftingError("La receta exige un 'id' válido.")
        result_item = data.get("result_item")
        if not isinstance(result_item, str) or not result_item.strip():
            raise CraftingError(f"La receta '{recipe_id}' exige un 'result_item' válido.")
        result_qty = int(data.get("result_quantity", 1))
        if result_qty < 1:
            raise CraftingError(f"La receta '{recipe_id}' exige result_quantity >= 1.")

        raw_ing = data.get("ingredients")
        if not isinstance(raw_ing, dict) or not raw_ing:
            raise CraftingError(f"La receta '{recipe_id}' debe contener ingredientes.")

        ingredients: dict[str, int] = {}
        for item_id, count in raw_ing.items():
            cnt = int(count)
            if cnt < 1:
                raise CraftingError(
                    f"Ingrediente '{item_id}' en receta '{recipe_id}' debe tener cantidad >= 1."
                )
            ingredients[str(item_id)] = cnt

        return cls(
            id=recipe_id,
            name=str(data.get("name", recipe_id)),
            description=str(data.get("description", "")),
            ingredients=ingredients,
            result_item=result_item,
            result_quantity=result_qty,
        )


@dataclass(frozen=True, slots=True)
class CraftResult:
    success: bool
    recipe_id: str
    message: str
    result_item: str = ""
    result_quantity: int = 0


def load_recipes(path: Path | str | None = None) -> list[Recipe]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "data" / "recipes.json"
    p = Path(path)
    if not p.is_file():
        raise CraftingError(f"Archivo de recetas no encontrado: {p}")
    try:
        with open(p, encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as exc:
        raise CraftingError(f"Error al leer recetas de {p}: {exc}") from exc

    if not isinstance(raw, dict) or "recipes" not in raw:
        raise CraftingError("El JSON de recetas debe contener un array 'recipes'.")

    recipes: list[Recipe] = []
    seen: set[str] = set()
    for entry in raw["recipes"]:
        recipe = Recipe.from_dict(entry)
        if recipe.id in seen:
            raise CraftingError(f"ID de receta duplicado: '{recipe.id}'")
        seen.add(recipe.id)
        recipes.append(recipe)
    return recipes


def can_craft(recipe: Recipe, inventory: Inventory) -> bool:
    """Verifica si el inventario contiene todos los ingredientes requeridos."""
    for item_id, required in recipe.ingredients.items():
        if inventory.count(item_id) < required:
            return False
    return True


def craft(recipe: Recipe, inventory: Inventory) -> CraftResult:
    """Intenta fabricar una receta de forma atómica en el inventario."""
    if not can_craft(recipe, inventory):
        return CraftResult(
            success=False,
            recipe_id=recipe.id,
            message="No dispones de los ingredientes necesarios.",
        )

    # 1. Retirar ingredientes temporalmente
    removed: list[tuple[str, int]] = []
    for item_id, count in recipe.ingredients.items():
        actual_removed = inventory.remove(item_id, count)
        removed.append((item_id, actual_removed))

    # 2. Depositar el resultado
    accepted = inventory.add(recipe.result_item, recipe.result_quantity)
    if accepted < recipe.result_quantity:
        # Revertir ingredientes si el inventario no tiene capacidad suficiente
        if accepted > 0:
            inventory.remove(recipe.result_item, accepted)
        for item_id, count in removed:
            inventory.add(item_id, count)
        return CraftResult(
            success=False,
            recipe_id=recipe.id,
            message="Espacio insuficiente en el inventario para el resultado.",
        )

    return CraftResult(
        success=True,
        recipe_id=recipe.id,
        message=f"Fabricado: {recipe.name} (+{recipe.result_quantity}).",
        result_item=recipe.result_item,
        result_quantity=recipe.result_quantity,
    )
