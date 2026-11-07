"""Interfaz de Línea de Comandos (CLI) para GameForge Asset Hub."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.asset_hub.db import AssetHubDB
from tools.asset_hub.exporter import AssetExporter
from tools.asset_hub.previewer import AssetPreviewer
from tools.asset_hub.query import AssetQueryEngine
from tools.asset_hub.scanner import AssetScanner
from tools.asset_hub.validator import AssetValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.asset_hub",
        description="GameForge Asset Hub: Búsqueda semántica, validación y gestión de recursos gráficos"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # 1. SCAN
    p_scan = subparsers.add_parser("scan", help="Escanea e indexa directorios en la base de datos local")
    p_scan.add_argument("path", type=str, nargs="?", default="assets", help="Ruta a escanear (por defecto: assets/)")
    p_scan.add_argument("--db", type=str, default=None, help="Ruta a la base de datos SQLite")

    # 2. SEARCH
    p_search = subparsers.add_parser("search", help="Busca recursos con filtros semánticos para agentes")
    p_search.add_argument("--kind", "-k", type=str, default=None, help="Tipo: character, creature_enemy, tileset, ui_component, etc.")
    p_search.add_argument("--style", "-s", type=str, default=None, help="Estilo visual: pixel_art_32x32, pixel_art_16x16, etc.")
    p_search.add_argument("--theme", "-t", type=str, default=None, help="Tema: dungeon, cavern, fantasy_medieval, etc.")
    p_search.add_argument("--size", type=str, default=None, help="Dimensiones esperadas: e.g. 32x32 o 64x64")
    p_search.add_argument("--clips", "-c", type=str, default=None, help="Clips de animación requeridos separados por coma (e.g. walk,attack,hurt)")
    p_search.add_argument("--tags", type=str, default=None, help="Etiquetas separadas por coma")
    p_search.add_argument("--max-tier", type=str, default=None, help="Nivel máximo de licencia: tier_0_public_domain, tier_1_permissive_attribution, tier_2_copyleft_warning")
    p_search.add_argument("--json", action="store_true", help="Salida en formato JSON puro para consumo por agentes")
    p_search.add_argument("--db", type=str, default=None, help="Ruta a la base de datos SQLite")

    # 3. INSPECT
    p_inspect = subparsers.add_parser("inspect", help="Muestra los metadatos completos y clips de un recurso")
    p_inspect.add_argument("asset_id", type=str, help="Identificador del activo")
    p_inspect.add_argument("--json", action="store_true", help="Salida en formato JSON")
    p_inspect.add_argument("--db", type=str, default=None, help="Ruta a la base de datos SQLite")

    # 4. VALIDATE
    p_val = subparsers.add_parser("validate", help="Audita la integridad técnica y legal de recursos (V-01 a V-07)")
    p_val.add_argument("asset_id", type=str, nargs="?", default=None, help="ID del activo a validar (o omitir con --all)")
    p_val.add_argument("--all", action="store_true", help="Valida todos los activos en el catálogo")
    p_val.add_argument("--json", action="store_true", help="Salida en formato JSON")
    p_val.add_argument("--db", type=str, default=None, help="Ruta a la base de datos SQLite")

    # 5. PREVIEW
    p_prev = subparsers.add_parser("preview", help="Previsualiza un recurso de forma headless o en ventana")
    p_prev.add_argument("asset_id", type=str, help="ID del activo a previsualizar")
    p_prev.add_argument("--clip", "-c", type=str, default=None, help="Clip específico a previsualizar")
    p_prev.add_argument("--output", "-o", type=str, default=None, help="Ruta donde guardar la tira o GIF de previsualización")
    p_prev.add_argument("--headless", action="store_true", default=True, help="Modo sin ventana (por defecto)")
    p_prev.add_argument("--window", action="store_true", help="Abre una ventana gráfica interactiva")
    p_prev.add_argument("--scale", type=int, default=2, help="Factor de escala para la previsualización")
    p_prev.add_argument("--db", type=str, default=None, help="Ruta a la base de datos SQLite")

    # 6. EXPORT
    p_exp = subparsers.add_parser("export", help="Compila y exporta un activo al directorio de juego")
    p_exp.add_argument("asset_id", type=str, help="ID del activo a exportar")
    p_exp.add_argument("--target", "-t", type=str, required=True, help="Directorio destino en el motor")
    p_exp.add_argument("--db", type=str, default=None, help="Ruta a la base de datos SQLite")

    # 7. CREDITS
    p_cred = subparsers.add_parser("credits", help="Reconstruye el archivo de créditos y licencias CREDITS.md")
    p_cred.add_argument("--output", "-o", type=str, default="CREDITS.md", help="Ruta del archivo CREDITS.md a generar")
    p_cred.add_argument("--db", type=str, default=None, help="Ruta a la base de datos SQLite")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    db = AssetHubDB(args.db)

    try:
        if args.command == "scan":
            scanner = AssetScanner(db)
            scan_path = Path(args.path)
            print(f"[ASSET HUB] Escaneando directorio: {scan_path.resolve()} ...")
            stats = scanner.scan_directory(scan_path)
            catalog_json = scan_path / "hub_index.json" if scan_path.is_dir() else Path("assets/hub_index.json")
            db.export_catalog_json(catalog_json)
            print(f"[ASSET HUB] Escaneo completado con éxito: {stats}")
            print(f"[ASSET HUB] Total activos registrados en base de datos: {db.count()}")
            print(f"[ASSET HUB] Catálogo JSON exportado a: {catalog_json}")
            return 0

        elif args.command == "search":
            engine = AssetQueryEngine(db)
            target_size = None
            if args.size:
                parts = args.size.lower().split("x")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    target_size = (int(parts[0]), int(parts[1]))

            req_clips = [c.strip() for c in args.clips.split(",")] if args.clips else None
            tags = [t.strip() for t in args.tags.split(",")] if args.tags else None

            res = engine.search(
                kind=args.kind,
                style=args.style,
                theme=args.theme,
                target_frame_size=target_size,
                required_clips=req_clips,
                tags=tags,
                max_license_tier=args.max_tier,
            )

            if args.json:
                print(json.dumps(res, indent=2, ensure_ascii=False))
            else:
                total = res["total_matches"]
                print(f"\n--- RESULTADOS DE BÚSQUEDA ({total} activos encontrados) ---")
                for r in res["results"]:
                    match_str = f"{r['match_score'] * 100:.0f}%"
                    status = "EXACTO" if r["exact_clip_match"] else "PARCIAL"
                    print(f"\nID: {r['asset_id']} | Nombre: {r['name']} | Compatibilidad: {match_str} ({status})")
                    print(f"  Tipo: {r['kind']} | Dimensión: {r['native_frame_size']} ({r['dimension_match']})")
                    print(f"  Clips encontrados: {r['found_clips']}")
                    if r["missing_clips"]:
                        print(f"  [AVISO] Clips faltantes: {r['missing_clips']}")
                    print(f"  Licencia: {r['license']['spdx']} ({r['license']['tier']})")
                    if r["warnings"]:
                        for w in r["warnings"]:
                            print(f"  - Alerta: {w}")
                    print(f"  Comando exportación: {r['engine_export_command']}")
                print("")
            return 0

        elif args.command == "inspect":
            manifest = db.get_asset(args.asset_id)
            if not manifest:
                print(f"[ERROR] Activo '{args.asset_id}' no encontrado en el catálogo", file=sys.stderr)
                return 1

            if args.json:
                print(json.dumps(manifest, indent=2, ensure_ascii=False))
            else:
                print(f"\n--- INSPECCIÓN DE ACTIVO: {manifest['asset_id']} ---")
                print(f"Nombre: {manifest.get('name')}")
                print(f"Tipo: {manifest.get('kind')}")
                geom = manifest.get("geometry", {})
                print(f"Disposición: {geom.get('layout_type')} | Celda: {geom.get('frame_size')}")
                prov = manifest.get("provenance", {})
                print(f"Autor: {prov.get('author')} | Fuente: {prov.get('source_repo')}")
                print(f"Licencia: {prov.get('license_spdx')} ({prov.get('license_tier')})")
                print(f"Atribución requerida: {prov.get('attribution_required')}")
                clips = manifest.get("character_data", {}).get("available_clips", [])
                if clips:
                    print("Clips de animación:")
                    for c in clips:
                        print(f"  - {c.get('name')}: {c.get('frame_count')} frames (duración: {c.get('duration_ms')}ms)")
                print("")
            return 0

        elif args.command == "validate":
            validator = AssetValidator(db)
            if args.all:
                all_assets = db.list_all()
                total_errors = 0
                reports = []
                for a in all_assets:
                    rep = validator.validate_manifest_and_image(a)
                    reports.append(rep)
                    if not rep.is_valid:
                        total_errors += 1

                if args.json:
                    print(json.dumps([r.to_dict() for r in reports], indent=2, ensure_ascii=False))
                else:
                    print(f"\n--- AUDITORÍA DE CATÁLOGO ({len(reports)} activos validados) ---")
                    for rep in reports:
                        status = "APROBADO" if rep.is_valid else "FALLIDO"
                        print(f"Activo [{rep.asset_id}]: {status}")
                        for err in rep.errors:
                            print(f"  - ERROR: {err}")
                        for warn in rep.warnings:
                            print(f"  - AVISO: {warn}")
                    print(f"\nResultado final: {len(reports) - total_errors} aprobados, {total_errors} con errores.")
                return 1 if total_errors > 0 else 0
            else:
                if not args.asset_id:
                    print("[ERROR] Debe indicar un asset_id o usar --all", file=sys.stderr)
                    return 1
                manifest = db.get_asset(args.asset_id)
                if not manifest:
                    print(f"[ERROR] Activo '{args.asset_id}' no encontrado", file=sys.stderr)
                    return 1
                rep = validator.validate_manifest_and_image(manifest)
                if args.json:
                    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
                else:
                    status = "APROBADO" if rep.is_valid else "FALLIDO"
                    print(f"\nAuditoría para [{rep.asset_id}]: {status}")
                    for err in rep.errors:
                        print(f"  - ERROR: {err}")
                    for warn in rep.warnings:
                        print(f"  - AVISO: {warn}")
                    print(f"Reglas aprobadas: {rep.passed_rules}\n")
                return 0 if rep.is_valid else 1

        elif args.command == "preview":
            manifest = db.get_asset(args.asset_id)
            if not manifest:
                print(f"[ERROR] Activo '{args.asset_id}' no encontrado", file=sys.stderr)
                return 1

            previewer = AssetPreviewer()
            if args.window:
                previewer.launch_interactive_viewer(manifest)
                return 0
            else:
                out = previewer.generate_headless_preview(
                    manifest,
                    clip_name=args.clip,
                    output_path=args.output,
                    scale=args.scale,
                )
                print(f"[ASSET HUB] Previsualización headless generada con éxito: {out.resolve()}")
                return 0

        elif args.command == "export":
            exporter = AssetExporter(db)
            res = exporter.export_asset(args.asset_id, args.target)
            print(f"[ASSET HUB] Activo '{args.asset_id}' exportado con éxito a: {res['target_dir']}")
            for f in res["exported_files"]:
                print(f"  - Archivo generado: {f}")
            return 0

        elif args.command == "credits":
            exporter = AssetExporter(db)
            out_path = Path(args.output)
            exporter.generate_credits_markdown(out_path)
            print(f"[ASSET HUB] Documento de créditos generado con éxito en: {out_path.resolve()}")
            return 0

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
