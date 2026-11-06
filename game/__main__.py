"""Punto de entrada CLI: ``python -m game``."""

from __future__ import annotations

import argparse
import logging
import sys

from game import __version__
from game.app import Application
from game.core.config import ConfigError, load_config
from game.persistence.savegame import SaveGameError
from game.world.generation import GenerationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gameforge",
        description="GAMEFORGE 2D — La Fragua Olvidada",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", type=str, default=None, help="Ruta a config.json")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Directorio de guardados y SQLite (por defecto, datos de usuario).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Sin ventana real (SDL dummy). Útil para CI y smoke tests.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=None,
        help="Detener tras N frames (por defecto: infinito; 120 en headless).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Semilla de la mazmorra. Implica iniciar una partida nueva.",
    )
    parser.add_argument(
        "--new-game",
        action="store_true",
        help="Saltar el menú e iniciar una partida nueva.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    if args.frames is not None and args.frames < 0:
        parser.error("--frames no puede ser negativo.")

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Error de configuración: {exc}", file=sys.stderr)
        return 2

    try:
        app = Application(config, data_dir=args.data_dir, headless=args.headless)
    except RuntimeError as exc:
        print(f"Error al iniciar: {exc}", file=sys.stderr)
        return 3

    try:
        if args.new_game or args.seed is not None:
            from game.scenes.play import PlayScene

            app.replace_scene(PlayScene(app, seed=args.seed))
        frames = args.frames
        if args.headless and frames is None:
            frames = 120
        app.run(frames)
    except (GenerationError, SaveGameError) as exc:
        print(f"Error durante la partida: {exc}", file=sys.stderr)
        return 4
    finally:
        app.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
