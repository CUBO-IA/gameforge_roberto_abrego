"""Sistema de animación 2D basado en la especificación gf-anim-v1.

Maneja la carga de manifiestos JSON, atlas de texturas, corte de subsurfaces,
puntos de anclaje (sockets), cajas de colisión y reproducción temporal con eventos.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pygame


class AnimationFormatError(ValueError):
    """Error emitido cuando un archivo de animación no cumple con la especificación gf-anim-v1."""


@dataclass(frozen=True, slots=True)
class FrameEvent:
    """Evento emitido en un fotograma específico (e.g. SFX, VFX, sacudida)."""

    name: str
    payload: dict[str, object]


@dataclass(frozen=True, slots=True)
class HitboxData:
    """Caja de ataque activa generada en un fotograma."""

    rect: tuple[int, int, int, int]  # (x, y, w, h) relativo al pivote
    damage: float
    knockback_force: float = 100.0
    hitstun_duration_s: float = 0.2
    hit_sound: str = ""


@dataclass(slots=True)
class FrameData:
    """Metadatos y superficie gráfica de un fotograma individual."""

    id: str
    rect: tuple[int, int, int, int]
    pivot: tuple[int, int]
    duration: float  # Segundos
    surface: pygame.Surface
    sockets: dict[str, tuple[int, int]]
    hurtboxes: tuple[tuple[int, int, int, int], ...]
    hitboxes: tuple[HitboxData, ...]
    events: tuple[FrameEvent, ...]


@dataclass(frozen=True, slots=True)
class AnimationClip:
    """Clip de animación compuesto por una secuencia ordenada de fotogramas."""

    name: str
    frames: tuple[FrameData, ...]
    loop: bool = True
    playback_speed: float = 1.0
    interrupt_priority: int = 0


class AnimationPlayer:
    """Reproductor de animación desacoplado del bucle de dibujo.

    Avanza en el tiempo, actualiza fotogramas y encola eventos de simulación con coste O(1).
    """

    __slots__ = (
        "clips",
        "current_clip",
        "frame_index",
        "elapsed_time",
        "is_finished",
        "pending_events",
    )

    def __init__(self, clips: dict[str, AnimationClip]) -> None:
        self.clips: dict[str, AnimationClip] = clips
        self.current_clip: AnimationClip | None = None
        self.frame_index: int = 0
        self.elapsed_time: float = 0.0
        self.is_finished: bool = False
        self.pending_events: list[FrameEvent] = []

    def play(self, clip_name: str, force_restart: bool = False) -> bool:
        """Inicia la reproducción de un clip. Devuelve True si se inició con éxito."""
        if not force_restart and self.current_clip and self.current_clip.name == clip_name:
            return True

        clip = self.clips.get(clip_name)
        if not clip:
            return False

        self.current_clip = clip
        self.frame_index = 0
        self.elapsed_time = 0.0
        self.is_finished = False
        self._enqueue_current_events()
        return True

    def interrupt_with(self, clip_name: str) -> bool:
        """Intenta interrumpir el clip actual respetando las prioridades de interrupción."""
        candidate = self.clips.get(clip_name)
        if not candidate:
            return False

        if self.current_clip and not self.is_finished:
            if candidate.interrupt_priority < self.current_clip.interrupt_priority:
                return False  # No tiene suficiente prioridad para interrumpir

        return self.play(clip_name, force_restart=True)

    def update(self, dt: float) -> list[FrameEvent]:
        """Avanza la animación y devuelve los eventos disparados en este paso temporal."""
        self.pending_events.clear()
        if not self.current_clip or self.is_finished or not self.current_clip.frames:
            return self.pending_events

        self.elapsed_time += dt * self.current_clip.playback_speed
        current_frame = self.current_clip.frames[self.frame_index]

        while self.elapsed_time >= current_frame.duration:
            self.elapsed_time -= current_frame.duration
            next_index = self.frame_index + 1

            if next_index >= len(self.current_clip.frames):
                if self.current_clip.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.current_clip.frames) - 1
                    self.is_finished = True
                    break
            else:
                self.frame_index = next_index

            current_frame = self.current_clip.frames[self.frame_index]
            self._enqueue_current_events()

        return self.pending_events

    def _enqueue_current_events(self) -> None:
        if self.current_clip and self.frame_index < len(self.current_clip.frames):
            frame = self.current_clip.frames[self.frame_index]
            self.pending_events.extend(frame.events)

    @property
    def current_frame(self) -> FrameData | None:
        """Devuelve los metadatos del fotograma actual."""
        if self.current_clip and self.frame_index < len(self.current_clip.frames):
            return self.current_clip.frames[self.frame_index]
        return None

    @property
    def current_surface(self) -> pygame.Surface | None:
        """Devuelve la superficie gráfica del fotograma actual."""
        frame = self.current_frame
        return frame.surface if frame else None

    @property
    def current_pivot(self) -> tuple[int, int]:
        """Devuelve el pivote invariante del fotograma actual."""
        frame = self.current_frame
        return frame.pivot if frame else (0, 0)

    @property
    def active_hitboxes(self) -> tuple[HitboxData, ...]:
        """Devuelve las cajas de ataque activas en este fotograma."""
        frame = self.current_frame
        return frame.hitboxes if frame else ()

    @property
    def active_hurtboxes(self) -> tuple[tuple[int, int, int, int], ...]:
        """Devuelve las cajas de daño pasivas en este fotograma."""
        frame = self.current_frame
        return frame.hurtboxes if frame else ()

    def get_socket(self, name: str) -> tuple[int, int] | None:
        """Devuelve las coordenadas locales del socket solicitado en el fotograma actual."""
        frame = self.current_frame
        if frame and name in frame.sockets:
            return frame.sockets[name]
        return None


def load_animation_manifest(
    manifest_path: str | Path,
    base_dir: Path | None = None,
) -> tuple[dict[str, AnimationClip], dict[str, object]]:
    """Carga y valida un archivo de animación en formato gf-anim-v1.

    Devuelve un diccionario de clips indexados por nombre y el diccionario de metadatos.
    """
    path = Path(manifest_path).resolve()
    if not path.is_file():
        raise AnimationFormatError(f"El manifiesto de animación no existe: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise AnimationFormatError(f"JSON inválido en {path}: {err}") from err

    # Validaciones fundamentales de esquema gf-anim-v1
    version = data.get("version")
    if version not in ("gf-anim-v1", "gf-anim-v1.0.0"):
        raise AnimationFormatError(f"Versión de esquema no soportada: {version}")

    metadata = data.get("metadata", {})
    texture_info = data.get("texture", {})
    raw_frames = data.get("frames", [])
    raw_clips = data.get("clips", {})

    if not isinstance(raw_frames, list) or not raw_frames:
        raise AnimationFormatError("El campo 'frames' debe ser una lista no vacía")
    if not isinstance(raw_clips, dict) or not raw_clips:
        raise AnimationFormatError("El campo 'clips' debe ser un diccionario no vacío")

    # Carga del atlas de textura
    image_rel_path = texture_info.get("image_path")
    if not image_rel_path:
        raise AnimationFormatError("Falta 'image_path' en la sección 'texture'")

    source_dir = base_dir if base_dir else path.parent
    atlas_file = (source_dir / image_rel_path).resolve()

    atlas_surface: pygame.Surface
    if atlas_file.is_file():
        try:
            raw_surf = pygame.image.load(str(atlas_file))
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                atlas_surface = raw_surf.convert_alpha()
            else:
                atlas_surface = raw_surf
        except pygame.error as err:
            raise AnimationFormatError(f"No se pudo cargar la imagen del atlas {atlas_file}: {err}") from err
    else:
        # Modo headless o fallback si la textura no existe físicamente: crear superficie mock
        atlas_w = int(texture_info.get("width", 256))
        atlas_h = int(texture_info.get("height", 256))
        atlas_surface = pygame.Surface((atlas_w, atlas_h), pygame.SRCALPHA)

    atlas_rect = atlas_surface.get_rect()

    # Procesar fotogramas
    parsed_frames: dict[str, FrameData] = {}
    for frame_entry in raw_frames:
        frame_id = frame_entry.get("id")
        if not frame_id or not isinstance(frame_id, str):
            raise AnimationFormatError(f"Entrada de fotograma con ID inválido: {frame_entry}")

        rect_coords = frame_entry.get("rect")
        if not rect_coords or len(rect_coords) != 4:
            raise AnimationFormatError(f"El fotograma '{frame_id}' no define un 'rect' [x, y, w, h] válido")

        x, y, w, h = (int(c) for c in rect_coords)
        if w <= 0 or h <= 0:
            raise AnimationFormatError(f"El fotograma '{frame_id}' tiene dimensiones inválidas: w={w}, h={h}")

        sub_rect = pygame.Rect(x, y, w, h)
        if not atlas_rect.contains(sub_rect):
            raise AnimationFormatError(
                f"El fotograma '{frame_id}' ({sub_rect}) excede los límites del atlas ({atlas_rect})"
            )

        # Extraer superficie compartida (subsurface)
        frame_surface = atlas_surface.subsurface(sub_rect)

        pivot_coords = frame_entry.get("pivot", [w // 2, h])
        pivot = (int(pivot_coords[0]), int(pivot_coords[1]))

        duration_ms = int(frame_entry.get("duration_ms", 100))
        duration_s = max(0.01, duration_ms / 1000.0)

        # Sockets
        raw_sockets = frame_entry.get("sockets", {})
        sockets: dict[str, tuple[int, int]] = {}
        for s_name, s_coords in raw_sockets.items():
            if len(s_coords) == 2:
                sockets[s_name] = (int(s_coords[0]), int(s_coords[1]))

        # Hurtboxes
        raw_hurtboxes = frame_entry.get("hurtboxes", [])
        hurtboxes = tuple(tuple(int(c) for c in hb[:4]) for hb in raw_hurtboxes if len(hb) >= 4)

        # Hitboxes
        raw_hitboxes = frame_entry.get("hitboxes", [])
        hitbox_list: list[HitboxData] = []
        for hb_entry in raw_hitboxes:
            hb_rect = hb_entry.get("rect")
            if hb_rect and len(hb_rect) == 4:
                hitbox_list.append(
                    HitboxData(
                        rect=(int(hb_rect[0]), int(hb_rect[1]), int(hb_rect[2]), int(hb_rect[3])),
                        damage=float(hb_entry.get("damage", 10.0)),
                        knockback_force=float(hb_entry.get("knockback_force", 100.0)),
                        hitstun_duration_s=float(hb_entry.get("hitstun_duration_s", 0.2)),
                        hit_sound=str(hb_entry.get("hit_sound", "")),
                    )
                )

        # Eventos
        raw_events = frame_entry.get("events", [])
        event_list: list[FrameEvent] = []
        for ev in raw_events:
            ev_name = ev.get("name")
            if ev_name:
                event_list.append(FrameEvent(name=str(ev_name), payload=ev.get("payload", {})))

        parsed_frames[frame_id] = FrameData(
            id=frame_id,
            rect=(x, y, w, h),
            pivot=pivot,
            duration=duration_s,
            surface=frame_surface,
            sockets=sockets,
            hurtboxes=hurtboxes,
            hitboxes=tuple(hitbox_list),
            events=tuple(event_list),
        )

    # Procesar clips
    parsed_clips: dict[str, AnimationClip] = {}
    for clip_name, clip_entry in raw_clips.items():
        frame_ids = clip_entry.get("frames", [])
        if not frame_ids:
            raise AnimationFormatError(f"El clip '{clip_name}' no define ningún fotograma")

        clip_frames: list[FrameData] = []
        for fid in frame_ids:
            if fid not in parsed_frames:
                raise AnimationFormatError(
                    f"El clip '{clip_name}' referencia un fotograma inexistente: '{fid}'"
                )
            clip_frames.append(parsed_frames[fid])

        loop = bool(clip_entry.get("loop", True))
        playback_speed = float(clip_entry.get("playback_speed", 1.0))
        priority = int(clip_entry.get("interrupt_priority", 0))

        parsed_clips[clip_name] = AnimationClip(
            name=clip_name,
            frames=tuple(clip_frames),
            loop=loop,
            playback_speed=playback_speed,
            interrupt_priority=priority,
        )

    return parsed_clips, metadata
