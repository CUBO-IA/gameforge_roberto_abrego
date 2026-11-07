"""Servicio de escaneo de directorios, detección automática de tipos e indexación en base de datos."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pygame

from tools.asset_hub.db import AssetHubDB
from tools.asset_hub.hasher import compute_dhash, compute_sha256


class AssetScanner:
    """Escáner recursivo para descubrimiento, ingestión e indexación de activos gráficos."""

    def __init__(self, db: AssetHubDB) -> None:
        self.db = db
        pygame.init()

    def scan_directory(self, target_dir: Path | str, base_repo_dir: Path | str | None = None) -> dict[str, int]:
        """Recorre recursivamente un directorio e indexa todos los activos válidos encontrados."""
        target_path = Path(target_dir).resolve()
        base_dir = (Path(base_repo_dir) if base_repo_dir else Path.cwd()).resolve()

        if not target_path.exists():
            raise FileNotFoundError(f"El directorio objetivo no existe: {target_path}")

        stats = {"scanned_images": 0, "indexed_manifests": 0, "synthesized_assets": 0, "errors": 0}

        # 1. Buscar primero archivos de manifiesto formales (*.asset.json)
        for manifest_file in target_path.rglob("*.asset.json"):
            try:
                manifest_file = manifest_file.resolve()
                with open(manifest_file, encoding="utf-8") as f:
                    data = json.load(f)
                # Resolver ruta de imagen y recalcular hashes si faltan
                img_info = data.get("image", {})
                rel_img = img_info.get("relative_path", "")
                if rel_img:
                    # Si es relativa, puede ser relativa a base_dir o al manifest_file
                    candidate1 = (base_dir / rel_img).resolve()
                    candidate2 = (manifest_file.parent / rel_img).resolve()
                    full_img = candidate1 if candidate1.is_file() else candidate2

                    if full_img.is_file():
                        if "sha256" not in img_info or not img_info["sha256"]:
                            img_info["sha256"] = compute_sha256(full_img)
                        if "dhash" not in img_info or not img_info["dhash"]:
                            surf = pygame.image.load(str(full_img))
                            img_info["dhash"] = compute_dhash(surf)
                            img_info["width"], img_info["height"] = surf.get_size()
                            img_info["has_alpha"] = bool(surf.get_masks()[3] != 0 or surf.get_flags() & pygame.SRCALPHA)
                        img_info["relative_path"] = str(full_img.relative_to(base_dir)).replace("\\", "/")
                        data["image"] = img_info

                rel_manifest_path = str(manifest_file.relative_to(base_dir)).replace("\\", "/")
                self.db.upsert_asset(data, manifest_path=rel_manifest_path)
                stats["indexed_manifests"] += 1
            except Exception as err:
                stats["errors"] += 1
                print(f"[AVISO] Error indexando manifiesto {manifest_file}: {err}")

        # 2. Buscar archivos .anim.json canónicos de GameForge 2D (gf-anim-v1)
        for anim_file in target_path.rglob("*.anim.json"):
            try:
                anim_file = anim_file.resolve()
                with open(anim_file, encoding="utf-8") as f:
                    anim_data = json.load(f)

                meta = anim_data.get("metadata", {})
                asset_id = meta.get("id") or anim_file.stem.replace(".anim", "")

                cur = self.db._conn.cursor()
                cur.execute("SELECT manifest_path FROM assets WHERE asset_id = ?", (asset_id,))
                row = cur.fetchone()
                if row and str(row["manifest_path"]).endswith(".asset.json"):
                    continue  # Ya indexado explícitamente desde un .asset.json formal

                tex = anim_data.get("texture", {})
                tex_rel = tex.get("image_path", "")
                full_img_path = (anim_file.parent / tex_rel).resolve() if tex_rel else (anim_file.with_name(f"{asset_id}_atlas.png")).resolve()

                if not full_img_path.is_file():
                    continue

                surface = pygame.image.load(str(full_img_path))
                w, h = surface.get_size()
                sha = compute_sha256(full_img_path)
                dhash = compute_dhash(surface)
                has_alpha = bool(surface.get_masks()[3] != 0 or surface.get_flags() & pygame.SRCALPHA)

                # Extraer fotogramas y tamaño promedio
                frames = anim_data.get("frames", [])
                fw, fh = 32, 32
                if frames:
                    first_rect = frames[0].get("rect", [0, 0, 32, 32])
                    fw, fh = first_rect[2], first_rect[3]

                # Extraer clips disponibles
                clips = anim_data.get("clips", {})
                avail_clips: list[dict[str, Any]] = []
                for cname, cinfo in clips.items():
                    f_list = cinfo.get("frames", [])
                    avail_clips.append({
                        "name": cname,
                        "frame_count": len(f_list),
                        "directions": ["down"] if "down" in cname else ["all"],
                        "duration_ms": 100,
                        "is_looping": cinfo.get("loop", True)
                    })

                # Procedencia: verificar si hay archivo .meta.json acompañante
                sidecar_meta = full_img_path.with_name(f"{full_img_path.name}.meta.json")
                author = meta.get("author", "GameForge Team")
                spdx = "MIT"
                tier = "tier_1_permissive_attribution"
                if sidecar_meta.is_file():
                    try:
                        with open(sidecar_meta, encoding="utf-8") as smf:
                            sdata = json.load(smf)
                        prov = sdata.get("provenance", {})
                        lic = sdata.get("license", {})
                        author = prov.get("author", author)
                        spdx = lic.get("spdx_id", spdx)
                        tier = lic.get("tier", tier)
                    except Exception:
                        pass

                synthesized_manifest = {
                    "schema_version": "gf-asset-catalog-v1.0.0",
                    "asset_id": asset_id,
                    "name": meta.get("display_name", asset_id.replace("_", " ").title()),
                    "kind": "character" if "player" in str(anim_file) else "creature_enemy",
                    "taxonomy": {
                        "genre": "top_down_rpg",
                        "theme": "dungeon",
                        "visual_style": f"pixel_art_{fw}x{fh}",
                        "tags": meta.get("tags", [asset_id, "animated"]),
                    },
                    "image": {
                        "relative_path": str(full_img_path.relative_to(base_dir)).replace("\\", "/"),
                        "width": w,
                        "height": h,
                        "has_alpha": has_alpha,
                        "color_mode": "RGBA",
                        "sha256": sha,
                        "dhash": dhash,
                    },
                    "geometry": {
                        "layout_type": "packed_atlas" if "atlas" in full_img_path.name else "uniform_grid",
                        "frame_size": [fw, fh],
                        "anchor_preset": "bottom_center",
                        "anchor_offset": [fw // 2, fh],
                    },
                    "character_data": {
                        "directions_supported": ["down", "left", "right", "up"],
                        "available_clips": avail_clips,
                        "has_paperdoll_layers": False,
                    },
                    "provenance": {
                        "author": author,
                        "source_repo": "internal_gameforge",
                        "license_spdx": spdx,
                        "license_tier": tier,
                        "attribution_required": (tier != "tier_0_public_domain"),
                        "attribution_text": f"Created for GameForge 2D by {author}",
                    },
                    "engine_compatibility": {
                        "gf_anim_v1_ready": True,
                        "tilemap_ready": False,
                        "canvas_scale_compatible": True,
                    }
                }

                rel_anim_path = str(anim_file.relative_to(base_dir)).replace("\\", "/")
                self.db.upsert_asset(synthesized_manifest, manifest_path=rel_anim_path)
                stats["synthesized_assets"] += 1
            except Exception as err:
                stats["errors"] += 1
                print(f"[AVISO] Error procesando archivo de animación {anim_file}: {err}")

        return stats
