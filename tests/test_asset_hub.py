"""Suite de pruebas unitarias y de integración para GameForge Asset Hub."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pygame
import pytest

from tools.asset_hub.db import AssetHubDB
from tools.asset_hub.exporter import AssetExporter
from tools.asset_hub.hasher import compute_dhash, compute_sha256, hamming_distance
from tools.asset_hub.previewer import AssetPreviewer
from tools.asset_hub.query import AssetQueryEngine
from tools.asset_hub.validator import AssetValidator


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_hasher_sha256_and_dhash():
    # 1. SHA-256
    data = b"GameForge Asset Hub Test Data"
    sha = compute_sha256(data)
    assert len(sha) == 64
    assert sha == "5a4f4dcdc9a44b92b1521d2a5d030b0bc0efccbecbb5024e229dcd8a95a9629d"

    # 2. dHash y distancia de Hamming
    surf1 = pygame.Surface((32, 32))
    surf1.fill((200, 200, 200))
    h1 = compute_dhash(surf1)
    assert len(h1) == 16

    # Imagen idéntica -> distancia 0
    surf1_clone = surf1.copy()
    h1_clone = compute_dhash(surf1_clone)
    assert hamming_distance(h1, h1_clone) == 0

    # Imagen con gradiente marcado -> distinta
    surf2 = pygame.Surface((32, 32))
    for x in range(32):
        surf2.fill((x * 7, x * 7, x * 7), (x, 0, 1, 32))
    h2 = compute_dhash(surf2)
    assert hamming_distance(h1, h2) > 0


def test_db_crud_in_memory():
    db = AssetHubDB(":memory:")
    assert db.count() == 0

    sample_manifest = {
        "asset_id": "test_knight",
        "name": "Test Knight",
        "kind": "character",
        "taxonomy": {
            "genre": "top_down_rpg",
            "theme": "fantasy_medieval",
            "visual_style": "pixel_art_32x32",
            "tags": ["knight", "melee", "player"]
        },
        "image": {
            "relative_path": "test_knight.png",
            "width": 128,
            "height": 32,
            "has_alpha": True,
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "dhash": "0000000000000000"
        },
        "geometry": {
            "layout_type": "uniform_grid",
            "frame_size": [32, 32]
        },
        "character_data": {
            "directions_supported": ["down"],
            "available_clips": [
                {"name": "walk", "frame_count": 4, "directions": ["down"]},
                {"name": "attack", "frame_count": 3, "directions": ["down"]}
            ]
        },
        "provenance": {
            "author": "Tester",
            "source_repo": "unit_tests",
            "license_spdx": "MIT",
            "license_tier": "tier_1_permissive_attribution"
        }
    }

    db.upsert_asset(sample_manifest, manifest_path="test_knight.asset.json")
    assert db.count() == 1

    retrieved = db.get_asset("test_knight")
    assert retrieved is not None
    assert retrieved["name"] == "Test Knight"
    assert retrieved["character_data"]["available_clips"][0]["name"] == "walk"

    # Búsqueda por SHA256
    found_sha = db.find_by_sha256("abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
    assert found_sha is not None
    assert found_sha["asset_id"] == "test_knight"

    db.close()


def test_agent_query_scenario():
    """Prueba el requerimiento explícito para agentes:

    Solicitud: 'personaje humanoide 32x32 con walk, attack, hurt'.
    El sistema debe localizar recursos compatibles sin alucinar clips inexistentes.
    """
    db = AssetHubDB(":memory:")

    # Activo 1: Completo con walk, attack y hurt
    db.upsert_asset({
        "asset_id": "full_fighter",
        "name": "Full Fighter",
        "kind": "character",
        "taxonomy": {"visual_style": "pixel_art_32x32", "tags": ["humanoid"]},
        "image": {"width": 128, "height": 32, "has_alpha": True, "sha256": "1111" * 16, "dhash": "0000000000000001"},
        "geometry": {"frame_size": [32, 32]},
        "character_data": {
            "available_clips": [
                {"name": "walk_down", "frame_count": 4},
                {"name": "attack_melee", "frame_count": 3},
                {"name": "hurt", "frame_count": 2}
            ]
        },
        "provenance": {"author": "Artist", "license_spdx": "MIT", "license_tier": "tier_1_permissive_attribution"}
    })

    # Activo 2: Solo tiene walk (faltan attack y hurt)
    db.upsert_asset({
        "asset_id": "partial_peasant",
        "name": "Partial Peasant",
        "kind": "character",
        "taxonomy": {"visual_style": "pixel_art_32x32", "tags": ["humanoid"]},
        "image": {"width": 64, "height": 32, "has_alpha": True, "sha256": "2222" * 16, "dhash": "0000000000000002"},
        "geometry": {"frame_size": [32, 32]},
        "character_data": {
            "available_clips": [
                {"name": "walk", "frame_count": 2}
            ]
        },
        "provenance": {"author": "Artist2", "license_spdx": "CC0-1.0", "license_tier": "tier_0_public_domain"}
    })

    engine = AssetQueryEngine(db)

    # Consulta del agente
    result = engine.search(
        kind="character",
        target_frame_size=(32, 32),
        required_clips=["walk", "attack", "hurt"]
    )

    assert result["total_matches"] == 2
    res_list = result["results"]

    # El primero debe ser full_fighter con 100% de compatibilidad
    assert res_list[0]["asset_id"] == "full_fighter"
    assert res_list[0]["match_score"] == 1.0
    assert res_list[0]["exact_clip_match"] is True
    assert set(res_list[0]["found_clips"]) == {"walk", "attack", "hurt"}
    assert res_list[0]["missing_clips"] == []

    # El segundo debe ser partial_peasant con solo 33.3% de compatibilidad
    assert res_list[1]["asset_id"] == "partial_peasant"
    assert res_list[1]["match_score"] == 0.333
    assert res_list[1]["exact_clip_match"] is False
    assert res_list[1]["found_clips"] == ["walk"]
    assert set(res_list[1]["missing_clips"]) == {"attack", "hurt"}
    assert "Clips faltantes" in res_list[1]["warnings"][0]

    db.close()


def test_validator_rules():
    db = AssetHubDB(":memory:")
    validator = AssetValidator(db)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 1. Crear imagen válida de 64x32 (2 fotogramas de 32x32)
        valid_img = tmp_path / "valid.png"
        surf = pygame.Surface((64, 32), pygame.SRCALPHA)
        surf.fill((200, 100, 50, 255), (4, 4, 24, 24))
        pygame.image.save(surf, str(valid_img))

        valid_manifest = {
            "asset_id": "valid_warrior",
            "kind": "character",
            "image": {
                "relative_path": "valid.png",
                "width": 64,
                "height": 32,
                "has_alpha": True,
                "sha256": compute_sha256(valid_img)
            },
            "geometry": {
                "layout_type": "uniform_grid",
                "frame_size": [32, 32],
                "anchor_offset": [16, 32]
            },
            "provenance": {
                "author": "Legal Artist",
                "license_spdx": "MIT",
                "license_tier": "tier_1_permissive_attribution"
            }
        }

        rep = validator.validate_manifest_and_image(valid_manifest, base_dir=tmp_path)
        assert rep.is_valid is True
        assert len(rep.errors) == 0
        assert "V-01" in rep.passed_rules
        assert "V-02" in rep.passed_rules
        assert "V-03" in rep.passed_rules
        assert "V-05" in rep.passed_rules

        # 2. Probar regla V-02 (dimensión desalineada: 65x32 para celdas de 32x32)
        bad_dim_manifest = dict(valid_manifest)
        bad_dim_manifest["geometry"] = {"layout_type": "uniform_grid", "frame_size": [30, 30]}
        rep_bad_dim = validator.validate_manifest_and_image(bad_dim_manifest, base_dir=tmp_path)
        assert rep_bad_dim.is_valid is False
        assert any("[V-02]" in err for err in rep_bad_dim.errors)

        # 3. Probar regla V-05 (licencia prohibida Tier 3)
        bad_lic_manifest = dict(valid_manifest)
        bad_lic_manifest["provenance"] = {
            "author": "Some Artist",
            "license_spdx": "CC-BY-NC-4.0",
            "license_tier": "tier_3_prohibited"
        }
        rep_bad_lic = validator.validate_manifest_and_image(bad_lic_manifest, base_dir=tmp_path)
        assert rep_bad_lic.is_valid is False
        assert any("[V-05]" in err for err in rep_bad_lic.errors)

    db.close()


def test_exporter_pipeline():
    db = AssetHubDB(":memory:")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        img_file = tmp_path / "export_hero.png"
        surf = pygame.Surface((64, 32), pygame.SRCALPHA)
        surf.fill((100, 150, 250, 255), (2, 2, 28, 28))
        pygame.image.save(surf, str(img_file))

        manifest = {
            "asset_id": "export_hero",
            "name": "Export Hero",
            "kind": "character",
            "taxonomy": {"visual_style": "pixel_art_32x32", "tags": ["hero"]},
            "image": {
                "relative_path": "export_hero.png",
                "width": 64,
                "height": 32,
                "has_alpha": True,
                "sha256": compute_sha256(img_file)
            },
            "geometry": {
                "frame_size": [32, 32],
                "anchor_offset": [16, 32]
            },
            "character_data": {
                "available_clips": [
                    {"name": "walk", "frame_count": 2, "duration_ms": 120}
                ]
            },
            "provenance": {
                "author": "Hero Designer",
                "source_repo": "kenney",
                "license_spdx": "CC0-1.0",
                "license_tier": "tier_0_public_domain"
            }
        }
        db.upsert_asset(manifest)

        exporter = AssetExporter(db)
        out_dir = tmp_path / "exported_game_asset"
        res = exporter.export_asset("export_hero", out_dir, base_dir=tmp_path)

        assert res["status"] == "SUCCESS"
        anim_json = out_dir / "export_hero.anim.json"
        assert anim_json.is_file()

        # Verificar que el JSON exportado es válido y contiene los clips canónicos
        data = json.loads(anim_json.read_text(encoding="utf-8"))
        assert data["version"] == "gf-anim-v1"
        assert "idle" in data["clips"]
        assert "walk" in data["clips"]
        assert "hurt" in data["clips"]
        assert "die" in data["clips"]

        # Verificar generación de CREDITS.md
        credits_file = tmp_path / "CREDITS.md"
        credits_content = exporter.generate_credits_markdown(credits_file)
        assert "Hero Designer" in credits_content
        assert "CC0 1.0" in credits_content

    db.close()


def test_previewer_headless():
    previewer = AssetPreviewer()
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        img_file = tmp_path / "preview_sprite.png"
        surf = pygame.Surface((64, 32), pygame.SRCALPHA)
        surf.fill((220, 40, 40, 255), (0, 0, 32, 32))
        surf.fill((40, 220, 40, 255), (32, 0, 32, 32))
        pygame.image.save(surf, str(img_file))

        manifest = {
            "asset_id": "preview_sprite",
            "image": {"relative_path": "preview_sprite.png"},
            "geometry": {"frame_size": [32, 32], "anchor_offset": [16, 32]},
            "character_data": {
                "available_clips": [{"name": "walk", "frame_count": 2}]
            }
        }

        out_preview = tmp_path / "preview_result.png"
        generated = previewer.generate_headless_preview(
            manifest,
            clip_name="walk",
            output_path=out_preview,
            base_dir=tmp_path,
        )

        assert generated.is_file()
        assert generated.stat().st_size > 100
