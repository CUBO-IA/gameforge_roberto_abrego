"""Pruebas de verificación de los entregables de la Misión 006 (Tooling Ecosystem 2D)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REQUIRED_DELIVERABLES = [
    "TOOLING_AUDIT.md",
    "TOOLING_COMPATIBILITY.md",
    "AGENT_TOOL_CATALOG.md",
    "GAME_TEST_RUNNER_DESIGN.md",
    "GRAPHICS_AND_ASSETS_PIPELINE.md",
    "TOOLING_INTEGRATION_PLAN.md",
    "TOOLING_BENCHMARK.md",
]

SECTION_2_TOOLS = [
    "ruff",
    "pyright",
    "pytest",
    "hypothesis",
    "tiled",
    "pytmx",
    "libresprite",
    "pillow",
    "blender",
    "ffmpeg",
    "audacity",
    "krita",
]

MANDATORY_CRITERIA_KEYS = [
    "función principal",
    "repositorio oficial",
    "licencia",
    "actividad y mantenimiento",
    "compatibilidad con python y pygame ce",
    "consumo de recursos",
    "funcionamiento offline",
    "integración con claude code",
    "capacidad de automatización",
    "complejidad de implementación",
    "beneficio real para gameforge",
    "alternativas existentes",
    "veredicto",
]

ADDITIONAL_RESEARCH_AREAS = [
    "generación procedural de mapas",
    "creación de personajes y animaciones",
    "navegación y pathfinding",
    "física y colisiones",
    "sistemas de partículas",
    "iluminación 2d",
    "inteligencia artificial de npc",
    "interfaces de usuario",
    "audio dinámico",
    "pruebas de videojuegos",
]


def test_all_mission_006_deliverables_exist_and_non_trivial() -> None:
    root = Path(__file__).resolve().parents[1]
    for filename in REQUIRED_DELIVERABLES:
        filepath = root / filename
        assert filepath.is_file(), f"Falta el entregable obligatorio: {filename}"
        assert (
            filepath.stat().st_size > 5000
        ), f"El entregable {filename} es demasiado corto o incompleto"


def test_tooling_audit_covers_all_required_tools() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_AUDIT.md").read_text(encoding="utf-8").lower()
    for tool in SECTION_2_TOOLS:
        assert tool in content, f"La herramienta obligatoria '{tool}' no está cubierta en TOOLING_AUDIT.md"


def test_tooling_audit_covers_mandatory_evaluation_criteria() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_AUDIT.md").read_text(encoding="utf-8").lower()
    for criterion in MANDATORY_CRITERIA_KEYS:
        assert (
            criterion in content
        ), f"El criterio de evaluación obligatorio '{criterion}' no está documentado en TOOLING_AUDIT.md"


def test_tooling_audit_covers_additional_research_areas() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_AUDIT.md").read_text(encoding="utf-8").lower()
    for area in ADDITIONAL_RESEARCH_AREAS:
        assert (
            area in content
        ), f"El área especializada '{area}' no está analizada en TOOLING_AUDIT.md"


def test_game_test_runner_design_covers_core_capabilities() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "GAME_TEST_RUNNER_DESIGN.md").read_text(encoding="utf-8").lower()
    expected_capabilities = [
        "headless",
        "virtualinputcontroller",
        "escenario",
        "colision",
        "captura",
        "diff",
        "telemetr",
        "pytest",
    ]
    for cap in expected_capabilities:
        assert cap in content, f"Capacidad clave '{cap}' no cubierta en GAME_TEST_RUNNER_DESIGN.md"


def test_graphics_and_assets_pipeline_covers_formats_and_tools() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "GRAPHICS_AND_ASSETS_PIPELINE.md").read_text(encoding="utf-8").lower()
    assert "gf-anim-v1" in content
    assert "tiled" in content
    assert "pillow" in content
    assert "ffmpeg" in content
    assert "asset_hub" in content


def test_tooling_compatibility_covers_python_and_hardware() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_COMPATIBILITY.md").read_text(encoding="utf-8").lower()
    assert "python 3.14" in content
    assert "pygame-ce" in content
    assert "16.67" in content
    assert "igpu" in content or "intel uhd" in content
    assert "mit" in content


def test_agent_tool_catalog_has_valid_json_schemas() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "AGENT_TOOL_CATALOG.md").read_text(encoding="utf-8")
    json_blocks = re.findall(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    assert len(json_blocks) >= 3, "AGENT_TOOL_CATALOG.md debe incluir esquemas JSON estructurados"
    for block in json_blocks:
        try:
            parsed = json.loads(block)
            assert isinstance(parsed, (dict, list))
        except json.JSONDecodeError as err:
            raise AssertionError(f"Bloque JSON inválido en AGENT_TOOL_CATALOG.md: {err}\n{block}") from err


def test_tooling_benchmark_contains_empirical_measurements() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_BENCHMARK.md").read_text(encoding="utf-8").lower()
    assert "314" in content  # tests medidos
    assert "fps" in content  # headless fps
    assert "blend_sub" in content
    assert "ffmpeg" in content
    assert "limitaciones" in content  # el informe declara sus límites
    assert "2026-11-07" in content  # fecha de medición


def test_tooling_audit_includes_mandatory_final_report() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_AUDIT.md").read_text(encoding="utf-8").lower()
    required_sections = [
        "informe final",
        "10 herramientas más valiosas",
        "no merece la pena incorporar",
        "probar primero",
        "pueden esperar",
        "coste aproximado",
        "riesgos",
        "siguientes pasos",
    ]
    for section in required_sections:
        assert section in content, f"El informe final no cubre '{section}'"


def test_tooling_compatibility_reports_real_pyright_baseline() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_COMPATIBILITY.md").read_text(encoding="utf-8")
    assert "46" in content, "Debe documentarse la línea base real de errores de Pyright"
    assert "game/core" in content, "Debe documentarse el estado de los módulos obligados a cero"
    assert "314" in content, "Debe documentarse el número real de tests"


def test_tooling_integration_plan_has_phased_roadmap() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TOOLING_INTEGRATION_PLAN.md").read_text(encoding="utf-8").lower()
    assert "fase 0" in content
    assert "fase 1" in content
    assert "fase 2" in content
    assert "fase 3" in content
    assert "fase 4" in content
    assert "rollback" in content
