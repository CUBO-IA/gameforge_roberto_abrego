"""Guardado/carga JSON versionado con escritura atómica y validación estricta.

El archivo no se ejecuta nunca: solo se deserializa como datos. Se imponen
límites de tamaño y de colecciones para evitar archivos patológicos.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from game.entities.items import item_exists

SCHEMA_VERSION = 1
MAX_SAVE_BYTES = 512 * 1024
MAX_LIST_ITEMS = 1000
MAX_INVENTORY_SLOTS = 20


class SaveGameError(ValueError):
    """Guardado ausente, corrupto o incompatible."""


@dataclass(frozen=True, slots=True)
class RunSnapshot:
    seed: int
    floor: int
    elapsed: float
    score: int
    kills: int
    player_x: float
    player_y: float
    health: float
    inventory: dict[str, int] = field(default_factory=dict)
    chests_opened: tuple[str, ...] = ()
    defeated: tuple[str, ...] = ()
    altar_activated: bool = False


@dataclass(frozen=True, slots=True)
class SaveData:
    schema_version: int
    saved_at: str
    run: RunSnapshot


def save_run(path: str | Path, snapshot: RunSnapshot) -> None:
    target = Path(path)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "saved_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "run": {
            "seed": snapshot.seed,
            "floor": snapshot.floor,
            "elapsed": round(snapshot.elapsed, 3),
            "score": snapshot.score,
            "kills": snapshot.kills,
            "player": {"x": snapshot.player_x, "y": snapshot.player_y},
            "health": snapshot.health,
            "inventory": dict(sorted(snapshot.inventory.items())),
            "chests_opened": list(snapshot.chests_opened),
            "defeated": list(snapshot.defeated),
            "altar_activated": snapshot.altar_activated,
        },
    }
    # Validar antes de tocar disco: un snapshot inválido no debe sobrescribir
    # una partida buena.
    _validate_payload(payload)

    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=target.parent, prefix=f".{target.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise SaveGameError(f"No se pudo escribir el guardado: {target}") from exc


def load_run(path: str | Path) -> SaveData:
    target = Path(path)
    try:
        size = target.stat().st_size
    except FileNotFoundError as exc:
        raise SaveGameError("No existe ninguna partida guardada.") from exc
    except OSError as exc:
        raise SaveGameError(f"No se pudo acceder al guardado: {target}") from exc
    if size <= 0:
        raise SaveGameError("El guardado está vacío.")
    if size > MAX_SAVE_BYTES:
        raise SaveGameError("El guardado excede el tamaño máximo permitido.")
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SaveGameError("El guardado no es texto UTF-8 legible.") from exc
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SaveGameError(
            f"Guardado corrupto (línea {exc.lineno}): {exc.msg}"
        ) from exc
    except RecursionError as exc:
        raise SaveGameError("El guardado tiene una estructura demasiado anidada.") from exc
    return _validate_payload(raw)


def delete_save(path: str | Path) -> bool:
    target = Path(path)
    try:
        target.unlink()
        return True
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise SaveGameError(f"No se pudo borrar el guardado: {target}") from exc


def save_slot(data_dir: str | Path, slot: int, snapshot: RunSnapshot) -> Path:
    """Guarda una partida en una ranura específica (1..3 por defecto)."""
    from game.persistence.paths import save_file

    path = save_file(data_dir, slot)
    save_run(path, snapshot)
    return path


def load_slot(data_dir: str | Path, slot: int) -> SaveData:
    """Carga la partida de una ranura específica."""
    from game.persistence.paths import save_file

    path = save_file(data_dir, slot)
    return load_run(path)


def delete_slot(data_dir: str | Path, slot: int) -> bool:
    """Elimina la partida de una ranura específica."""
    from game.persistence.paths import save_file

    path = save_file(data_dir, slot)
    return delete_save(path)


def list_save_slots(data_dir: str | Path, max_slots: int = 3) -> dict[int, SaveData | None]:
    """Lista las ranuras disponibles con sus metadatos de partida o None si están vacías."""
    from game.persistence.paths import save_file

    slots: dict[int, SaveData | None] = {}
    for slot in range(1, max_slots + 1):
        path = save_file(data_dir, slot)
        if path.is_file():
            try:
                slots[slot] = load_run(path)
            except SaveGameError:
                slots[slot] = None
        else:
            slots[slot] = None
    return slots


def _validate_payload(raw: Any) -> SaveData:
    if not isinstance(raw, dict):
        raise SaveGameError("La raíz del guardado debe ser un objeto.")
    version = raw.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise SaveGameError("Falta schema_version o no es un entero.")
    if version > SCHEMA_VERSION:
        raise SaveGameError(
            f"Guardado creado con una versión más nueva ({version}); "
            f"esta build soporta {SCHEMA_VERSION}."
        )
    if version < SCHEMA_VERSION:
        raise SaveGameError(
            f"Guardado de versión {version} sin migración disponible "
            f"(versión actual {SCHEMA_VERSION})."
        )
    saved_at = raw.get("saved_at")
    if not isinstance(saved_at, str) or len(saved_at) > 64:
        raise SaveGameError("saved_at inválido.")
    run_raw = raw.get("run")
    if not isinstance(run_raw, dict):
        raise SaveGameError("Falta el bloque 'run'.")

    seed = _integer(run_raw, "seed", 0, (1 << 63) - 1)
    floor = _integer(run_raw, "floor", 1, 99)
    elapsed = _number(run_raw, "elapsed", 0.0, 10_000_000.0)
    score = _integer(run_raw, "score", 0, 1_000_000_000)
    kills = _integer(run_raw, "kills", 0, 10_000_000)

    player = run_raw.get("player")
    if not isinstance(player, dict):
        raise SaveGameError("Falta la posición del jugador.")
    player_x = _number(player, "x", 0.0, 1_000_000.0)
    player_y = _number(player, "y", 0.0, 1_000_000.0)
    health = _number(run_raw, "health", 0.01, 1_000_000.0)

    inventory_raw = run_raw.get("inventory", {})
    if not isinstance(inventory_raw, dict) or len(inventory_raw) > MAX_INVENTORY_SLOTS:
        raise SaveGameError("Inventario inválido o demasiado grande.")
    inventory: dict[str, int] = {}
    for item_id, quantity in inventory_raw.items():
        if not isinstance(item_id, str) or not item_exists(item_id):
            raise SaveGameError(f"Objeto desconocido en el guardado: {item_id!r}.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or not (1 <= quantity <= 9999):
            raise SaveGameError("Cantidad de inventario inválida.")
        inventory[item_id] = quantity

    chests = _string_list(run_raw.get("chests_opened", []), "chests_opened")
    defeated = _string_list(run_raw.get("defeated", []), "defeated")
    altar_activated = run_raw.get("altar_activated", False)
    if not isinstance(altar_activated, bool):
        raise SaveGameError("altar_activated debe ser booleano.")

    return SaveData(
        schema_version=version,
        saved_at=saved_at,
        run=RunSnapshot(
            seed=seed,
            floor=floor,
            elapsed=elapsed,
            score=score,
            kills=kills,
            player_x=player_x,
            player_y=player_y,
            health=health,
            inventory=inventory,
            chests_opened=chests,
            defeated=defeated,
            altar_activated=altar_activated,
        ),
    )


def _integer(section: dict[str, Any], key: str, minimum: int, maximum: int) -> int:
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise SaveGameError(f"'{key}' debe ser un entero.")
    if not minimum <= value <= maximum:
        raise SaveGameError(f"'{key}' fuera de rango.")
    return value


def _number(section: dict[str, Any], key: str, minimum: float, maximum: float) -> float:
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SaveGameError(f"'{key}' debe ser numérico.")
    number = float(value)
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise SaveGameError(f"'{key}' fuera de rango.")
    return number


def _string_list(raw: Any, name: str) -> tuple[str, ...]:
    if not isinstance(raw, list):
        raise SaveGameError(f"'{name}' debe ser una lista.")
    if len(raw) > MAX_LIST_ITEMS:
        raise SaveGameError(f"'{name}' contiene demasiados elementos.")
    result: list[str] = []
    seen: set[str] = set()
    for value in raw:
        if not isinstance(value, str) or not (1 <= len(value) <= 40):
            raise SaveGameError(f"Elemento inválido en '{name}'.")
        if value in seen:
            raise SaveGameError(f"Elemento duplicado en '{name}'.")
        seen.add(value)
        result.append(value)
    return tuple(result)
