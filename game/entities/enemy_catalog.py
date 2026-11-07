"""Catálogo data-driven de enemigos: nombre, comportamiento y parámetros.

El balance numérico (salud, velocidad, daño) vive en config.json
(``GameConfig.enemies``); este catálogo define el significado de cada tipo:
qué comportamiento ejecuta la FSM genérica y con qué parámetros.

Añadir un nuevo tipo de enemigo con un comportamiento existente solo exige
una entrada aquí y sus estadísticas en config.json; no hay que escribir código.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "enemies.json"

KNOWN_BEHAVIORS = ("melee", "ranged", "charger")

# Parámetros válidos por comportamiento. Todo parámetro es un número finito.
_ALLOWED_PARAMS: dict[str, frozenset[str]] = {
    "melee": frozenset({"wobble_amplitude", "wobble_frequency"}),
    "ranged": frozenset(
        {"far_distance", "near_distance", "move_scale", "projectile_bonus", "origin_offset"}
    ),
    "charger": frozenset(
        {
            "windup_time",
            "charge_time",
            "charge_speed_scale",
            "recover_time",
            "charge_cooldown",
            "min_charge_distance",
        }
    ),
}

_DEFAULT_PARAMS: dict[str, dict[str, float]] = {
    "melee": {"wobble_amplitude": 0.0, "wobble_frequency": 6.0},
    "ranged": {
        "far_distance": 250.0,
        "near_distance": 140.0,
        "move_scale": 0.55,
        "projectile_bonus": 4.0,
        "origin_offset": 4.0,
    },
    "charger": {
        "windup_time": 0.55,
        "charge_time": 0.42,
        "charge_speed_scale": 4.0,
        "recover_time": 0.7,
        "charge_cooldown": 2.4,
        "min_charge_distance": 30.0,
    },
}


class CatalogError(RuntimeError):
    """El catálogo de enemigos es inválido o no se puede leer."""


@dataclass(frozen=True, slots=True)
class EnemyDefinition:
    kind: str
    name: str
    behavior: str
    params: Mapping[str, float]

    def param(self, key: str) -> float:
        """Parámetro con valor por defecto según el comportamiento."""
        try:
            return float(self.params[key])
        except KeyError:
            return _DEFAULT_PARAMS[self.behavior][key]


def load_enemy_catalog(path: str | Path | None = None) -> dict[str, EnemyDefinition]:
    """Carga y valida el catálogo. Errores explícitos, nunca silenciosos."""
    file_path = Path(path) if path is not None else CATALOG_PATH
    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CatalogError(f"No se pudo leer {file_path}: {exc}") from exc
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise CatalogError(f"JSON inválido en {file_path}: {exc}") from exc
    return _parse_catalog(data)


def _parse_catalog(data: object) -> dict[str, EnemyDefinition]:
    if not isinstance(data, dict):
        raise CatalogError("El catálogo debe ser un objeto JSON.")
    if data.get("schema_version") != 1:
        raise CatalogError(f"schema_version desconocida: {data.get('schema_version')!r}")
    kinds = data.get("kinds")
    if not isinstance(kinds, dict) or not kinds:
        raise CatalogError("El catálogo debe definir al menos un tipo en 'kinds'.")
    catalog: dict[str, EnemyDefinition] = {}
    for kind, entry in kinds.items():
        if not isinstance(kind, str) or not kind or not isinstance(entry, dict):
            raise CatalogError(f"Entrada inválida para el tipo {kind!r}.")
        name = entry.get("name")
        behavior = entry.get("behavior")
        params = entry.get("params", {})
        if not isinstance(name, str) or not name.strip():
            raise CatalogError(f"{kind}: 'name' debe ser texto no vacío.")
        if behavior not in KNOWN_BEHAVIORS:
            raise CatalogError(
                f"{kind}: behavior {behavior!r} desconocido. Válidos: {KNOWN_BEHAVIORS}."
            )
        if not isinstance(params, dict):
            raise CatalogError(f"{kind}: 'params' debe ser un objeto.")
        allowed = _ALLOWED_PARAMS[behavior]
        for key, value in params.items():
            if key not in allowed:
                raise CatalogError(f"{kind}: parámetro {key!r} no válido para {behavior!r}.")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise CatalogError(f"{kind}: el parámetro {key!r} debe ser numérico.")
        catalog[kind] = EnemyDefinition(
            kind=kind, name=name, behavior=behavior, params=dict(params)
        )
    return catalog


# Catálogo del juego, cargado una sola vez (dato de solo lectura, como TILE_DEFS).
ENEMY_CATALOG: dict[str, EnemyDefinition] = load_enemy_catalog()


def definition_for(kind: str) -> EnemyDefinition:
    """Definición del tipo; los tipos no catalogados caen a melee por defecto."""
    definition = ENEMY_CATALOG.get(kind)
    if definition is not None:
        return definition
    return EnemyDefinition(kind=kind, name=kind, behavior="melee", params={})
