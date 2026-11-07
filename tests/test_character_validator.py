"""Pruebas unitarias para la herramienta de validación de personajes (tools/validate_character.py)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.validate_character import validate_character_manifest


def test_validator_on_canonical_manifest() -> None:
    manifest_path = Path("assets/sprites/characters/player/knight_hero.anim.json")
    errors = validate_character_manifest(manifest_path)
    assert errors == [], f"El archivo canónico produjo errores inesperados: {errors}"


def test_validator_detects_missing_fields_and_overflow(tmp_path: Path) -> None:
    # 1. Crear un atlas falso temporal
    dummy_atlas = tmp_path / "mock_atlas.png"
    dummy_atlas.write_bytes(b"dummy image data")

    # 2. Manifiesto con desborde de rect y clips faltantes
    bad_data = {
        "version": "gf-anim-v1",
        "metadata": {
            "id": "bad_character",
            "display_name": "Test",
            "rig_type": "frame_by_frame",
        },
        "texture": {
            "image_path": "mock_atlas.png",
            "width": 64,
            "height": 64,
        },
        "frames": [
            {
                "id": "f0",
                "rect": [0, 0, 100, 100],  # Desborda 64x64
                "pivot": [16, 16],
            }
        ],
        "clips": {
            "idle": {
                "frames": ["f0", "f_inexistente"],  # Referencia huérfana
            }
            # Faltan 'walk', 'hurt', 'die'
        },
    }

    bad_manifest = tmp_path / "bad.anim.json"
    bad_manifest.write_text(json.dumps(bad_data), encoding="utf-8")

    errors = validate_character_manifest(bad_manifest)
    assert len(errors) >= 4
    error_text = " ".join(errors)
    assert "desborda el atlas" in error_text
    assert "referencia un fotograma inexistente" in error_text
    assert "Falta el clip obligatorio 'walk'" in error_text
    assert "Falta el clip obligatorio 'die'" in error_text
