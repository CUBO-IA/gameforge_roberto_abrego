"""Aserciones de estado sobre la escena de juego, sin depender del render."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from game.scenes.play import PlayScene
from game.world.collision import circle_hits_solid
from tools.test_runner.scenario import AssertionSpec

Evaluator = Callable[[PlayScene, dict[str, Any]], tuple[bool, dict[str, Any], str]]


@dataclass(frozen=True, slots=True)
class AssertionOutcome:
    passed: bool
    check: str
    at_frame: int
    actual: dict[str, Any]
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "at_frame": self.at_frame,
            "check": self.check,
            "passed": self.passed,
            "actual": self.actual,
            "message": self.message,
        }


def evaluate_assertion(scene: PlayScene, spec: AssertionSpec, frame: int) -> AssertionOutcome:
    evaluator = _EVALUATORS.get(spec.type)
    if evaluator is None:
        return AssertionOutcome(
            passed=False,
            check=spec.type,
            at_frame=frame,
            actual={},
            message=f"Tipo de aserción desconocido: {spec.type!r}.",
        )
    try:
        passed, actual, message = evaluator(scene, dict(spec.params))
    except (KeyError, TypeError, ValueError) as exc:
        return AssertionOutcome(
            passed=False,
            check=spec.type,
            at_frame=frame,
            actual={},
            message=f"Parámetros de aserción inválidos: {exc}",
        )
    return AssertionOutcome(
        passed=passed,
        check=spec.type,
        at_frame=frame,
        actual=actual,
        message=message,
    )


def _player_position(scene: PlayScene, params: dict[str, Any]) -> tuple[bool, dict[str, Any], str]:
    expected = params.get("expected")
    if not isinstance(expected, dict):
        raise ValueError("'expected' debe ser {'x': ..., 'y': ...}.")
    target_x = float(expected["x"])
    target_y = float(expected["y"])
    tolerance = float(params.get("tolerance", 2.0))
    position = scene.player.position
    distance = ((position.x - target_x) ** 2 + (position.y - target_y) ** 2) ** 0.5
    actual = {
        "x": round(position.x, 3),
        "y": round(position.y, 3),
        "distance": round(distance, 3),
    }
    return distance <= tolerance, actual, f"Distancia {distance:.2f} px (tolerancia {tolerance})."


def _player_z_above(scene: PlayScene, params: dict[str, Any]) -> tuple[bool, dict[str, Any], str]:
    minimum = float(params.get("min_z", 1.0))
    height = scene.player.z
    return height >= minimum, {"z": round(height, 3)}, f"Altura {height:.2f} (mínimo {minimum})."


def _player_alive(scene: PlayScene, params: dict[str, Any]) -> tuple[bool, dict[str, Any], str]:
    expected = bool(params.get("expected", True))
    alive = scene.player.alive
    return alive is expected, {"alive": alive}, f"alive={alive} (esperado {expected})."


def _no_wall_collision(scene: PlayScene, params: dict[str, Any]) -> tuple[bool, dict[str, Any], str]:
    collides = circle_hits_solid(scene.tilemap, scene.player.position, scene.player.radius)
    return not collides, {"collides": collides}, "El jugador penetra un tile sólido." if collides else "Sin penetración."


def _enemy_dead(scene: PlayScene, params: dict[str, Any]) -> tuple[bool, dict[str, Any], str]:
    enemy_id = params["enemy_id"]
    present = [enemy.id for enemy in scene.enemies if enemy.id == enemy_id]
    return not present, {"enemy_id": enemy_id, "present": bool(present)}, (
        f"El enemigo {enemy_id!r} sigue presente." if present else f"El enemigo {enemy_id!r} no está."
    )


def _any_chest_opened(scene: PlayScene, params: dict[str, Any]) -> tuple[bool, dict[str, Any], str]:
    opened = sorted(scene.chests_opened)
    return bool(opened), {"opened": opened}, f"Cofres abiertos: {len(opened)}."


def _inventory_item_present(
    scene: PlayScene, params: dict[str, Any]
) -> tuple[bool, dict[str, Any], str]:
    item_id = params["item_id"]
    minimum = int(params.get("min_count", 1))
    count = scene.inventory.count(str(item_id))
    return count >= minimum, {"item_id": item_id, "count": count}, (
        f"{item_id}: {count} (mínimo {minimum})."
    )


def _inventory_not_empty(scene: PlayScene, params: dict[str, Any]) -> tuple[bool, dict[str, Any], str]:
    total = scene.inventory.total_quantity
    return total > 0, {"total_quantity": total}, f"Objetos en inventario: {total}."


_EVALUATORS: dict[str, Evaluator] = {
    "player_position": _player_position,
    "player_z_above": _player_z_above,
    "player_alive": _player_alive,
    "no_wall_collision": _no_wall_collision,
    "enemy_dead": _enemy_dead,
    "any_chest_opened": _any_chest_opened,
    "inventory_item_present": _inventory_item_present,
    "inventory_not_empty": _inventory_not_empty,
}
