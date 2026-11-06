"""SFX sintetizados en memoria.

No se distribuyen assets de audio ni se descargan recursos: los sonidos se
generan con ondas simples al iniciar. Si el dispositivo de audio no está
disponible, el juego continúa en silencio y deja constancia en el log.
"""

from __future__ import annotations

import logging
import math
import random
from array import array

import pygame

logger = logging.getLogger(__name__)


class Audio:
    def __init__(self, master_volume: float = 0.55) -> None:
        self.master_volume = max(0.0, min(1.0, master_volume))
        self.enabled = False
        self.error: str | None = None
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self.sample_rate = 44100
        self.channels = 1
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            init = pygame.mixer.get_init()
            if init is None:
                raise pygame.error("mixer no inicializado")
            self.sample_rate, _, self.channels = init
            self.enabled = True
            self._build_sounds()
        except pygame.error as exc:
            self.error = str(exc)
            self.enabled = False
            logger.warning("Audio deshabilitado: %s", exc)

    def _build_sounds(self) -> None:
        self._sounds = {
            "hit": self._synthesize([(170, 0.05, "noise", 0.55), (90, 0.07, "sine", 0.35)]),
            "shoot": self._synthesize([(520, 0.13, "sine", 0.35, 170)]),
            "pickup": self._synthesize([(660, 0.07, "sine", 0.3), (990, 0.09, "sine", 0.3)]),
            "heal": self._synthesize([(480, 0.16, "sine", 0.3, 760)]),
            "dash": self._synthesize([(300, 0.1, "noise", 0.28), (900, 0.07, "sine", 0.18)]),
            "interact": self._synthesize([(440, 0.07, "sine", 0.3), (660, 0.08, "sine", 0.25)]),
            "denied": self._synthesize([(150, 0.16, "square", 0.22)]),
            "ui": self._synthesize([(760, 0.045, "sine", 0.25)]),
            "death": self._synthesize([(300, 0.6, "sine", 0.35, 80)]),
            "victory": self._synthesize(
                [
                    (523, 0.12, "sine", 0.3),
                    (659, 0.12, "sine", 0.3),
                    (784, 0.14, "sine", 0.3),
                    (1047, 0.36, "sine", 0.32),
                ]
            ),
        }

    def _synthesize(
        self,
        segments: list[tuple],
    ) -> pygame.mixer.Sound:
        samples: list[float] = []
        generator = random.Random(0xBEEF)
        for segment in segments:
            frequency = float(segment[0])
            duration = float(segment[1])
            waveform = str(segment[2])
            amplitude = float(segment[3])
            end_frequency = float(segment[4]) if len(segment) > 4 else frequency
            count = max(1, int(duration * self.sample_rate))
            phase = 0.0
            for index in range(count):
                t = index / count
                current = frequency + (end_frequency - frequency) * t
                phase += math.tau * current / self.sample_rate
                if waveform == "noise":
                    value = generator.uniform(-1.0, 1.0)
                elif waveform == "square":
                    value = 1.0 if math.sin(phase) >= 0 else -1.0
                else:
                    value = math.sin(phase)
                envelope = min(1.0, t / 0.06) * (1.0 - t) ** 1.5
                samples.append(value * envelope * amplitude)
        return self._to_sound(samples)

    def _to_sound(self, samples: list[float]) -> pygame.mixer.Sound:
        data = array("h")
        for sample in samples:
            value = int(max(-1.0, min(1.0, sample)) * 32767 * self.master_volume)
            for _ in range(self.channels):
                data.append(value)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        sound = self._sounds.get(name)
        if sound is None:
            return
        try:
            sound.play()
        except pygame.error as exc:
            logger.warning("No se pudo reproducir '%s': %s", name, exc)

    def shutdown(self) -> None:
        self._sounds.clear()
