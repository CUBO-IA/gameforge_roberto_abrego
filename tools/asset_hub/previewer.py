"""Previsualizador headless e interactivo para sprites, animaciones, tilesets y componentes 9-slice."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pygame


class AssetPreviewer:
    """Generador de previsualizaciones de inspección para agentes y desarrolladores."""

    def __init__(self) -> None:
        pygame.init()

    def generate_headless_preview(
        self,
        manifest: dict[str, Any],
        clip_name: str | None = None,
        output_path: Path | str | None = None,
        base_dir: Path | str | None = None,
        scale: int = 2,
    ) -> Path:
        """Genera una hoja de contacto / tira de fotogramas de previsualización en modo headless."""
        base = Path(base_dir) if base_dir else Path.cwd()
        asset_id = manifest.get("asset_id", "asset")

        img_info = manifest.get("image", {})
        rel_img = img_info.get("relative_path", "")
        full_img_path = base / rel_img if not Path(rel_img).is_absolute() else Path(rel_img)

        if not full_img_path.is_file():
            raise FileNotFoundError(f"Imagen del activo no encontrada: {full_img_path}")

        source_surface = pygame.image.load(str(full_img_path))
        if pygame.display.get_surface() is not None:
            source_surface = source_surface.convert_alpha()

        geom = manifest.get("geometry", {})
        frame_size = geom.get("frame_size", [source_surface.get_width(), source_surface.get_height()])
        fw, fh = frame_size[0], frame_size[1]
        anchor = geom.get("anchor_offset", [fw // 2, fh])

        char_data = manifest.get("character_data", {})
        available_clips = char_data.get("available_clips", [])

        # Determinar clip a previsualizar
        target_clip = None
        if clip_name:
            target_clip = next((c for c in available_clips if c.get("name") == clip_name), None)
        if not target_clip and available_clips:
            target_clip = available_clips[0]

        frame_count = target_clip.get("frame_count", 1) if target_clip else 1
        active_clip_name = target_clip.get("name", "default") if target_clip else "default"

        # Extraer fotogramas de la fila superior o uniforme
        frames: list[pygame.Surface] = []
        cols = max(1, source_surface.get_width() // fw)

        for i in range(min(frame_count, cols)):
            sub_rect = pygame.Rect(i * fw, 0, fw, fh)
            cell = pygame.Surface((fw, fh), pygame.SRCALPHA)
            cell.blit(source_surface, (0, 0), sub_rect)

            # Dibujar guías de inspección en una superficie de lienzo
            canvas = pygame.Surface((fw, fh), pygame.SRCALPHA)
            canvas.blit(cell, (0, 0))

            # Dibujar cruz de anclaje (pivote) en cian
            px, py = anchor[0], anchor[1]
            pygame.draw.line(canvas, (40, 220, 255, 200), (px - 3, py), (px + 3, py), 1)
            pygame.draw.line(canvas, (40, 220, 255, 200), (px, py - 3), (px, py + 3), 1)

            # Escalar para mejor inspección de píxel
            if scale > 1:
                scaled_canvas = pygame.transform.scale(canvas, (fw * scale, fh * scale))
                frames.append(scaled_canvas)
            else:
                frames.append(canvas)

        if not frames:
            # Fallback a la imagen completa si no hay fotogramas
            frames = [source_surface]

        # Componer tira horizontal con fondo neutro de inspección
        total_w = sum(f.get_width() for f in frames) + (len(frames) + 1) * 4
        max_h = max(f.get_height() for f in frames) + 8

        strip = pygame.Surface((total_w, max_h))
        strip.fill((30, 30, 36))  # Fondo gris oscuro

        curr_x = 4
        for f in frames:
            strip.blit(f, (curr_x, 4))
            # Borde sutil alrededor de cada frame
            pygame.draw.rect(strip, (60, 60, 75), (curr_x - 1, 3, f.get_width() + 2, f.get_height() + 2), 1)
            curr_x += f.get_width() + 4

        # Determinar ruta de salida
        if output_path is None:
            out_file = Path("artifacts/previews") / f"{asset_id}_{active_clip_name}_preview.png"
        else:
            out_file = Path(output_path)

        out_file.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(strip, str(out_file))

        # Intentar también generar GIF animado si Pillow estuviera disponible
        try:
            from PIL import Image
            pil_frames = []
            for f in frames:
                data = pygame.image.tobytes(f, "RGBA")
                img = Image.frombytes("RGBA", f.get_size(), data).convert("RGB")
                pil_frames.append(img)
            gif_path = out_file.with_suffix(".gif")
            pil_frames[0].save(
                str(gif_path),
                save_all=True,
                append_images=pil_frames[1:],
                duration=100,
                loop=0,
            )
        except Exception:
            pass

        return out_file

    def launch_interactive_viewer(self, manifest: dict[str, Any], base_dir: Path | str | None = None) -> None:
        """Abre una ventana ligera interactiva para inspección humana."""
        base = Path(base_dir) if base_dir else Path.cwd()
        img_info = manifest.get("image", {})
        rel_img = img_info.get("relative_path", "")
        full_img_path = base / rel_img if not Path(rel_img).is_absolute() else Path(rel_img)

        source_surface = pygame.image.load(str(full_img_path))
        if pygame.display.get_surface() is not None:
            source_surface = source_surface.convert_alpha()
        geom = manifest.get("geometry", {})
        frame_size = geom.get("frame_size", [source_surface.get_width(), source_surface.get_height()])
        fw, fh = frame_size[0], frame_size[1]

        screen = pygame.display.set_mode((400, 400))
        pygame.display.set_caption(f"GameForge Asset Hub Preview: {manifest.get('name', 'Asset')}")
        clock = pygame.time.Clock()

        running = True
        frame_idx = 0
        timer = 0.0

        cols = max(1, source_surface.get_width() // fw)

        while running:
            dt = clock.tick(60) / 1000.0
            timer += dt
            if timer >= 0.15:  # 150 ms por fotograma
                timer = 0.0
                frame_idx = (frame_idx + 1) % cols

            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    running = False

            screen.fill((25, 25, 30))
            sub_rect = pygame.Rect(frame_idx * fw, 0, fw, fh)
            cell = pygame.Surface((fw, fh), pygame.SRCALPHA)
            cell.blit(source_surface, (0, 0), sub_rect)

            scaled_cell = pygame.transform.scale(cell, (fw * 4, fh * 4))
            screen.blit(scaled_cell, (200 - (fw * 2), 200 - (fh * 2)))
            pygame.display.flip()

        pygame.display.quit()
