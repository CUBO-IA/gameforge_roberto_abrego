"""Rutas de datos de usuario, sin escribir dentro del repositorio."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "GameForge"


def resolve_data_dir(override: str | Path | None = None) -> Path:
    if override is not None:
        return Path(override).expanduser().resolve()
    env_value = os.environ.get("GAMEFORGE_DATA_DIR")
    if env_value:
        return Path(env_value).expanduser().resolve()
    home = Path.home()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        root = Path(base) if base else home / "AppData" / "Local"
    elif sys.platform == "darwin":
        root = home / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    return (root / APP_DIR_NAME).resolve()


def save_file(data_dir: str | Path, slot: int = 1) -> Path:
    if slot < 1 or slot > 9:
        raise ValueError("El slot debe estar comprendido entre 1 y 9.")
    return Path(data_dir) / f"slot{slot}.json"


def scores_file(data_dir: str | Path) -> Path:
    return Path(data_dir) / "scores.sqlite3"
