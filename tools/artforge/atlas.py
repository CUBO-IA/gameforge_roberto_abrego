"""Empaquetado de fotogramas en atlas y escritura de manifiestos gf-anim-v1."""

from __future__ import annotations

import json
from pathlib import Path

from tools.artforge.pixel import Canvas


def pack(
    frames: list[tuple[str, Canvas]],
    frame_w: int,
    frame_h: int,
    columns: int,
    pivot: tuple[int, int],
) -> tuple[Canvas, dict[str, tuple[int, int, int, int]]]:
    """Coloca los fotogramas en una rejilla y devuelve rects por id."""
    rows = (len(frames) + columns - 1) // columns
    atlas = Canvas(columns * frame_w, rows * frame_h)
    rects: dict[str, tuple[int, int, int, int]] = {}
    for index, (frame_id, canvas) in enumerate(frames):
        col = index % columns
        row = index // columns
        x = col * frame_w
        y = row * frame_h
        # Centrado inferior dentro de la celda
        offset_x = x + (frame_w - canvas.width) // 2
        offset_y = y + (frame_h - canvas.height)
        atlas.blit(canvas, (offset_x, offset_y))
        rects[frame_id] = (x, y, frame_w, frame_h)
    return atlas, rects


def build_manifest(
    *,
    asset_id: str,
    display_name: str,
    description: str,
    tags: list[str],
    image_name: str,
    atlas: Canvas,
    rects: dict[str, tuple[int, int, int, int]],
    clips: dict[str, dict[str, object]],
    pivot: tuple[int, int],
    sockets: dict[str, tuple[int, int]] | None = None,
    hurtbox: tuple[int, int, int, int] | None = None,
    rig_type: str = "frame_by_frame",
) -> dict[str, object]:
    """Construye un manifiesto gf-anim-v1 a partir de clips declarativos."""
    frame_duration: dict[str, int] = {}
    frame_events: dict[str, list[dict[str, object]]] = {}
    frame_hitboxes: dict[str, list[dict[str, object]]] = {}

    for clip in clips.values():
        duration = int(clip.get("duration_ms", 110))
        events: dict[int, object] = clip.get("events", {})  # type: ignore[assignment]
        hitbox = clip.get("hitbox")
        for index, frame_id in enumerate(clip["frames"]):  # type: ignore[union-attr]
            frame_duration[frame_id] = duration
            if index in events:
                name = events[index]
                if name == "slash_spark":
                    frame_events.setdefault(frame_id, []).append(
                        {"name": "spawn_particle", "payload": {"type": "slash_spark"}}
                    )
                    frame_events.setdefault(frame_id, []).append(
                        {"name": "screen_shake", "payload": {"trauma": 0.35}}
                    )
                elif name == "dust_step":
                    frame_events.setdefault(frame_id, []).append(
                        {"name": "spawn_particle", "payload": {"type": "dust_step"}}
                    )
            if hitbox and index == int(hitbox[0]):
                frame_hitboxes.setdefault(frame_id, []).append(
                    {
                        "rect": list(hitbox[1]),
                        "damage": float(hitbox[2]),
                        "knockback_force": 120.0,
                        "hitstun_duration_s": 0.18,
                        "hit_sound": "hit",
                    }
                )

    default_sockets = sockets or {
        "hand_right": [pivot[0] + 6, pivot[1] - 16],
        "head": [pivot[0], pivot[1] - 34],
        "cast_point": [pivot[0] + 8, pivot[1] - 18],
        "shadow": [pivot[0], pivot[1]],
    }

    frames_json: list[dict[str, object]] = []
    for frame_id, rect in rects.items():
        frames_json.append(
            {
                "id": frame_id,
                "rect": list(rect),
                "pivot": [pivot[0], pivot[1]],
                "duration_ms": frame_duration.get(frame_id, 110),
                "sockets": default_sockets,
                "hurtboxes": [list(hurtbox)] if hurtbox else [],
                "hitboxes": frame_hitboxes.get(frame_id, []),
                "events": frame_events.get(frame_id, []),
            }
        )

    clips_json: dict[str, object] = {}
    for name, clip in clips.items():
        clips_json[name] = {
            "frames": list(clip["frames"]),  # type: ignore[arg-type]
            "loop": bool(clip.get("loop", True)),
            "playback_speed": float(clip.get("playback_speed", 1.0)),
            "interrupt_priority": int(clip.get("interrupt_priority", 0)),
        }

    return {
        "version": "gf-anim-v1",
        "metadata": {
            "id": asset_id,
            "display_name": display_name,
            "author": "GameForge ArtForge",
            "license": "MIT",
            "rig_type": rig_type,
            "description": description,
            "tags": tags,
        },
        "texture": {
            "image_path": image_name,
            "width": atlas.width,
            "height": atlas.height,
            "format": "RGBA",
        },
        "frames": frames_json,
        "clips": clips_json,
    }


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
