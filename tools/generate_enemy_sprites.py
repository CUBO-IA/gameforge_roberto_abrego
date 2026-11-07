"""Generador de atlas de textura y manifiestos de animación gf-anim-v1 para enemigos.

Crea atlas de marcadores gráficos con paletas acordes a cada enemigo (Cieno, Fuego fatuo, Bruto)
y sus respectivos archivos .anim.json válidos según la especificación del motor.
"""

from __future__ import annotations

import json
from pathlib import Path

import pygame


def generate_enemy_assets() -> None:
    pygame.init()
    base_dir = Path("assets/sprites/enemies")

    enemies_spec = [
        {
            "id": "slime",
            "name": "Cieno de las Profundidades",
            "dir": base_dir / "slime",
            "atlas_name": "slime_atlas.png",
            "manifest_name": "slime.anim.json",
            "atlas_size": (256, 256),
            "frames": [
                {"id": "idle_0", "rect": [0, 0, 32, 32], "pivot": [16, 32], "dur": 160, "color": (80, 200, 100)},
                {"id": "idle_1", "rect": [32, 0, 32, 32], "pivot": [16, 32], "dur": 160, "color": (90, 215, 110)},
                {"id": "walk_0", "rect": [64, 0, 32, 32], "pivot": [16, 32], "dur": 130, "color": (70, 190, 90)},
                {"id": "attack_0", "rect": [96, 0, 32, 32], "pivot": [16, 32], "dur": 180, "color": (110, 230, 120)},
                {"id": "hurt_0", "rect": [128, 0, 32, 32], "pivot": [16, 32], "dur": 150, "color": (220, 100, 100)},
                {"id": "die_0", "rect": [160, 0, 32, 32], "pivot": [16, 32], "dur": 400, "color": (50, 80, 50)},
            ],
            "clips": {
                "idle": {"frames": ["idle_0", "idle_1"], "loop": True, "playback_speed": 1.0, "interrupt_priority": 0},
                "walk": {"frames": ["walk_0", "idle_0"], "loop": True, "playback_speed": 1.0, "interrupt_priority": 0},
                "attack": {"frames": ["attack_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 3},
                "hurt": {"frames": ["hurt_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 4},
                "die": {"frames": ["die_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 10},
            },
        },
        {
            "id": "wisp",
            "name": "Fuego Fatuo Arcano",
            "dir": base_dir / "wisp",
            "atlas_name": "wisp_atlas.png",
            "manifest_name": "wisp.anim.json",
            "atlas_size": (256, 256),
            "frames": [
                {"id": "idle_0", "rect": [0, 0, 28, 28], "pivot": [14, 28], "dur": 140, "color": (160, 110, 240)},
                {"id": "idle_1", "rect": [28, 0, 28, 28], "pivot": [14, 28], "dur": 140, "color": (180, 130, 255)},
                {"id": "walk_0", "rect": [56, 0, 28, 28], "pivot": [14, 28], "dur": 120, "color": (140, 90, 220)},
                {"id": "shoot_0", "rect": [84, 0, 28, 28], "pivot": [14, 28], "dur": 200, "color": (210, 160, 255)},
                {"id": "hurt_0", "rect": [112, 0, 28, 28], "pivot": [14, 28], "dur": 150, "color": (240, 110, 110)},
                {"id": "die_0", "rect": [140, 0, 28, 28], "pivot": [14, 28], "dur": 400, "color": (60, 40, 90)},
            ],
            "clips": {
                "idle": {"frames": ["idle_0", "idle_1"], "loop": True, "playback_speed": 1.0, "interrupt_priority": 0},
                "walk": {"frames": ["walk_0", "idle_0"], "loop": True, "playback_speed": 1.0, "interrupt_priority": 0},
                "shoot": {"frames": ["shoot_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 3},
                "hurt": {"frames": ["hurt_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 4},
                "die": {"frames": ["die_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 10},
            },
        },
        {
            "id": "brute",
            "name": "Bruto de Escoria Fundida",
            "dir": base_dir / "brute",
            "atlas_name": "brute_atlas.png",
            "manifest_name": "brute.anim.json",
            "atlas_size": (256, 256),
            "frames": [
                {"id": "idle_0", "rect": [0, 0, 44, 44], "pivot": [22, 44], "dur": 180, "color": (200, 100, 80)},
                {"id": "idle_1", "rect": [44, 0, 44, 44], "pivot": [22, 44], "dur": 180, "color": (215, 115, 90)},
                {"id": "walk_0", "rect": [88, 0, 44, 44], "pivot": [22, 44], "dur": 150, "color": (185, 85, 70)},
                {"id": "windup_0", "rect": [132, 0, 44, 44], "pivot": [22, 44], "dur": 220, "color": (230, 130, 100)},
                {"id": "charge_0", "rect": [176, 0, 44, 44], "pivot": [22, 44], "dur": 120, "color": (255, 120, 80)},
                {"id": "attack_0", "rect": [0, 44, 44, 44], "pivot": [22, 44], "dur": 160, "color": (220, 90, 70)},
                {"id": "hurt_0", "rect": [44, 44, 44, 44], "pivot": [22, 44], "dur": 150, "color": (255, 160, 160)},
                {"id": "die_0", "rect": [88, 44, 44, 44], "pivot": [22, 44], "dur": 500, "color": (70, 30, 30)},
            ],
            "clips": {
                "idle": {"frames": ["idle_0", "idle_1"], "loop": True, "playback_speed": 1.0, "interrupt_priority": 0},
                "walk": {"frames": ["walk_0", "idle_0"], "loop": True, "playback_speed": 1.0, "interrupt_priority": 0},
                "windup": {"frames": ["windup_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 2},
                "charge": {"frames": ["charge_0"], "loop": True, "playback_speed": 1.0, "interrupt_priority": 2},
                "attack": {"frames": ["attack_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 3},
                "hurt": {"frames": ["hurt_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 4},
                "die": {"frames": ["die_0"], "loop": False, "playback_speed": 1.0, "interrupt_priority": 10},
            },
        },
    ]

    for spec in enemies_spec:
        enemy_dir: Path = spec["dir"]
        enemy_dir.mkdir(parents=True, exist_ok=True)

        atlas_w, atlas_h = spec["atlas_size"]
        atlas_surf = pygame.Surface((atlas_w, atlas_h), pygame.SRCALPHA)

        frames_manifest = []
        for f in spec["frames"]:
            x, y, w, h = f["rect"]
            col = f["color"]

            # Dibujar un rectángulo distintivo con borde y detalle
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(atlas_surf, (col[0] // 3, col[1] // 3, col[2] // 3, 255), rect)
            pygame.draw.rect(atlas_surf, (*col, 255), rect.inflate(-4, -4), border_radius=4)
            pygame.draw.circle(atlas_surf, (255, 255, 255, 220), (x + w // 2, y + h // 2), max(2, w // 8))

            frames_manifest.append({
                "id": f["id"],
                "rect": f["rect"],
                "pivot": f["pivot"],
                "duration_ms": f["dur"],
                "sockets": {
                    "shadow": f["pivot"],
                    "origin": [f["rect"][2] // 2, f["rect"][3] // 2],
                },
                "hurtboxes": [
                    [-f["pivot"][0], -f["pivot"][1], f["rect"][2], f["rect"][3]]
                ],
                "hitboxes": [],
                "events": [],
            })

        # Guardar atlas PNG
        atlas_path = enemy_dir / spec["atlas_name"]
        pygame.image.save(atlas_surf, str(atlas_path))
        print(f"[OK] Atlas generado: {atlas_path}")

        # Guardar manifiesto JSON
        manifest_data = {
            "version": "gf-anim-v1",
            "metadata": {
                "id": spec["id"],
                "display_name": spec["name"],
                "author": "GameForge Agent",
                "rig_type": "sprite_sheet",
                "description": f"Enemigo {spec['name']} animado con spritesheets.",
                "tags": ["enemy", spec["id"]],
            },
            "texture": {
                "image_path": spec["atlas_name"],
                "width": atlas_w,
                "height": atlas_h,
                "format": "RGBA",
            },
            "frames": frames_manifest,
            "clips": spec["clips"],
        }

        manifest_path = enemy_dir / spec["manifest_name"]
        manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Manifiesto generado: {manifest_path}")

    pygame.quit()


if __name__ == "__main__":
    generate_enemy_assets()
