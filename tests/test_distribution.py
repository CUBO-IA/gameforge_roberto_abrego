"""Pruebas de verificación de distribución y empaquetado (Fase 5)."""

from __future__ import annotations

from pathlib import Path

from game.__main__ import main
from game.core.config import load_config
from game.entities.enemy_catalog import load_enemy_catalog
from game.sim.crafting import load_recipes
from game.sim.quest import load_quest_catalog
from tools.build_dist import check_packaging_prerequisites


def test_packaging_prerequisites() -> None:
    assert check_packaging_prerequisites() is True


def test_cli_entrypoint_callable() -> None:
    assert callable(main)


def test_spec_file_validity() -> None:
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "gameforge.spec"
    assert spec_path.is_file()
    content = spec_path.read_text(encoding="utf-8")
    assert "game/data" in content
    assert "gameforge" in content


def test_all_data_catalogs_load_successfully() -> None:
    config = load_config()
    assert config.window.width > 0

    enemies = load_enemy_catalog()
    assert len(enemies) >= 3

    quests = load_quest_catalog()
    assert len(quests) >= 5

    recipes = load_recipes()
    assert len(recipes) >= 3
