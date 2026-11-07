"""Herramienta de previsualización autónoma de animaciones gf-anim-v1.

Permite a agentes de IA exportar secuencias de fotogramas o GIFs animados en modo headless,
o a desarrolladores humanos inspeccionar clips interactivamente con visualización de cajas de colisión y sockets.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pygame

from game.render.animation import AnimationClip, load_animation_manifest


def render_clip_to_surfaces(
    clip: AnimationClip,
    draw_boxes: bool = True,
    draw_sockets: bool = True,
    canvas_size: tuple[int, int] = (128, 128),
) -> list[pygame.Surface]:
    """Renderiza cada fotograma del clip sobre un lienzo centrado en su pivote."""
    rendered_frames: list[pygame.Surface] = []
    cw, ch = canvas_size
    origin_x = cw // 2
    origin_y = int(ch * 0.8)  # Pies en el 80% de la altura

    for frame in clip.frames:
        surf = pygame.Surface((cw, ch), pygame.SRCALPHA)
        surf.fill((40, 40, 48, 255))  # Fondo neutro para visualización

        # Sombra básica proyectada en el suelo
        pygame.draw.ellipse(surf, (20, 20, 25), (origin_x - 18, origin_y - 6, 36, 12))

        # Dibujar sprite del frame respetando su pivote
        px, py = frame.pivot
        blit_x = origin_x - px
        blit_y = origin_y - py
        surf.blit(frame.surface, (blit_x, blit_y))

        # Dibujar cajas pasivas (Hurtbox) en verde
        if draw_boxes:
            for hx, hy, hw, hh in frame.hurtboxes:
                box_rect = pygame.Rect(origin_x + hx, origin_y + hy, hw, hh)
                # Contorno verde
                pygame.draw.rect(surf, (60, 220, 60), box_rect, width=1)

            # Dibujar cajas ofensivas (Hitbox) en rojo
            for hb in frame.hitboxes:
                hbx, hby, hbw, hbh = hb.rect
                hit_rect = pygame.Rect(origin_x + hbx, origin_y + hby, hbw, hbh)
                # Contorno rojo brillante
                pygame.draw.rect(surf, (240, 40, 40), hit_rect, width=2)

        # Dibujar sockets en amarillo / cian
        if draw_sockets:
            for sname, (sx, sy) in frame.sockets.items():
                abs_sx = blit_x + sx
                abs_sy = blit_y + sy
                color = (255, 220, 40) if "hand" in sname else (40, 220, 255)
                pygame.draw.circle(surf, color, (abs_sx, abs_sy), 2)

        # Cruz guía en el punto invariante (pivote de contacto con el suelo)
        pygame.draw.line(surf, (255, 255, 255, 120), (origin_x - 4, origin_y), (origin_x + 4, origin_y), 1)
        pygame.draw.line(surf, (255, 255, 255, 120), (origin_x, origin_y - 4), (origin_x, origin_y + 4), 1)

        rendered_frames.append(surf)

    return rendered_frames


def export_gif(
    surfaces: list[pygame.Surface],
    output_path: Path,
    durations_ms: list[int],
) -> bool:
    """Exporta las superficies generadas como un archivo GIF animado."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image

        pil_images = []
        for surf in surfaces:
            data = pygame.image.tobytes(surf, "RGBA")
            img = Image.frombytes("RGBA", surf.get_size(), data)
            pil_images.append(img.convert("RGB"))

        if pil_images:
            duration = durations_ms[0] if durations_ms else 100
            pil_images[0].save(
                str(output_path),
                save_all=True,
                append_images=pil_images[1:],
                duration=duration,
                loop=0,
            )
            return True
    except ImportError:
        # Fallback si Pillow no está instalado: guardar primer frame como PNG de preview
        fallback_png = output_path.with_suffix(".png")
        if surfaces:
            pygame.image.save(surfaces[0], str(fallback_png))
            print(f"[AVISO] Pillow no disponible para GIF; guardado frame estático: {fallback_png}")
            return True
    except Exception as err:
        print(f"[ERROR] Error al exportar GIF: {err}", file=sys.stderr)
        return False
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Previsualizador de animaciones gf-anim-v1")
    parser.add_argument("--manifest", "-m", type=str, required=True, help="Ruta al archivo .anim.json")
    parser.add_argument("--clip", "-c", type=str, default=None, help="Nombre del clip a previsualizar")
    parser.add_argument("--export-gif", type=str, default=None, help="Ruta donde guardar el GIF animado")
    parser.add_argument("--export-frames-dir", type=str, default=None, help="Directorio donde exportar fotogramas PNG")
    parser.add_argument("--no-boxes", action="store_true", help="Desactiva el dibujo de hitboxes y hurtboxes")
    parser.add_argument("--window", action="store_true", help="Abre una ventana interactiva")

    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"[ERROR] No se encontró el manifiesto: {manifest_path}", file=sys.stderr)
        return 1

    # Inicializar pygame básico
    pygame.init()

    try:
        clips, metadata = load_animation_manifest(manifest_path)
    except Exception as err:
        print(f"[ERROR] Falló la carga del manifiesto: {err}", file=sys.stderr)
        return 1

    clip_name = args.clip or next(iter(clips.keys()))
    clip = clips.get(clip_name)
    if not clip:
        print(f"[ERROR] El clip '{clip_name}' no existe en {manifest_path}. Clips disponibles: {list(clips.keys())}")
        return 1

    print(f"Previsualizando '{metadata.get('id')}' -> Clip: '{clip_name}' ({len(clip.frames)} fotogramas)")

    draw_boxes = not args.no_boxes
    rendered_surfs = render_clip_to_surfaces(clip, draw_boxes=draw_boxes)
    durations = [int(f.duration * 1000) for f in clip.frames]

    # Exportación headless de fotogramas
    if args.export_frames_dir:
        out_dir = Path(args.export_frames_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, s in enumerate(rendered_surfs):
            fpath = out_dir / f"frame_{i:02d}.png"
            pygame.image.save(s, str(fpath))
        print(f"[OK] {len(rendered_surfs)} fotogramas exportados a {out_dir}")

    # Exportación headless a GIF
    if args.export_gif:
        gif_path = Path(args.export_gif)
        success = export_gif(rendered_surfs, gif_path, durations)
        if success:
            print(f"[OK] GIF generado exitosamente en: {gif_path}")

    # Modo ventana interactiva opcional
    if args.window:
        screen = pygame.display.set_mode((400, 400))
        pygame.display.set_caption(f"GF-Anim: {clip_name}")
        clock = pygame.time.Clock()
        frame_idx = 0
        timer = 0.0
        running = True

        while running:
            dt = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            timer += dt
            if timer >= clip.frames[frame_idx].duration:
                timer -= clip.frames[frame_idx].duration
                frame_idx = (frame_idx + 1) % len(clip.frames)

            screen.fill((20, 20, 24))
            scaled = pygame.transform.scale(rendered_surfs[frame_idx], (384, 384))
            screen.blit(scaled, (8, 8))
            pygame.display.flip()

        pygame.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
