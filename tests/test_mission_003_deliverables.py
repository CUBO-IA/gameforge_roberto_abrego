"""Pruebas de verificación de los entregables de la Misión 003 (Asset Ecosystem & GameForge Asset Hub)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REQUIRED_DELIVERABLES = [
    "ASSET_HUB_RESEARCH.md",
    "ASSET_CATALOG_SCHEMA.md",
    "CHARACTER_ASSET_PIPELINE.md",
    "MAP_AND_TILESET_PIPELINE.md",
    "UI_ASSET_PIPELINE.md",
    "LICENSE_PROVENANCE_SYSTEM.md",
    "ASSET_HUB_ARCHITECTURE.md",
]

REQUIRED_SOURCES = [
    "shorepine/kenney",
    "liberatedpixelcup",
    "lpc-style-guide",
    "tiddybub/2d-assets",
    "eturner58/game-assets",
    "kenney.nl",
    "opengameart.org",
]

REQUIRED_RESEARCH_AREAS = [
    "personajes y sus animaciones",
    "spritesheets y atlas",
    "mapas y tilesets",
    "npc y criaturas",
    "armas, objetos y equipamiento",
    "iconos y componentes de interfaz",
    "hud, inventario, menús y ventanas",
    "efectos visuales",
    "formatos y metadatos",
    "licencias y procedencia",
]


def test_all_mission_003_deliverables_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for filename in REQUIRED_DELIVERABLES:
        filepath = root / filename
        assert filepath.is_file(), f"Falta el entregable obligatorio: {filename}"
        assert filepath.stat().st_size > 5000, f"El entregable {filename} es demasiado corto o incompleto"


def test_required_sources_covered_in_research() -> None:
    root = Path(__file__).resolve().parents[1]
    research_content = (root / "ASSET_HUB_RESEARCH.md").read_text(encoding="utf-8").lower()
    for source in REQUIRED_SOURCES:
        assert source in research_content, f"La fuente requerida '{source}' no está analizada en ASSET_HUB_RESEARCH.md"


def test_all_ten_research_areas_covered() -> None:
    root = Path(__file__).resolve().parents[1]
    research_content = (root / "ASSET_HUB_RESEARCH.md").read_text(encoding="utf-8").lower()
    for area in REQUIRED_RESEARCH_AREAS:
        assert area in research_content, f"El área de investigación '{area}' no está cubierta en ASSET_HUB_RESEARCH.md"


def test_agent_requirement_explicitly_addressed() -> None:
    root = Path(__file__).resolve().parents[1]
    arch_content = (root / "ASSET_HUB_ARCHITECTURE.md").read_text(encoding="utf-8").lower()
    assert "humanoide" in arch_content
    assert "32x32" in arch_content
    assert "walk" in arch_content
    assert "attack" in arch_content
    assert "hurt" in arch_content
    assert "match_score" in arch_content


def test_asset_catalog_json_blocks_are_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    schema_doc = (root / "ASSET_CATALOG_SCHEMA.md").read_text(encoding="utf-8")

    # Extraer bloques ```json ... ```
    json_blocks = re.findall(r"```json\s+(.*?)\s+```", schema_doc, re.DOTALL)
    assert len(json_blocks) >= 4, "Debe haber al menos 4 bloques JSON en ASSET_CATALOG_SCHEMA.md"

    for i, block in enumerate(json_blocks):
        try:
            parsed = json.loads(block)
            assert isinstance(parsed, dict), f"El bloque JSON {i} no es un objeto válido"
        except json.JSONDecodeError as err:
            raise AssertionError(f"Bloque JSON {i} en ASSET_CATALOG_SCHEMA.md es inválido: {err}") from err
