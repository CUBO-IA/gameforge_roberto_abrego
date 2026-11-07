"""Pruebas de verificación de los entregables de investigación arquitectónica."""

from __future__ import annotations

from pathlib import Path

REQUIRED_DELIVERABLES = [
    "REPOSITORY_RESEARCH.md",
    "TECH_STACK_RECOMMENDATION.md",
    "ARCHITECTURE_PROPOSAL.md",
    "DEPENDENCY_AUDIT.md",
    "REUSABLE_ALGORITHMS.md",
]

INVESTIGATED_REPOSITORIES = [
    "pygame-ce",
    "pymunk",
    "esper",
    "Tiled",
    "pytmx",
    "tilemap-generator",
    "python-tcod",
    "py_trees",
    "SolarWolf",
    "pygame-topdownengine",
    "Procedural-Maps",
    "opensimplex-island-generator",
]


def test_all_research_deliverables_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for filename in REQUIRED_DELIVERABLES:
        filepath = root / filename
        assert filepath.is_file(), f"Falta el entregable obligatorio {filename}"
        assert filepath.stat().st_size > 1000, f"El entregable {filename} está incompleto"


def test_repository_research_covers_all_twelve_repos() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "REPOSITORY_RESEARCH.md").read_text(encoding="utf-8")
    for repo in INVESTIGATED_REPOSITORIES:
        assert repo in content, f"El repositorio {repo} no está analizado en REPOSITORY_RESEARCH.md"


def test_tech_stack_recommendation_covers_core_decisions() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "TECH_STACK_RECOMMENDATION.md").read_text(encoding="utf-8")
    assert "pygame-ce" in content
    assert "Python 3.11+" in content
    assert "Spatial Hash" in content
    assert "ADR-002" in content
    assert "Virtual Canvas" in content


def test_architecture_proposal_defines_pure_layers() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "ARCHITECTURE_PROPOSAL.md").read_text(encoding="utf-8")
    assert "core" in content
    assert "world" in content
    assert "entities" in content
    assert "ai" in content
    assert "sim" in content
    assert "scenes" in content
    assert "app" in content
    assert "16.67 ms" in content


def test_dependency_audit_identifies_license_risks() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "DEPENDENCY_AUDIT.md").read_text(encoding="utf-8")
    assert "LGPL-2.1" in content
    assert "LGPL v3" in content
    assert "SIN LICENCIA" in content or "ALL RIGHTS RESERVED" in content
    assert "MIT" in content


def test_reusable_algorithms_specifies_complexity_and_code() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "REUSABLE_ALGORITHMS.md").read_text(encoding="utf-8")
    assert "ALG-01" in content
    assert "ALG-02" in content
    assert "ALG-03" in content
    assert "ALG-04" in content
    assert "ALG-05" in content
    assert "ALG-06" in content
    assert "ALG-07" in content
    assert "ALG-08" in content
    assert "ALG-09" in content
