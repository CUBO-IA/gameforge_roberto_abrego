"""Catálogo de objetos y definiciones de inventario."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ItemDef:
    id: str
    name: str
    kind: str
    description: str
    color: tuple[int, int, int]


ITEMS: dict[str, ItemDef] = {
    "shard": ItemDef(
        id="shard",
        name="Fragmento de ascua",
        kind="quest",
        description="Late con el calor de la Fragua. Reúne tres.",
        color=(255, 154, 64),
    ),
    "potion": ItemDef(
        id="potion",
        name="Frasco de brasa",
        kind="consumable",
        description="Restaura salud al usarlo (Q).",
        color=(220, 72, 92),
    ),
    "coin": ItemDef(
        id="coin",
        name="Moneda de hierro",
        kind="currency",
        description="Puntúa al final de la partida.",
        color=(226, 196, 92),
    ),
}


def item_exists(item_id: str) -> bool:
    return item_id in ITEMS
