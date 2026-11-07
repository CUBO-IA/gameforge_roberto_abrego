"""Ciclo de vida de la aplicación: ventana, escenas, entrada y servicios."""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path

import pygame

from game.core.config import GameConfig, load_config
from game.input.actions import InputMapper
from game.persistence.paths import resolve_data_dir, save_file, scores_file
from game.persistence.savegame import SaveGameError, delete_save
from game.persistence.scores import RunResult, ScoreEntry, ScoreError, ScoreRepository
from game.render.audio import Audio
from game.render.canvas import VirtualCanvas
from game.render.fonts import FontCache

logger = logging.getLogger(__name__)

WINDOW_ICON_SIZE = 32


class Application:
    def __init__(
        self,
        config: GameConfig | None = None,
        data_dir: str | Path | None = None,
        headless: bool = False,
    ) -> None:
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        self.config = config or load_config()
        self.headless = headless
        self.data_dir = resolve_data_dir(data_dir)
        self.running = True
        self.fps = float(self.config.window.fps)
        self._scenes: list[object] = []

        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        try:
            self.screen = pygame.display.set_mode(
                (self.config.window.width, self.config.window.height)
            )
        except pygame.error as exc:
            pygame.quit()
            raise RuntimeError(f"No se pudo crear la ventana: {exc}") from exc
        pygame.display.set_caption(self.config.window.title)
        pygame.display.set_icon(self._make_icon())
        self.clock = pygame.time.Clock()
        self.input = InputMapper()
        self.fonts = FontCache()
        self.canvas = VirtualCanvas(
            logical_width=self.config.window.width,
            logical_height=self.config.window.height,
            initial_window_size=(self.config.window.width, self.config.window.height),
        )
        self.audio = Audio(self.config.audio.master_volume)
        self.save_path = save_file(self.data_dir)

        self.scores: ScoreRepository | None = None
        self.score_error: str | None = None
        try:
            self.scores = ScoreRepository(scores_file(self.data_dir))
        except (sqlite3.Error, OSError) as exc:
            self.score_error = f"Clasificación no disponible: {exc}"
            logger.error("No se pudo abrir SQLite: %s", exc)

        from game.scenes.menu import MenuScene

        self.replace_scene(MenuScene(self))

    @property
    def scene(self) -> object | None:
        return self._scenes[-1] if self._scenes else None

    def replace_scene(self, scene: object) -> None:
        if self._scenes:
            previous = self._scenes[-1]
            if hasattr(previous, "on_exit"):
                previous.on_exit()
        self._scenes = [scene]
        if hasattr(scene, "on_enter"):
            scene.on_enter()

    def push_scene(self, scene: object) -> None:
        self._scenes.append(scene)
        if hasattr(scene, "on_enter"):
            scene.on_enter()

    def pop_scene(self) -> None:
        if not self._scenes:
            return
        previous = self._scenes.pop()
        if hasattr(previous, "on_exit"):
            previous.on_exit()
        if self._scenes and hasattr(self._scenes[-1], "on_enter"):
            self._scenes[-1].on_enter()

    def run(self, max_frames: int | None = None) -> int:
        frames = 0
        while self.running:
            elapsed = self.clock.tick(self.config.window.fps) / 1000.0
            dt = min(max(elapsed, 0.0), 0.05)
            if dt > 0:
                self.fps = self.fps * 0.9 + (1.0 / dt) * 0.1
            self.input.begin_frame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.VIDEORESIZE:
                    self.canvas.resize_window(event.w, event.h)
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.input.handle_event(event)
                current = self.scene
                if current is not None:
                    current.handle_event(event)  # type: ignore[attr-defined]
            if not self.running:
                break
            current = self.scene
            if current is None:
                break
            current.update(dt)  # type: ignore[attr-defined]
            current = self.scene
            if current is None:
                break
            current.draw(self.canvas.surface)  # type: ignore[attr-defined]
            self.canvas.render_to_display(self.screen)
            pygame.display.flip()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
        return frames

    def record_result(self, result: RunResult) -> str | None:
        if self.scores is None:
            return self.score_error or "La clasificación no está disponible."
        try:
            self.scores.record(result)
            return None
        except (sqlite3.Error, ScoreError) as exc:
            logger.error("No se pudo registrar la partida: %s", exc)
            return f"No se pudo guardar la puntuación: {exc}"

    def top_scores(self, limit: int = 10) -> tuple[list[ScoreEntry] | None, str | None]:
        if self.scores is None:
            return None, self.score_error or "La clasificación no está disponible."
        try:
            return self.scores.top(limit), None
        except (sqlite3.Error, ScoreError) as exc:
            logger.error("No se pudo leer la clasificación: %s", exc)
            return None, f"No se pudo leer la clasificación: {exc}"

    def has_save(self) -> bool:
        return self.save_path.is_file()

    def discard_save(self) -> str | None:
        try:
            delete_save(self.save_path)
            return None
        except SaveGameError as exc:
            logger.error("No se pudo borrar el guardado: %s", exc)
            return str(exc)

    def request_quit(self) -> None:
        self.running = False

    def shutdown(self) -> None:
        if self.scores is not None:
            self.scores.close()
            self.scores = None
        self.audio.shutdown()
        self.fonts.clear()
        pygame.quit()

    @staticmethod
    def _make_icon() -> pygame.Surface:
        icon = pygame.Surface((WINDOW_ICON_SIZE, WINDOW_ICON_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(icon, (18, 16, 26), icon.get_rect(), border_radius=6)
        pygame.draw.polygon(
            icon,
            (230, 92, 42),
            [(16, 5), (24, 16), (20, 26), (12, 26), (8, 16)],
        )
        pygame.draw.polygon(
            icon,
            (255, 196, 90),
            [(16, 11), (20, 18), (16, 25), (13, 18)],
        )
        return icon
