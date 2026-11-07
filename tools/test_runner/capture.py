"""Captura determinista de frames y comparación visual sin dependencias.

La comparación usa dos niveles nativos de Pygame CE: igualdad de buffers y,
solo si difieren, una resta ``BLEND_SUB`` para producir la máscara de
diagnóstico. El ratio de píxeles distintos se calcula con ``array`` de la
librería estándar para no añadir numpy al proyecto.
"""

from __future__ import annotations

import array
from dataclasses import dataclass
from pathlib import Path

import pygame


@dataclass(frozen=True, slots=True)
class DiffResult:
    passed: bool
    ratio: float
    mask: pygame.Surface | None = None
    baseline_missing: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "pixel_diff_ratio": round(self.ratio, 8),
            "baseline_missing": self.baseline_missing,
        }


def capture_frame(surface: pygame.Surface) -> pygame.Surface:
    """Copia el frame actual a memoria (no escribe en disco)."""
    return surface.copy()


def save_png(surface: pygame.Surface, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(destination))
    return destination


def buffers_equal(first: pygame.Surface, second: pygame.Surface) -> bool:
    if first.get_size() != second.get_size():
        return False
    return first.get_buffer().raw == second.get_buffer().raw


def pixel_diff_ratio(first: pygame.Surface, second: pygame.Surface) -> float:
    """Proporción de píxeles distintos entre dos superficies del mismo tamaño."""
    if first.get_size() != second.get_size():
        return 1.0
    first_raw = first.get_buffer().raw
    second_raw = second.get_buffer().raw
    if first_raw == second_raw:
        return 0.0

    first_pixels = array.array("I")
    second_pixels = array.array("I")
    if first_pixels.itemsize != 4 or len(first_raw) % 4 != 0:
        return 1.0
    first_pixels.frombytes(first_raw)
    second_pixels.frombytes(second_raw)
    if len(first_pixels) != len(second_pixels) or not first_pixels:
        return 1.0
    differing = sum(
        1 for left, right in zip(first_pixels, second_pixels, strict=False) if left != right
    )
    return differing / len(first_pixels)


def make_diff_mask(actual: pygame.Surface, golden: pygame.Surface) -> pygame.Surface:
    """Máscara de diagnóstico: resta el golden del frame actual."""
    mask = pygame.Surface(actual.get_size(), pygame.SRCALPHA)
    mask.blit(actual, (0, 0))
    mask.blit(golden, (0, 0), special_flags=pygame.BLEND_SUB)
    return mask


def compare(
    actual: pygame.Surface,
    golden: pygame.Surface,
    tolerance_ratio: float = 0.0005,
) -> DiffResult:
    if buffers_equal(actual, golden):
        return DiffResult(passed=True, ratio=0.0)
    ratio = pixel_diff_ratio(actual, golden)
    passed = ratio <= tolerance_ratio
    mask = None if passed else make_diff_mask(actual, golden)
    return DiffResult(passed=passed, ratio=ratio, mask=mask)
