"""Configuración tipada y validada.

Los valores viven en ``game/data/config.json`` para poder ajustar el balance sin
tocar código. Este módulo no importa pygame a propósito: los tests de dominio
pueden cargar la configuración sin inicializar vídeo.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "config.json"


class ConfigError(ValueError):
    """Configuración ausente, ilegible o fuera de rango."""


@dataclass(frozen=True, slots=True)
class WindowConfig:
    width: int = 1280
    height: int = 720
    fps: int = 60
    title: str = "GAMEFORGE: La Fragua Olvidada"


@dataclass(frozen=True, slots=True)
class PlayerConfig:
    speed: float = 205.0
    max_health: float = 100.0
    radius: float = 12.0
    attack_damage: float = 26.0
    attack_range: float = 62.0
    attack_arc: float = 100.0
    attack_cooldown: float = 0.38
    dash_speed: float = 560.0
    dash_duration: float = 0.16
    dash_cooldown: float = 1.1
    invulnerability: float = 0.75
    potion_heal: float = 45.0


@dataclass(frozen=True, slots=True)
class DungeonConfig:
    width: int = 64
    height: int = 48
    tile_size: int = 32
    rooms: int = 11
    min_room: int = 6
    max_room: int = 10
    chests: int = 5
    shards_required: int = 3
    enemies_per_room: int = 3
    placement_attempts: int = 80


@dataclass(frozen=True, slots=True)
class EnemyStats:
    health: float
    speed: float
    radius: float
    touch_damage: float
    score: int
    attack_range: float = 0.0
    shoot_cooldown: float = 0.0
    projectile_speed: float = 0.0


@dataclass(frozen=True, slots=True)
class AudioConfig:
    master_volume: float = 0.55


DEFAULT_ENEMIES: dict[str, EnemyStats] = {
    "slime": EnemyStats(health=42, speed=74, radius=15, touch_damage=8, score=15),
    "wisp": EnemyStats(
        health=30,
        speed=88,
        radius=13,
        touch_damage=6,
        score=25,
        attack_range=340,
        shoot_cooldown=2.1,
        projectile_speed=215,
    ),
    "brute": EnemyStats(
        health=110,
        speed=66,
        radius=21,
        touch_damage=16,
        score=55,
        attack_range=300,
    ),
}


@dataclass(frozen=True, slots=True)
class GameConfig:
    window: WindowConfig = field(default_factory=WindowConfig)
    player: PlayerConfig = field(default_factory=PlayerConfig)
    dungeon: DungeonConfig = field(default_factory=DungeonConfig)
    enemies: dict[str, EnemyStats] = field(default_factory=lambda: dict(DEFAULT_ENEMIES))
    audio: AudioConfig = field(default_factory=AudioConfig)

    @classmethod
    def from_dict(cls, raw: Any) -> "GameConfig":
        if not isinstance(raw, dict):
            raise ConfigError("La raíz de config.json debe ser un objeto JSON.")

        window_raw = _section(raw, "window")
        player_raw = _section(raw, "player")
        dungeon_raw = _section(raw, "dungeon")
        audio_raw = _section(raw, "audio")
        enemies_raw = raw.get("enemies", {})

        window = WindowConfig(
            width=_int(window_raw, "width", 1280, 320, 3840),
            height=_int(window_raw, "height", 720, 240, 2160),
            fps=_int(window_raw, "fps", 60, 30, 240),
            # `WindowConfig.title` es un descriptor con slots=True: hay que
            # leer el valor desde una instancia para obtener el texto real.
            title=_text(window_raw, "title", WindowConfig().title, max_length=80),
        )
        player = PlayerConfig(
            speed=_number(player_raw, "speed", 205.0, 10.0, 1000.0),
            max_health=_number(player_raw, "max_health", 100.0, 1.0, 10000.0),
            radius=_number(player_raw, "radius", 12.0, 4.0, 64.0),
            attack_damage=_number(player_raw, "attack_damage", 26.0, 1.0, 1000.0),
            attack_range=_number(player_raw, "attack_range", 62.0, 8.0, 500.0),
            attack_arc=_number(player_raw, "attack_arc", 100.0, 1.0, 360.0),
            attack_cooldown=_number(player_raw, "attack_cooldown", 0.38, 0.02, 10.0),
            dash_speed=_number(player_raw, "dash_speed", 560.0, 10.0, 2000.0),
            dash_duration=_number(player_raw, "dash_duration", 0.16, 0.02, 2.0),
            dash_cooldown=_number(player_raw, "dash_cooldown", 1.1, 0.0, 20.0),
            invulnerability=_number(player_raw, "invulnerability", 0.75, 0.0, 10.0),
            potion_heal=_number(player_raw, "potion_heal", 45.0, 0.0, 1000.0),
        )
        dungeon = DungeonConfig(
            width=_int(dungeon_raw, "width", 64, 16, 256),
            height=_int(dungeon_raw, "height", 48, 16, 256),
            tile_size=_int(dungeon_raw, "tile_size", 32, 8, 128),
            rooms=_int(dungeon_raw, "rooms", 11, 2, 40),
            min_room=_int(dungeon_raw, "min_room", 6, 3, 30),
            max_room=_int(dungeon_raw, "max_room", 10, 3, 30),
            chests=_int(dungeon_raw, "chests", 5, 1, 20),
            shards_required=_int(dungeon_raw, "shards_required", 3, 1, 20),
            enemies_per_room=_int(dungeon_raw, "enemies_per_room", 3, 0, 20),
            placement_attempts=_int(dungeon_raw, "placement_attempts", 80, 5, 1000),
        )
        if dungeon.min_room > dungeon.max_room:
            raise ConfigError("dungeon.min_room no puede ser mayor que max_room.")
        if dungeon.shards_required > dungeon.chests:
            raise ConfigError("dungeon.shards_required no puede superar dungeon.chests.")
        if 2 * dungeon.max_room + 4 > min(dungeon.width, dungeon.height):
            raise ConfigError("Las salas no caben en el tamaño de mapa configurado.")

        audio = AudioConfig(
            master_volume=_number(audio_raw, "master_volume", 0.55, 0.0, 1.0),
        )
        enemies = _parse_enemies(enemies_raw)
        return cls(window=window, player=player, dungeon=dungeon, enemies=enemies, audio=audio)


def _section(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key, {})
    if not isinstance(value, dict):
        raise ConfigError(f"'{key}' debe ser un objeto JSON.")
    return value


def _number(
    section: dict[str, Any], key: str, default: float, minimum: float, maximum: float
) -> float:
    value = section.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"'{key}' debe ser numérico.")
    number = float(value)
    if not math.isfinite(number) or not (minimum <= number <= maximum):
        raise ConfigError(f"'{key}' debe estar entre {minimum} y {maximum}.")
    return number


def _int(
    section: dict[str, Any], key: str, default: int, minimum: int, maximum: int
) -> int:
    number = _number(section, key, float(default), float(minimum), float(maximum))
    if number != int(number):
        raise ConfigError(f"'{key}' debe ser un entero.")
    return int(number)


def _text(section: dict[str, Any], key: str, default: str, max_length: int) -> str:
    value = section.get(key, default)
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ConfigError(f"'{key}' debe ser texto no vacío de hasta {max_length} caracteres.")
    return value


def _parse_enemies(raw: Any) -> dict[str, EnemyStats]:
    if not isinstance(raw, dict):
        raise ConfigError("'enemies' debe ser un objeto JSON.")
    result = dict(DEFAULT_ENEMIES)
    for name, values in raw.items():
        if name not in DEFAULT_ENEMIES:
            raise ConfigError(f"Enemigo desconocido en configuración: {name!r}.")
        if not isinstance(values, dict):
            raise ConfigError(f"enemies.{name} debe ser un objeto JSON.")
        base = DEFAULT_ENEMIES[name]
        result[name] = EnemyStats(
            health=_number(values, "health", base.health, 1.0, 100000.0),
            speed=_number(values, "speed", base.speed, 0.0, 2000.0),
            radius=_number(values, "radius", base.radius, 4.0, 100.0),
            touch_damage=_number(values, "touch_damage", base.touch_damage, 0.0, 1000.0),
            score=_int(values, "score", base.score, 0, 100000),
            attack_range=_number(values, "attack_range", base.attack_range, 0.0, 2000.0),
            # Slime/brute no disparan: sus valores por defecto son 0 y deben
            # poder permanecer en 0 aunque el JSON los omita.
            shoot_cooldown=_number(
                values, "shoot_cooldown", base.shoot_cooldown, 0.0, 30.0
            ),
            projectile_speed=_number(
                values, "projectile_speed", base.projectile_speed, 0.0, 1500.0
            ),
        )
    return result


def load_config(path: str | Path | None = None) -> GameConfig:
    """Carga y valida la configuración.

    ``None`` usa el archivo empaquetado. Un error de E/S o JSON se convierte en
    ``ConfigError`` para que la UI pueda mostrarlo sin capturar excepciones
    genéricas.
    """
    config_path = DEFAULT_CONFIG_PATH if path is None else Path(path)
    if not config_path.is_file():
        raise ConfigError(f"No se encontró la configuración: {config_path}")
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"No se pudo leer la configuración: {config_path}") from exc
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"JSON inválido en {config_path.name} (línea {exc.lineno}): {exc.msg}"
        ) from exc
    return GameConfig.from_dict(raw)
