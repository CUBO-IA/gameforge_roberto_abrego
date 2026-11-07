"""Sentinela de validación matemática, geométrica y de licencias para recursos gráficos."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pygame

from tools.asset_hub.db import AssetHubDB
from tools.asset_hub.hasher import compute_dhash, compute_sha256


@dataclass
class ValidationReport:
    """Informe de auditoría técnica y legal de un recurso gráfico."""
    asset_id: str
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passed_rules: list[str] = field(default_factory=list)

    def add_error(self, rule_code: str, message: str) -> None:
        self.is_valid = False
        self.errors.append(f"[{rule_code}] {message}")

    def add_warning(self, rule_code: str, message: str) -> None:
        self.warnings.append(f"[{rule_code}] {message}")

    def add_pass(self, rule_code: str) -> None:
        self.passed_rules.append(rule_code)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "passed_rules": self.passed_rules,
        }


class AssetValidator:
    """Validador estricto de recursos contra las 7 reglas normativas (V-01 a V-07)."""

    def __init__(self, db: AssetHubDB | None = None) -> None:
        self.db = db
        pygame.init()

    def validate_manifest_and_image(
        self,
        manifest: dict[str, Any],
        base_dir: Path | str | None = None,
    ) -> ValidationReport:
        """Audita exhaustivamente un manifiesto y su archivo de imagen asociado."""
        asset_id = manifest.get("asset_id", "unknown_asset")
        report = ValidationReport(asset_id=asset_id)

        # ---------------------------------------------------------
        # Regla V-01: Integridad y decodificación de la imagen
        # ---------------------------------------------------------
        img_meta = manifest.get("image", {})
        rel_img_path = img_meta.get("relative_path", "")
        if not rel_img_path:
            report.add_error("V-01", "El manifiesto no especifica 'image.relative_path'")
            return report

        base = Path(base_dir) if base_dir else Path.cwd()
        full_img_path = base / rel_img_path if not Path(rel_img_path).is_absolute() else Path(rel_img_path)

        if not full_img_path.is_file():
            report.add_error("V-01", f"Archivo de imagen no encontrado en disco: {full_img_path}")
            return report

        try:
            surface = pygame.image.load(str(full_img_path))
            if pygame.display.get_surface() is not None:
                surface = surface.convert_alpha()
            report.add_pass("V-01")
        except Exception as err:
            report.add_error("V-01", f"Error al decodificar la imagen: {err}")
            return report

        # Verificar hash SHA-256 si está declarado
        declared_sha = img_meta.get("sha256")
        if declared_sha:
            computed_sha = compute_sha256(full_img_path)
            if declared_sha.lower() != computed_sha.lower():
                report.add_error("V-01", f"Firma SHA-256 alterada: esperada {declared_sha}, calculada {computed_sha}")

        # ---------------------------------------------------------
        # Regla V-02: Retícula y dimensiones
        # ---------------------------------------------------------
        w, h = surface.get_size()
        geom = manifest.get("geometry", {})
        layout_type = geom.get("layout_type", "uniform_grid")
        frame_size = geom.get("frame_size", [w, h])
        fw, fh = frame_size[0], frame_size[1]

        if fw <= 0 or fh <= 0:
            report.add_error("V-02", f"Tamaño de fotograma inválido: {frame_size}")
        elif layout_type == "uniform_grid":
            if (w % fw) != 0 or (h % fh) != 0:
                report.add_error(
                    "V-02",
                    f"Dimensiones de imagen ({w}x{h}) no son múltiplos de celda ({fw}x{fh}). Residuo: {w % fw}x{h % fh}"
                )
            else:
                report.add_pass("V-02")
        elif layout_type in ["single_image", "9_slice"]:
            if w != fw or h != fh:
                report.add_warning("V-02", f"Dimensiones {w}x{h} difieren del frame_size declarado {fw}x{fh}")
            else:
                report.add_pass("V-02")
        else:
            report.add_pass("V-02")

        # ---------------------------------------------------------
        # Regla V-03: Canal alfa y transparencia
        # ---------------------------------------------------------
        declared_alpha = img_meta.get("has_alpha", True)
        has_alpha_channel = bool(surface.get_masks()[3] != 0 or surface.get_flags() & pygame.SRCALPHA)

        bbox = surface.get_bounding_rect()
        if bbox.width == 0 and bbox.height == 0:
            report.add_error("V-03", "La imagen está completamente vacía (100% píxeles transparentes)")
        elif declared_alpha and not has_alpha_channel:
            report.add_error("V-03", "El manifiesto declara transparencia (has_alpha=true) pero la imagen carece de canal alfa")
        else:
            report.add_pass("V-03")

        # ---------------------------------------------------------
        # Regla V-04: Estabilidad y límites de pivotes
        # ---------------------------------------------------------
        anchor_offset = geom.get("anchor_offset", [fw // 2, fh])

        px, py = anchor_offset[0], anchor_offset[1]
        if px < 0 or px > fw or py < 0 or py > fh:
            report.add_warning("V-04", f"El pivote [{px}, {py}] excede los límites de la celda ({fw}x{fh})")
        else:
            report.add_pass("V-04")

        # ---------------------------------------------------------
        # Regla V-05: Completitud legal y procedencia
        # ---------------------------------------------------------
        provenance = manifest.get("provenance", {})
        author = provenance.get("author", "").strip()
        spdx = provenance.get("license_spdx", "").strip()
        tier = provenance.get("license_tier", "").strip()

        if not author or author.lower() in ["unknown", "desconocido"]:
            report.add_error("V-05", "Autor no declarado o ambiguo en 'provenance.author'")
        elif not spdx or spdx.lower() == "unknown":
            report.add_error("V-05", "Licencia SPDX no declarada en 'provenance.license_spdx'")
        elif tier == "tier_3_prohibited":
            report.add_error("V-05", f"Activo bajo licencia prohibida por directiva de cumplimiento: {spdx}")
        else:
            if tier == "tier_2_copyleft_warning":
                report.add_warning("V-05", f"Licencia con cláusula ShareAlike ({spdx}): aislar en paquetes de datos")
            report.add_pass("V-05")

        # ---------------------------------------------------------
        # Regla V-06: Detección de duplicados perceptuales
        # ---------------------------------------------------------
        computed_dhash = compute_dhash(surface)
        if self.db:
            duplicates = self.db.find_duplicates(computed_dhash, max_hamming=2)
            other_dups = [d for d, dist in duplicates if d.get("asset_id") != asset_id]
            if other_dups:
                dup_ids = [d.get("asset_id") for d in other_dups]
                report.add_warning("V-06", f"Posible imagen duplicada con activos existentes: {dup_ids}")
            else:
                report.add_pass("V-06")
        else:
            report.add_pass("V-06")

        # ---------------------------------------------------------
        # Regla V-07: Verificación de fotogramas vacíos
        # ---------------------------------------------------------
        char_data = manifest.get("character_data", {})
        clips = char_data.get("available_clips", [])
        if clips and layout_type == "uniform_grid":
            # Inspeccionar la primera celda
            first_cell = pygame.Surface((fw, fh), pygame.SRCALPHA)
            first_cell.blit(surface, (0, 0), pygame.Rect(0, 0, fw, fh))
            cell_bbox = first_cell.get_bounding_rect()
            if cell_bbox.width == 0 and cell_bbox.height == 0:
                report.add_error("V-07", "El primer fotograma del spritesheet está completamente vacío/transparente")
            else:
                report.add_pass("V-07")
        else:
            report.add_pass("V-07")

        return report
