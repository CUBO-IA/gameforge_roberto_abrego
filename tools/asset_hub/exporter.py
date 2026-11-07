"""Compilador, empaquetador y exportador de recursos hacia el motor de juego y generador de créditos."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pygame

from tools.asset_hub.db import AssetHubDB
from tools.asset_hub.hasher import compute_sha256


class AssetExporter:
    """Exportador atómico que traduce activos del catálogo a formatos de ejecución del motor."""

    def __init__(self, db: AssetHubDB) -> None:
        self.db = db

    def export_asset(
        self,
        asset_id: str,
        target_dir: Path | str,
        base_dir: Path | str | None = None,
    ) -> dict[str, Any]:
        """Exporta y compila un activo en el directorio de destino para uso directo por el motor."""
        manifest = self.db.get_asset(asset_id)
        if not manifest:
            raise ValueError(f"Activo no encontrado en el catálogo: {asset_id}")

        base = Path(base_dir) if base_dir else Path.cwd()
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        img_meta = manifest.get("image", {})
        rel_img = img_meta.get("relative_path", "")
        source_img = base / rel_img if not Path(rel_img).is_absolute() else Path(rel_img)

        if not source_img.is_file():
            raise FileNotFoundError(f"Imagen fuente no encontrada: {source_img}")

        kind = manifest.get("kind", "character")
        exported_files: list[str] = []

        if kind in ["character", "creature_enemy", "npc"]:
            # Exportar a formato estándar gf-anim-v1
            dest_atlas = target_path / f"{asset_id}_atlas.png"
            shutil.copy2(source_img, dest_atlas)
            exported_files.append(str(dest_atlas))

            # Crear o adaptar .anim.json
            anim_manifest_path = target_path / f"{asset_id}.anim.json"
            geom = manifest.get("geometry", {})
            frame_size = geom.get("frame_size", [32, 32])
            fw, fh = frame_size[0], frame_size[1]
            anchor = geom.get("anchor_offset", [fw // 2, fh])

            # Cargar imagen para saber dimensiones
            surf = pygame.image.load(str(dest_atlas))
            w, h = surf.get_size()
            cols = max(1, w // fw)
            rows = max(1, h // fh)
            total_cells = max(1, cols * rows)

            char_data = manifest.get("character_data", {})
            available_clips = char_data.get("available_clips", [])

            frames_list: list[dict[str, Any]] = []
            clips_dict: dict[str, Any] = {}

            # Si no hay clips explícitos, generar clips estándar por defecto
            if not available_clips:
                available_clips = [
                    {"name": "idle", "frame_count": min(cols, 4), "duration_ms": 150, "is_looping": True},
                    {"name": "walk", "frame_count": min(cols, 4), "duration_ms": 100, "is_looping": True},
                ]

            frame_counter = 0
            for clip in available_clips:
                cname = clip.get("name", "idle")
                fcount = max(1, clip.get("frame_count", 1))
                dur = clip.get("duration_ms", 100)
                is_loop = clip.get("is_looping", True)

                clip_frame_ids = []
                for idx in range(fcount):
                    fid = f"{cname}_{idx}"
                    cell_idx = (frame_counter + idx) % total_cells
                    col = cell_idx % cols
                    row = cell_idx // cols
                    clip_frame_ids.append(fid)

                    # Si el frame ya fue creado, reutilizarlo
                    if not any(f["id"] == fid for f in frames_list):
                        frames_list.append({
                            "id": fid,
                            "rect": [col * fw, row * fh, fw, fh],
                            "pivot": anchor,
                            "duration_ms": dur,
                            "hurtboxes": [
                                [int(fw * 0.2), int(fh * 0.2), int(fw * 0.6), int(fh * 0.7)]
                            ],
                            "hitboxes": [],
                            "sockets": {
                                "hand_r": [int(fw * 0.8), int(fh * 0.6)],
                                "hand_l": [int(fw * 0.2), int(fh * 0.6)],
                            }
                        })

                clips_dict[cname] = {
                    "loop": is_loop,
                    "priority": 50 if "attack" in cname else (80 if "hurt" in cname else 20),
                    "frames": clip_frame_ids
                }
                frame_counter += fcount

            # Garantizar que existan los clips canónicos requeridos por el validador del motor ("idle", "walk", "hurt", "die")
            first_frame_id = frames_list[0]["id"] if frames_list else "default_0"
            if not frames_list:
                frames_list.append({
                    "id": first_frame_id,
                    "rect": [0, 0, min(fw, w), min(fh, h)],
                    "pivot": anchor,
                    "duration_ms": 150,
                    "hurtboxes": [[0, 0, fw, fh]],
                    "hitboxes": [],
                    "sockets": {}
                })

            if "idle" not in clips_dict:
                idle_frames = clips_dict.get("walk", {}).get("frames", [first_frame_id])[:2] or [first_frame_id]
                clips_dict["idle"] = {"loop": True, "priority": 10, "frames": idle_frames}
            if "walk" not in clips_dict:
                walk_frames = clips_dict.get("idle", {}).get("frames", [first_frame_id]) or [first_frame_id]
                clips_dict["walk"] = {"loop": True, "priority": 20, "frames": walk_frames}
            if "hurt" not in clips_dict:
                clips_dict["hurt"] = {"loop": False, "priority": 80, "frames": [first_frame_id]}
            if "die" not in clips_dict:
                die_frames = clips_dict.get("hurt", {}).get("frames", [first_frame_id]) or [first_frame_id]
                clips_dict["die"] = {"loop": False, "priority": 100, "frames": die_frames}

            anim_data = {
                "version": "gf-anim-v1",
                "metadata": {
                    "id": asset_id,
                    "display_name": manifest.get("name", asset_id),
                    "author": manifest.get("provenance", {}).get("author", "GameForge Team"),
                    "rig_type": "frame_by_frame",
                    "tags": manifest.get("taxonomy", {}).get("tags", []),
                },
                "texture": {
                    "image_path": dest_atlas.name,
                    "width": w,
                    "height": h,
                    "format": "RGBA"
                },
                "frames": frames_list,
                "clips": clips_dict
            }

            with open(anim_manifest_path, "w", encoding="utf-8") as f:
                json.dump(anim_data, f, indent=2, ensure_ascii=False)
            exported_files.append(str(anim_manifest_path))

        else:
            # Archivo genérico (tileset, ui, etc.)
            dest_img = target_path / source_img.name
            shutil.copy2(source_img, dest_img)
            exported_files.append(str(dest_img))

            spec_path = target_path / f"{asset_id}.spec.json"
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            exported_files.append(str(spec_path))

        # Copiar metadato de procedencia sidecar (.meta.json)
        dest_meta = target_path / f"{source_img.name}.meta.json"
        prov_data = {
            "$schema": "https://gameforge2d.org/schemas/gf-provenance-v1.json",
            "asset_id": asset_id,
            "provenance": manifest.get("provenance", {}),
            "checksums": {
                "sha256": compute_sha256(dest_atlas if kind in ["character", "creature_enemy"] else dest_img),
            }
        }
        with open(dest_meta, "w", encoding="utf-8") as f:
            json.dump(prov_data, f, indent=2, ensure_ascii=False)
        exported_files.append(str(dest_meta))

        # Actualizar assets/README.md y CREDITS.md
        self.update_assets_readme(asset_id, manifest)

        return {
            "status": "SUCCESS",
            "asset_id": asset_id,
            "target_dir": str(target_path),
            "exported_files": exported_files,
        }

    def update_assets_readme(self, asset_id: str, manifest: dict[str, Any]) -> None:
        """Registra el activo exportado en assets/README.md según la directiva 01_GLOBAL.md."""
        readme_path = Path("assets/README.md")
        if not readme_path.is_file():
            return

        content = readme_path.read_text(encoding="utf-8")
        prov = manifest.get("provenance", {})
        author = prov.get("author", "Desconocido")
        license_spdx = prov.get("license_spdx", "Desconocida")

        entry = f"- `{asset_id}`: Autor: {author} | Licencia: {license_spdx} | Registro en GameForge Asset Hub\n"

        if asset_id not in content:
            updated_content = content.rstrip() + "\n\n### Registro de Activos Externos\n" if "### Registro de Activos Externos" not in content else content
            if entry not in updated_content:
                updated_content += entry
                readme_path.write_text(updated_content, encoding="utf-8")

    def generate_credits_markdown(self, output_path: Path | str = "CREDITS.md") -> str:
        """Genera un archivo CREDITS.md completo con todos los recursos registrados en el catálogo."""
        all_assets = self.db.list_all()

        by_tier: dict[str, list[dict[str, Any]]] = {
            "tier_0_public_domain": [],
            "tier_1_permissive_attribution": [],
            "tier_2_copyleft_warning": [],
            "tier_3_prohibited": [],
        }

        for asset in all_assets:
            prov = asset.get("provenance", {})
            tier = prov.get("license_tier", "tier_1_permissive_attribution")
            by_tier.setdefault(tier, []).append(asset)

        lines = [
            "# CRÉDITOS Y PROCEDENCIA DE RECURSOS — GAMEFORGE 2D",
            "",
            "Este documento reconoce a todos los autores y fuentes de recursos visuales y auditivos",
            "utilizados en GameForge 2D, conforme a sus respectivas licencias de distribución abierta.",
            "",
        ]

        if by_tier["tier_0_public_domain"]:
            lines.extend([
                "## Dominio Público (CC0 1.0 Universal / Unlicense)",
                "Recursos completamente libres de restricciones de autoría:",
            ])
            for a in by_tier["tier_0_public_domain"]:
                prov = a.get("provenance", {})
                author = prov.get("author", "Comunidad")
                repo = prov.get("source_repo", "")
                lines.append(f"- **{a.get('name', a['asset_id'])}**: Creado por {author} ({repo}). Licencia CC0 1.0.")
            lines.append("")

        if by_tier["tier_1_permissive_attribution"]:
            lines.extend([
                "## Licencias Permisivas con Atribución (CC-BY 3.0 / 4.0, MIT, OGA-BY)",
                "Recursos que requieren mención de autoría:",
            ])
            for a in by_tier["tier_1_permissive_attribution"]:
                prov = a.get("provenance", {})
                author = prov.get("author", "Comunidad")
                spdx = prov.get("license_spdx", "CC-BY")
                notice = prov.get("attribution_text") or f"Creado por {author} bajo licencia {spdx}."
                lines.append(f"- **{a.get('name', a['asset_id'])}**: {notice}")
            lines.append("")

        if by_tier["tier_2_copyleft_warning"]:
            lines.extend([
                "## Copyleft Artístico / ShareAlike (CC-BY-SA 3.0 / 4.0, GPLv3)",
                "Recursos compartimentados como paquetes de datos externos:",
            ])
            for a in by_tier["tier_2_copyleft_warning"]:
                prov = a.get("provenance", {})
                author = prov.get("author", "Comunidad")
                spdx = prov.get("license_spdx", "CC-BY-SA")
                notice = prov.get("attribution_text") or f"Creado por {author} bajo licencia {spdx}."
                lines.append(f"- **{a.get('name', a['asset_id'])}**: {notice}")
            lines.append("")

        out_text = "\n".join(lines)
        out_file = Path(output_path)
        out_file.write_text(out_text, encoding="utf-8")
        return out_text
