"""Pruebas de verificación de los entregables de la Misión 002 (Sprites, Animación y Lógica)."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_DELIVERABLES = [
    "SPRITE_PIPELINE_RESEARCH.md",
    "ANIMATION_SYSTEM_PROPOSAL.md",
    "CHARACTER_CONTROLLER_ARCHITECTURE.md",
    "ANIMATION_FORMAT_SPEC.md",
    "VISUAL_EFFECTS_ARCHITECTURE.md",
    "AGENT_ANIMATION_WORKFLOW.md",
    "LICENSE_AND_DEPENDENCY_AUDIT.md",
]

INVESTIGATED_TARGETS = [
    "skelform",
    "PySpine",
    "transitions",
    "py_trees",
    "pygame-ce",
    "HitBox",
    "rsheet",
]


def test_all_mission_002_deliverables_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for filename in REQUIRED_DELIVERABLES:
        filepath = root / filename
        assert filepath.is_file(), f"Falta el entregable obligatorio: {filename}"
        assert filepath.stat().st_size > 2000, f"El entregable {filename} es demasiado corto o incompleto"


def test_investigated_repositories_covered_in_audit_and_proposals() -> None:
    root = Path(__file__).resolve().parents[1]
    audit_content = (root / "LICENSE_AND_DEPENDENCY_AUDIT.md").read_text(encoding="utf-8")
    anim_content = (root / "ANIMATION_SYSTEM_PROPOSAL.md").read_text(encoding="utf-8")
    sprite_content = (root / "SPRITE_PIPELINE_RESEARCH.md").read_text(encoding="utf-8")
    logic_content = (root / "CHARACTER_CONTROLLER_ARCHITECTURE.md").read_text(encoding="utf-8")

    combined = f"{audit_content}\n{anim_content}\n{sprite_content}\n{logic_content}"

    for target in INVESTIGATED_TARGETS:
        assert target.lower() in combined.lower(), (
            f"El repositorio o herramienta requerida '{target}' no está analizado en la documentación"
        )


def test_sprite_pipeline_research_covers_core_concepts() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "SPRITE_PIPELINE_RESEARCH.md").read_text(encoding="utf-8")
    assert "rsheet" in content
    assert "subsurface" in content
    assert "convert_alpha" in content
    assert "pivote" in content.lower() or "pivot" in content.lower()
    assert "paperdoll" in content.lower() or "multicapa" in content.lower()
    assert "jittering" in content.lower()


def test_animation_proposal_covers_skeletal_and_traditional() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "ANIMATION_SYSTEM_PROPOSAL.md").read_text(encoding="utf-8")
    assert "skelform" in content.lower()
    assert "pyspine" in content.lower()
    assert "cinemática inversa" in content.lower() or "ik" in content.lower()
    assert "deformación de mallas" in content.lower() or "mesh" in content.lower()
    assert "animationclip" in content.lower()
    assert "hitbox" in content.lower()


def test_character_controller_covers_fsm_and_bt() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "CHARACTER_CONTROLLER_ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "hfsm" in content.lower() or "máquina de estados" in content.lower()
    assert "behaviortree" in content.lower() or "árbol de comportamiento" in content.lower()
    assert "blackboard" in content.lower()
    assert "input buffer" in content.lower()
    assert "coyote time" in content.lower()
    assert "pushbox" in content.lower()
    assert "hurtbox" in content.lower()
    assert "hitbox" in content.lower()


def test_animation_format_spec_has_valid_json_examples() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "ANIMATION_FORMAT_SPEC.md").read_text(encoding="utf-8")

    # Extraer bloques JSON del documento
    import re

    json_blocks = re.findall(r"```json\s*(\{[\s\S]*?\})\s*```", content)
    assert len(json_blocks) >= 2, "Debe haber al menos 2 bloques JSON (esquema y ejemplo)"

    for i, block in enumerate(json_blocks):
        try:
            parsed = json.loads(block)
            assert isinstance(parsed, dict)
        except json.JSONDecodeError as err:
            raise AssertionError(f"El bloque JSON {i} en ANIMATION_FORMAT_SPEC.md no es JSON válido: {err}") from err


def test_visual_effects_covers_juice_and_particles() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "VISUAL_EFFECTS_ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "particlepool" in content.lower() or "object pool" in content.lower()
    assert "trauma" in content.lower()
    assert "hitstop" in content.lower() or "freeze frame" in content.lower()
    assert "flash-hit" in content.lower() or "silueta" in content.lower()


def test_agent_workflow_covers_all_eight_steps() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "AGENT_ANIMATION_WORKFLOW.md").read_text(encoding="utf-8")
    for step_num in range(1, 9):
        assert f"Paso {step_num}" in content, f"Falta el Paso {step_num} en AGENT_ANIMATION_WORKFLOW.md"
    assert "tools/validate_character.py" in content
    assert "tools/preview_animation.py" in content


def test_license_audit_covers_all_critical_licenses() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "LICENSE_AND_DEPENDENCY_AUDIT.md").read_text(encoding="utf-8")
    assert "lgpl" in content.lower()
    assert "mit" in content.lower()
    assert "bsd" in content.lower()
    assert "esoteric software" in content.lower() or "spine" in content.lower()
    assert "runtime" in content.lower()
    assert "offline" in content.lower() or "desarrollo" in content.lower()
