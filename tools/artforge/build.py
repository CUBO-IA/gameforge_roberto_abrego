"""Pipeline de generación de arte de GameForge (offline, determinista).

Uso:
    python -m tools.artforge.build

Escribe los PNG en ``assets/`` y hojas de contacto en
``artifacts/art_preview/`` para inspección visual. El juego nunca ejecuta
este paquete: solo consume los PNG y sus manifiestos.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

from tools.artforge import characters as chars  # noqa: E402
from tools.artforge.atlas import build_manifest, pack, write_manifest  # noqa: E402
from tools.artforge.pixel import Canvas, contact_sheet  # noqa: E402
from tools.artforge.tiles import build_tileset  # noqa: E402

ART_ROOT = Path("assets/art")
SPRITE_ROOT = Path("assets/sprites")
PREVIEW_ROOT = Path("artifacts/art_preview")


def _ensure(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_tiles(scale: int = 4) -> dict[str, object]:
    atlas, manifest = build_tileset()
    target = _ensure(ART_ROOT / "tiles")
    atlas.save(str(target / "dungeon_tileset.png"))
    (target / "dungeon_tileset.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    preview = _ensure(PREVIEW_ROOT)
    frames: list[tuple[str, Canvas]] = []
    for name, entry in manifest["tiles"].items():  # type: ignore[union-attr]
        rect = entry["rect"]
        tile = Canvas(rect[2], rect[3])
        tile.surface.blit(atlas.surface, (0, 0), pygame.Rect(rect[0], rect[1], rect[2], rect[3]))
        frames.append((name, tile))
    contact_sheet(frames, str(preview / "tiles_contact.png"), scale=scale, columns=8)
    return manifest


def build_hero(scale: int = 3) -> dict[str, object]:
    frames = chars.build_hero_frames()
    atlas, rects = pack(frames, chars.HERO_W, chars.HERO_H, columns=12, pivot=chars.HERO_PIVOT)
    target = _ensure(SPRITE_ROOT / "characters" / "player")
    atlas.save(str(target / "knight_hero_atlas.png"))
    manifest = build_manifest(
        asset_id="knight_hero",
        display_name="Caballero Forjador",
        description="Guerrero de la Forja con yelmo de visor cian, tabardo teal y espada larga",
        tags=["player", "melee", "humanoid", "dark-fantasy"],
        image_name="knight_hero_atlas.png",
        atlas=atlas,
        rects=rects,
        clips=chars.HERO_CLIPS,
        pivot=chars.HERO_PIVOT,
        hurtbox=(-10, -40, 20, 38),
    )
    write_manifest(target / "knight_hero.anim.json", manifest)
    (target / "knight_hero_atlas.png.meta.json").write_text(
        json.dumps(
            {
                "asset_id": "knight_hero",
                "author": "GameForge ArtForge",
                "license": "MIT",
                "origin": "Generado internamente por tools/artforge/characters.py",
                "frame_size": [chars.HERO_W, chars.HERO_H],
                "frames": len(frames),
                "modified": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    contact_sheet(
        frames, str(_ensure(PREVIEW_ROOT) / "hero_contact.png"), scale=scale, columns=9
    )
    return manifest


ENEMY_SPECS = {
    "slime": {
        "build": chars.build_slime_frames,
        "clips": chars.SLIME_CLIPS,
        "size": (chars.SLIME_W, chars.SLIME_H),
        "pivot": (16, 32),
        "name": "Cieno",
        "description": "Masa de cieno verdoso con núcleo y ojos brillantes",
        "tags": ["enemy", "melee", "ooze"],
        "hurtbox": (-11, -18, 22, 16),
    },
    "wisp": {
        "build": chars.build_wisp_frames,
        "clips": chars.WISP_CLIPS,
        "size": (chars.WISP_W, chars.WISP_H),
        "pivot": (16, 32),
        "name": "Fuego fatuo",
        "description": "Llama espectral cian-violeta con máscara y chispas orbitales",
        "tags": ["enemy", "ranged", "spirit"],
        "hurtbox": (-9, -22, 18, 20),
    },
    "brute": {
        "build": chars.build_brute_frames,
        "clips": chars.BRUTE_CLIPS,
        "size": (chars.BRUTE_W, chars.BRUTE_H),
        "pivot": (24, 46),
        "name": "Bruto de escoria",
        "description": "Ogro de escoria con placas de hierro, grietas de lava y mandoble",
        "tags": ["enemy", "charger", "ogre"],
        "hurtbox": (-14, -38, 28, 34),
    },
}


def build_enemy(kind: str, scale: int = 3) -> dict[str, object]:
    spec = ENEMY_SPECS[kind]
    frames = spec["build"]()
    width, height = spec["size"]
    atlas, rects = pack(frames, width, height, columns=6, pivot=spec["pivot"])
    target = _ensure(SPRITE_ROOT / "enemies" / kind)
    atlas.save(str(target / f"{kind}_atlas.png"))
    manifest = build_manifest(
        asset_id=kind,
        display_name=spec["name"],
        description=spec["description"],
        tags=spec["tags"],
        image_name=f"{kind}_atlas.png",
        atlas=atlas,
        rects=rects,
        clips=spec["clips"],
        pivot=spec["pivot"],
        hurtbox=spec["hurtbox"],
    )
    write_manifest(target / f"{kind}.anim.json", manifest)
    (target / f"{kind}_atlas.png.meta.json").write_text(
        json.dumps(
            {
                "asset_id": kind,
                "author": "GameForge ArtForge",
                "license": "MIT",
                "origin": "Generado internamente por tools/artforge/characters.py",
                "frame_size": [width, height],
                "frames": len(frames),
                "modified": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    contact_sheet(
        frames, str(_ensure(PREVIEW_ROOT) / f"{kind}_contact.png"), scale=scale, columns=8
    )
    return manifest


def build_hero_and_enemies(scale: int = 3) -> dict[str, object]:
    summary = {"hero": build_hero(scale)}
    for kind in ENEMY_SPECS:
        summary[kind] = build_enemy(kind, scale)
    return summary


def build_objects(scale: int = 3) -> dict[str, object]:
    from tools.artforge import objects

    atlas, manifest = objects.build_objects()
    target = _ensure(ART_ROOT / "objects")
    atlas.save(str(target / "objects.png"))
    (target / "objects.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    frames: list[tuple[str, Canvas]] = []
    for name, entry in manifest["objects"].items():  # type: ignore[union-attr]
        x, y, w, h = entry["rect"]
        piece = Canvas(w, h)
        piece.surface.blit(atlas.surface, (0, 0), pygame.Rect(x, y, w, h))
        frames.append((name, piece))
    contact_sheet(frames, str(_ensure(PREVIEW_ROOT) / "objects_contact.png"), scale=scale, columns=6)
    return manifest


def build_vfx(scale: int = 4) -> dict[str, object]:
    from tools.artforge import vfx

    atlas, manifest = vfx.build_particles()
    target = _ensure(ART_ROOT / "vfx")
    atlas.save(str(target / "particles.png"))
    (target / "particles.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    frames: list[tuple[str, Canvas]] = []
    for name, entry in manifest["sprites"].items():  # type: ignore[union-attr]
        x, y, w, h = entry["rect"]
        piece = Canvas(w, h)
        piece.surface.blit(atlas.surface, (0, 0), pygame.Rect(x, y, w, h))
        frames.append((name, piece))
    contact_sheet(frames, str(_ensure(PREVIEW_ROOT) / "vfx_contact.png"), scale=scale, columns=6)
    return manifest


def build_ui(scale: int = 4) -> dict[str, object]:
    from tools.artforge import ui

    atlas, manifest = ui.build_ui()
    target = _ensure(ART_ROOT / "ui")
    atlas.save(str(target / "ui.png"))
    (target / "ui.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    frames: list[tuple[str, Canvas]] = []
    for name, entry in manifest["elements"].items():  # type: ignore[union-attr]
        x, y, w, h = entry["rect"]
        piece = Canvas(w, h)
        piece.surface.blit(atlas.surface, (0, 0), pygame.Rect(x, y, w, h))
        frames.append((name, piece))
    contact_sheet(frames, str(_ensure(PREVIEW_ROOT) / "ui_contact.png"), scale=scale, columns=5)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", default="build", choices=("build", "tiles", "characters"))
    parser.add_argument("--scale", type=int, default=3)
    args = parser.parse_args(argv)

    pygame.init()
    if args.command in ("build", "tiles"):
        manifest = build_tiles(scale=max(2, args.scale + 1))
        print(f"tiles: {len(manifest['tiles'])} tiles -> assets/art/tiles/dungeon_tileset.png")
    if args.command in ("build", "characters"):
        summary = build_hero_and_enemies(scale=max(2, args.scale))
        for key, manifest in summary.items():
            print(f"actor {key}: {len(manifest['clips'])} clips, {len(manifest['frames'])} frames")
    if args.command == "build":
        print(f"objects: {len(build_objects()['objects'])} piezas")
        print(f"vfx: {len(build_vfx()['sprites'])} sprites")
        print(f"ui: {len(build_ui()['elements'])} elementos")
    print(f"previews -> {PREVIEW_ROOT}")
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
