"""Configuración común de pytest: SDL headless y rutas del proyecto."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from game.core.config import GameConfig, load_config  # noqa: E402


@pytest.fixture(scope="session")
def default_config() -> GameConfig:
    return load_config()


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "gameforge-data"
    directory.mkdir()
    return directory
