"""Pruebas de integración de pisos alternativos (Cavernas en floor.py)."""

from __future__ import annotations

from game.core.config import DungeonConfig
from game.sim.floor import FloorType, calculate_floor_transition, floor_type_for
from game.world.cavern_generation import generate_cavern
from game.world.generation import generate_dungeon


def test_floor_type_mapping() -> None:
    """Verifica que el piso 2 sea Caverna y los pisos 1 y 3 sean Mazmorra."""
    assert floor_type_for(1) == FloorType.DUNGEON
    assert floor_type_for(2) == FloorType.CAVERN
    assert floor_type_for(3) == FloorType.DUNGEON


def test_floor_type_variant_override() -> None:
    """Permite sobreescribir explícitamente el tipo de piso con la variante."""
    assert floor_type_for(1, variant="cavern") == FloorType.CAVERN
    assert floor_type_for(2, variant="dungeon") == FloorType.DUNGEON


def test_floor_transition_carries_floor_type() -> None:
    """La transición al piso 2 indica tipo caverna."""
    t1 = calculate_floor_transition(1)
    assert t1 is not None
    assert t1.next_floor == 2
    assert t1.floor_type == FloorType.CAVERN

    t2 = calculate_floor_transition(2)
    assert t2 is not None
    assert t2.next_floor == 3
    assert t2.floor_type == FloorType.DUNGEON


def test_floor_generation_dispatch() -> None:
    """Comprueba que generate_cavern y generate_dungeon se invocan de acuerdo al tipo de piso."""
    seed = 88776655
    cfg = DungeonConfig()

    # Piso 1 -> Mazmorra estándar (debe tener salas rectangulares > 2)
    dungeon_f1 = generate_dungeon(seed, floor=1, config=cfg)
    assert len(dungeon_f1.rooms) >= 2

    # Piso 2 -> Caverna orgánica (debe generarse sin error y tener spawn y altar válidos)
    cavern_f2 = generate_cavern(seed, floor=2, config=cfg)
    assert cavern_f2.spawn is not None
    assert cavern_f2.altar is not None
    assert not cavern_f2.tilemap.is_solid_at(cavern_f2.spawn.x, cavern_f2.spawn.y)
