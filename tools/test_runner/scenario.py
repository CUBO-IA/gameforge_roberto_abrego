"""Definición declarativa de escenarios de prueba (JSON) del GF-TR.

Un escenario describe semilla, estado inicial, línea temporal de entradas y
aserciones. El cargador valida todo antes de ejecutar para que un JSON
malformado falle con un mensaje claro en lugar de a mitad de la partida.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SUPPORTED_ACTIONS = {"press", "release", "tap", "move", "click"}

SUPPORTED_ASSERTIONS = {
    "player_position": "Posición del jugador con tolerancia en píxeles.",
    "player_z_above": "Altura 2.5D mínima alcanzada en el frame.",
    "player_alive": "El jugador sigue vivo (o muerto, si se espera ``false``).",
    "no_wall_collision": "El círculo del jugador no penetra ningún tile sólido.",
    "enemy_dead": "Un enemigo concreto ya no está en la escena.",
    "any_chest_opened": "Se ha abierto al menos un cofre.",
    "inventory_item_present": "El inventario contiene al menos N unidades.",
    "inventory_not_empty": "El inventario tiene al menos un objeto.",
}


class ScenarioError(ValueError):
    """Escenario inválido o incompatible con el runner."""


@dataclass(frozen=True, slots=True)
class TimelineEntry:
    frame: int
    action: str
    key: str | None = None
    vector: tuple[float, float] | None = None
    button: int = 1
    position: tuple[int, int] | None = None


@dataclass(frozen=True, slots=True)
class AssertionSpec:
    at_frame: int
    type: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VisualSpec:
    capture_at_frames: tuple[int, ...] = ()
    max_allowed_pixel_diff_ratio: float = 0.0005


@dataclass(frozen=True, slots=True)
class Scenario:
    id: str
    description: str
    seed: int
    timeout_frames: int
    initial_state: dict[str, Any]
    timeline: tuple[TimelineEntry, ...]
    assertions: tuple[AssertionSpec, ...]
    visual: VisualSpec | None = None
    source: Path | None = None


def load_scenario(path: str | Path) -> Scenario:
    file_path = Path(path)
    if not file_path.is_file():
        raise ScenarioError(f"No existe el escenario: {file_path}")
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScenarioError(f"JSON inválido en {file_path}: {exc}") from exc
    return scenario_from_dict(data, source=file_path)


def scenario_from_dict(data: object, source: Path | None = None) -> Scenario:
    if not isinstance(data, dict):
        raise ScenarioError("El escenario debe ser un objeto JSON.")

    scenario_id = data.get("id")
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise ScenarioError("El escenario necesita un 'id' no vacío.")

    config = data.get("config", {})
    if not isinstance(config, dict):
        raise ScenarioError("'config' debe ser un objeto.")

    seed = config.get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ScenarioError("'config.seed' es obligatorio y debe ser un entero.")

    timeout = config.get("timeout_frames", 600)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ScenarioError("'config.timeout_frames' debe ser un entero positivo.")

    initial_state = data.get("initial_state", {})
    if not isinstance(initial_state, dict):
        raise ScenarioError("'initial_state' debe ser un objeto.")

    timeline = tuple(
        _parse_timeline_entry(entry, index, timeout)
        for index, entry in enumerate(_as_list(data.get("input_timeline", []), "input_timeline"))
    )
    assertions = tuple(
        _parse_assertion(entry, index, timeout)
        for index, entry in enumerate(_as_list(data.get("assertions", []), "assertions"))
    )

    visual_data = data.get("visual_validation")
    visual: VisualSpec | None = None
    if visual_data is not None:
        if not isinstance(visual_data, dict):
            raise ScenarioError("'visual_validation' debe ser un objeto.")
        frames = visual_data.get("capture_at_frames", [])
        ratio = visual_data.get("max_allowed_pixel_diff_ratio", 0.0005)
        if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or not 0 <= ratio <= 1:
            raise ScenarioError("'max_allowed_pixel_diff_ratio' debe estar entre 0 y 1.")
        parsed_frames = tuple(_positive_int(frame, "capture_at_frames") for frame in _as_list(frames, "capture_at_frames"))
        visual = VisualSpec(
            capture_at_frames=parsed_frames,
            max_allowed_pixel_diff_ratio=float(ratio),
        )

    description = data.get("description", "")
    if not isinstance(description, str):
        raise ScenarioError("'description' debe ser texto.")

    return Scenario(
        id=scenario_id.strip(),
        description=description,
        seed=seed,
        timeout_frames=timeout,
        initial_state=initial_state,
        timeline=timeline,
        assertions=assertions,
        visual=visual,
        source=source,
    )


def _parse_timeline_entry(entry: object, index: int, timeout: int) -> TimelineEntry:
    if not isinstance(entry, dict):
        raise ScenarioError(f"input_timeline[{index}] debe ser un objeto.")
    frame = _positive_int(entry.get("frame"), f"input_timeline[{index}].frame")
    if frame > timeout:
        raise ScenarioError(f"input_timeline[{index}].frame={frame} supera timeout_frames={timeout}.")
    action = entry.get("action")
    if action not in SUPPORTED_ACTIONS:
        raise ScenarioError(
            f"input_timeline[{index}].action={action!r} no soportada; "
            f"usa una de {sorted(SUPPORTED_ACTIONS)}."
        )

    key: str | None = None
    vector: tuple[float, float] | None = None
    button = 1
    position: tuple[int, int] | None = None

    if action in {"press", "release", "tap"}:
        raw_key = entry.get("key")
        if not isinstance(raw_key, str) or not raw_key:
            raise ScenarioError(f"input_timeline[{index}] ({action}) requiere 'key'.")
        key = raw_key
    elif action == "move":
        raw_vector = entry.get("vector")
        if (
            not isinstance(raw_vector, list)
            or len(raw_vector) != 2
            or not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in raw_vector)
        ):
            raise ScenarioError(f"input_timeline[{index}] (move) requiere 'vector' [x, y].")
        vector = (float(raw_vector[0]), float(raw_vector[1]))
    else:  # click
        raw_button = entry.get("button", 1)
        if not isinstance(raw_button, int) or isinstance(raw_button, bool):
            raise ScenarioError(f"input_timeline[{index}].button debe ser entero.")
        button = raw_button
        raw_position = entry.get("position")
        if raw_position is not None:
            if (
                not isinstance(raw_position, list)
                or len(raw_position) != 2
                or not all(isinstance(value, int) and not isinstance(value, bool) for value in raw_position)
            ):
                raise ScenarioError(f"input_timeline[{index}].position debe ser [x, y].")
            position = (int(raw_position[0]), int(raw_position[1]))

    return TimelineEntry(
        frame=frame,
        action=action,
        key=key,
        vector=vector,
        button=button,
        position=position,
    )


def _parse_assertion(entry: object, index: int, timeout: int) -> AssertionSpec:
    if not isinstance(entry, dict):
        raise ScenarioError(f"assertions[{index}] debe ser un objeto.")
    frame = _positive_int(entry.get("at_frame"), f"assertions[{index}].at_frame")
    if frame > timeout:
        raise ScenarioError(f"assertions[{index}].at_frame={frame} supera timeout_frames={timeout}.")
    assertion_type = entry.get("type")
    if assertion_type not in SUPPORTED_ASSERTIONS:
        raise ScenarioError(
            f"assertions[{index}].type={assertion_type!r} no soportada; "
            f"usa una de {sorted(SUPPORTED_ASSERTIONS)}."
        )
    params = {
        key: value
        for key, value in entry.items()
        if key not in {"at_frame", "type"}
    }
    return AssertionSpec(at_frame=frame, type=str(assertion_type), params=params)


def _as_list(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise ScenarioError(f"'{field_name}' debe ser una lista.")
    return value


def _positive_int(value: object, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ScenarioError(f"'{field_name}' debe ser un entero >= 1.")
    return value
