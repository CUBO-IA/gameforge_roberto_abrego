"""Motor de consulta y búsqueda semántica para agentes de IA y desarrolladores."""

from __future__ import annotations

from typing import Any

from tools.asset_hub.db import AssetHubDB

LICENSE_TIER_RANK = {
    "tier_0_public_domain": 0,
    "tier_1_permissive_attribution": 1,
    "tier_2_copyleft_warning": 2,
    "tier_3_prohibited": 3,
}


def normalize_clip_name(raw_name: str) -> str:
    """Normaliza un nombre de clip para cotejar acciones canónicas (ej. 'attack_down' -> 'attack')."""
    raw = raw_name.lower().strip()
    for cardinal in ["_down", "_left", "_right", "_up", "_melee", "_ranged", "_slam", "_slash"]:
        if raw.endswith(cardinal):
            raw = raw[:-len(cardinal)]
    return raw


class AssetQueryEngine:
    """Motor de evaluación de compatibilidad y búsqueda semántica sin alucinaciones."""

    def __init__(self, db: AssetHubDB) -> None:
        self.db = db

    def search(
        self,
        kind: str | None = None,
        style: str | None = None,
        theme: str | None = None,
        target_frame_size: tuple[int, int] | None = None,
        required_clips: list[str] | None = None,
        tags: list[str] | None = None,
        max_license_tier: str | None = None,
        allow_scaling: bool = True,
    ) -> dict[str, Any]:
        """Ejecuta una búsqueda semántica rigurosa.

        Evalúa dimensionalidad, presencia real de clips de animación y compatibilidad de licencias.
        No inventa clips ni declara compatibilidad 1.0 si faltan animaciones requeridas.
        """
        all_assets = self.db.list_all()
        results: list[dict[str, Any]] = []

        target_w, target_h = target_frame_size if target_frame_size else (None, None)
        normalized_req_clips = [req.lower().strip() for req in (required_clips or [])]

        for asset in all_assets:
            # 1. Filtro de tipo (kind)
            asset_kind = asset.get("kind", "")
            if kind:
                # Si el usuario busca 'character', acepta también 'creature_enemy' o 'npc'
                if kind == "character" and asset_kind in ["character", "creature_enemy", "npc"]:
                    pass
                elif asset_kind != kind:
                    continue

            # 2. Filtro de estilo
            taxonomy = asset.get("taxonomy", {})
            asset_style = taxonomy.get("visual_style", "")
            if style and asset_style != style:
                continue

            # 3. Filtro de tema
            asset_theme = taxonomy.get("theme", "")
            if theme and asset_theme != theme:
                continue

            # 4. Filtro de licencia
            provenance = asset.get("provenance", {})
            asset_tier = provenance.get("license_tier", "tier_3_prohibited")
            if max_license_tier:
                max_rank = LICENSE_TIER_RANK.get(max_license_tier, 3)
                asset_rank = LICENSE_TIER_RANK.get(asset_tier, 3)
                if asset_rank > max_rank:
                    continue

            # 5. Filtro de etiquetas (tags)
            asset_tags = [t.lower() for t in taxonomy.get("tags", [])]
            if tags:
                if not all(tag.lower() in asset_tags for tag in tags):
                    continue

            # 6. Evaluación dimensional
            geometry = asset.get("geometry", {})
            frame_size = geometry.get("frame_size", [32, 32])
            fw, fh = frame_size[0], frame_size[1]

            dim_match = "exact"
            if target_w and target_h:
                if fw == target_w and fh == target_h:
                    dim_match = "exact"
                elif allow_scaling and fw % target_w == 0 and fh % target_h == 0:
                    dim_match = f"downscale_compatible_{fw // target_w}x"
                elif allow_scaling and target_w % fw == 0 and target_h % fh == 0:
                    dim_match = f"upscale_compatible_{target_w // fw}x"
                elif allow_scaling:
                    dim_match = "scale_compatible_ratio"
                else:
                    continue  # Dimensión incompatible y escalado deshabilitado

            # 7. Evaluación estricta de clips de animación
            char_data = asset.get("character_data", {})
            available_clips_meta = char_data.get("available_clips", [])
            available_clip_names = [c.get("name", "").lower() for c in available_clips_meta]
            normalized_available = {normalize_clip_name(c) for c in available_clip_names} | set(available_clip_names)

            found_clips: list[str] = []
            missing_clips: list[str] = []

            for req in normalized_req_clips:
                req_norm = normalize_clip_name(req)
                if req_norm in normalized_available or req in normalized_available:
                    found_clips.append(req)
                else:
                    missing_clips.append(req)

            match_score = 1.0
            if normalized_req_clips:
                match_score = round(len(found_clips) / len(normalized_req_clips), 3)

            exact_clip_match = (len(missing_clips) == 0)

            # Advertencias accionables
            warnings: list[str] = []
            if not exact_clip_match:
                warnings.append(f"Clips faltantes no encontrados en el activo: {missing_clips}")
            if asset_tier == "tier_2_copyleft_warning":
                warnings.append("Licencia ShareAlike (Tier 2): requiere aislamiento como paquete de datos desacoplado.")

            # Comando para exportar directamente
            export_cmd = f"python -m tools.asset_hub export {asset['asset_id']} --target assets/sprites/{asset['asset_id']}/"

            results.append({
                "asset_id": asset["asset_id"],
                "name": asset.get("name", asset["asset_id"]),
                "kind": asset_kind,
                "match_score": match_score,
                "exact_clip_match": exact_clip_match,
                "found_clips": found_clips,
                "missing_clips": missing_clips,
                "native_frame_size": [fw, fh],
                "dimension_match": dim_match,
                "license": {
                    "spdx": provenance.get("license_spdx", "UNKNOWN"),
                    "tier": asset_tier,
                    "attribution": provenance.get("attribution_text", "")
                },
                "warnings": warnings,
                "engine_export_command": export_cmd,
            })

        # Ordenar resultados: mayor match_score primero, luego dimensión exacta, luego mejor tier de licencia
        def sort_key(item: dict[str, Any]) -> tuple[float, int, int]:
            score = item["match_score"]
            dim_priority = 0 if item["dimension_match"] == "exact" else 1
            tier_rank = LICENSE_TIER_RANK.get(item["license"]["tier"], 3)
            return (-score, dim_priority, tier_rank)

        results.sort(key=sort_key)

        return {
            "query": {
                "kind": kind,
                "style": style,
                "theme": theme,
                "target_frame_size": target_frame_size,
                "required_clips": required_clips or [],
                "tags": tags or [],
                "max_license_tier": max_license_tier,
            },
            "total_matches": len(results),
            "results": results,
        }
