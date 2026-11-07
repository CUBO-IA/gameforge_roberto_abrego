"""Herramienta CLI de validación estricta para manifiestos de animación gf-anim-v1.

Utilizada por agentes de IA y pipelines de CI para asegurar que ningún personaje
con errores de fotogramas, límites o referencias huérfanas ingrese al juego.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MANDATORY_CLIPS = ("idle", "walk", "hurt", "die")
SUPPORTED_VERSIONS = ("gf-anim-v1", "gf-anim-v1.0.0")


def validate_character_manifest(manifest_path: Path) -> list[str]:
    """Valida un archivo de manifiesto y devuelve una lista de errores encontrados."""
    errors: list[str] = []

    if not manifest_path.is_file():
        return [f"El archivo no existe: {manifest_path}"]

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return [f"JSON inválido en {manifest_path}: {err}"]

    if not isinstance(data, dict):
        return ["La raíz del archivo debe ser un objeto JSON"]

    # 1. Versión
    version = data.get("version")
    if version not in SUPPORTED_VERSIONS:
        errors.append(f"Versión no soportada '{version}'. Esperada una de {SUPPORTED_VERSIONS}")

    # 2. Metadatos
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("Falta la sección obligatoria 'metadata'")
    else:
        for req_field in ("id", "display_name", "rig_type"):
            if req_field not in metadata:
                errors.append(f"Falta el campo obligatorio '{req_field}' en 'metadata'")

    # 3. Textura
    texture = data.get("texture")
    tex_w = 0
    tex_h = 0
    if not isinstance(texture, dict):
        errors.append("Falta la sección obligatoria 'texture'")
    else:
        img_rel = texture.get("image_path")
        if not img_rel:
            errors.append("Falta 'image_path' en 'texture'")
        else:
            img_file = manifest_path.parent / img_rel
            if not img_file.is_file():
                errors.append(f"La imagen de atlas especificada no existe en disco: {img_file}")

        tex_w = texture.get("width", 0)
        tex_h = texture.get("height", 0)
        if not isinstance(tex_w, int) or tex_w <= 0:
            errors.append(f"Ancho de textura inválido: {tex_w}")
        if not isinstance(tex_h, int) or tex_h <= 0:
            errors.append(f"Alto de textura inválido: {tex_h}")

    # 4. Fotogramas (Frames)
    raw_frames = data.get("frames")
    frame_ids: set[str] = set()
    if not isinstance(raw_frames, list) or len(raw_frames) == 0:
        errors.append("La sección 'frames' debe ser una lista no vacía")
    else:
        for idx, frame in enumerate(raw_frames):
            if not isinstance(frame, dict):
                errors.append(f"Fotograma en índice {idx} no es un objeto")
                continue

            fid = frame.get("id")
            if not fid or not isinstance(fid, str):
                errors.append(f"Fotograma en índice {idx} carece de un 'id' válido")
            elif fid in frame_ids:
                errors.append(f"Identificador de fotograma duplicado: '{fid}'")
            else:
                frame_ids.add(fid)

            rect = frame.get("rect")
            if not isinstance(rect, list) or len(rect) != 4:
                errors.append(f"Fotograma '{fid}' carece de 'rect' [x, y, w, h] válido")
            else:
                x, y, w, h = rect
                if not all(isinstance(c, int) for c in (x, y, w, h)):
                    errors.append(f"Coordenadas de rect no son enteros en '{fid}': {rect}")
                else:
                    if x < 0 or y < 0 or w <= 0 or h <= 0:
                        errors.append(f"Dimensiones de rect inválidas en '{fid}': {rect}")
                    if tex_w > 0 and tex_h > 0:
                        if x + w > tex_w or y + h > tex_h:
                            errors.append(
                                f"Fotograma '{fid}' [{x}, {y}, {w}, {h}] desborda el atlas ({tex_w}x{tex_h})"
                            )

            pivot = frame.get("pivot")
            if not isinstance(pivot, list) or len(pivot) != 2:
                errors.append(f"Fotograma '{fid}' carece de 'pivot' [px, py] válido")

            dur = frame.get("duration_ms")
            if dur is not None:
                if not isinstance(dur, int) or dur <= 0:
                    errors.append(f"Duración inválida en '{fid}': {dur} ms")

            # Hitboxes
            hitboxes = frame.get("hitboxes", [])
            for h_idx, hb in enumerate(hitboxes):
                if not isinstance(hb, dict) or "rect" not in hb or "damage" not in hb:
                    errors.append(f"Hitbox {h_idx} en '{fid}' no tiene estructura válida")
                else:
                    hb_dmg = hb.get("damage")
                    if not isinstance(hb_dmg, (int, float)) or hb_dmg <= 0:
                        errors.append(f"Daño de hitbox inválido en '{fid}': {hb_dmg}")

    # 5. Clips
    raw_clips = data.get("clips")
    if not isinstance(raw_clips, dict) or len(raw_clips) == 0:
        errors.append("La sección 'clips' debe ser un diccionario no vacío")
    else:
        # Verificar clips obligatorios para jugabilidad
        for mandatory in MANDATORY_CLIPS:
            if mandatory not in raw_clips:
                errors.append(f"Falta el clip obligatorio '{mandatory}' en 'clips'")

        # Integridad referencial
        for cname, cinfo in raw_clips.items():
            if not isinstance(cinfo, dict):
                errors.append(f"Clip '{cname}' debe ser un objeto")
                continue
            cframes = cinfo.get("frames")
            if not isinstance(cframes, list) or len(cframes) == 0:
                errors.append(f"Clip '{cname}' no contiene fotogramas")
                continue
            for fid in cframes:
                if fid not in frame_ids:
                    errors.append(
                        f"Clip '{cname}' referencia un fotograma inexistente: '{fid}'"
                    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validador de personajes y animaciones gf-anim-v1")
    parser.add_argument("--character", "-c", type=str, help="Ruta al archivo .anim.json a validar")
    parser.add_argument("--dir", "-d", type=str, help="Directorio con archivos .anim.json a validar recursivamente")

    args = parser.parse_args()

    targets: list[Path] = []
    if args.character:
        targets.append(Path(args.character))
    elif args.dir:
        targets.extend(Path(args.dir).rglob("*.anim.json"))
    else:
        # Por defecto validar la carpeta assets si existe
        default_dir = Path("assets/sprites")
        if default_dir.is_dir():
            targets.extend(default_dir.rglob("*.anim.json"))
        else:
            parser.print_help()
            return 1

    if not targets:
        print("No se encontraron archivos de animación .anim.json para validar.")
        return 0

    total_errors = 0
    print(f"== Validando {len(targets)} archivo(s) de animación ==")
    for target in targets:
        errors = validate_character_manifest(target)
        if errors:
            total_errors += len(errors)
            print(f"\n[FALLO] {target.name}:")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"[OK] {target.name} cumple con gf-anim-v1")

    if total_errors > 0:
        print(f"\nSe encontraron {total_errors} error(es) en total.")
        return 1

    print("\nTodos los personajes son válidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
