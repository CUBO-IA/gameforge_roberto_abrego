"""Telemetría de ejecución de escenarios: tiempos, FPS y memoria."""

from __future__ import annotations

import math
import tracemalloc
from dataclasses import dataclass, field


def percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        return 0.0
    index = max(0, min(len(sorted_values) - 1, math.ceil(fraction * len(sorted_values)) - 1))
    return sorted_values[index]


@dataclass(slots=True)
class Telemetry:
    """Acumula muestras de tiempo por frame y memoria trazada."""

    samples_ms: list[float] = field(default_factory=list)
    started_tracemalloc: bool = False

    def start_memory_tracking(self) -> None:
        if not self.started_tracemalloc:
            tracemalloc.start()
            self.started_tracemalloc = True

    def stop_memory_tracking(self) -> float:
        if not self.started_tracemalloc:
            return 0.0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.started_tracemalloc = False
        return peak / 1024.0

    def add_frame(self, milliseconds: float) -> None:
        self.samples_ms.append(milliseconds)

    def summary(self, wall_ms: float, peak_kb: float = 0.0) -> dict[str, object]:
        if not self.samples_ms:
            return {
                "frames": 0,
                "elapsed_wall_ms": round(wall_ms, 3),
                "fps_equivalent": 0.0,
                "peak_memory_kb": round(peak_kb, 3),
                "frame_ms": {"p50": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0},
            }
        ordered = sorted(self.samples_ms)
        total = sum(ordered)
        fps = (len(ordered) / total * 1000.0) if total > 0 else 0.0
        return {
            "frames": len(ordered),
            "elapsed_wall_ms": round(wall_ms, 3),
            "fps_equivalent": round(fps, 1),
            "peak_memory_kb": round(peak_kb, 3),
            "frame_ms": {
                "p50": round(percentile(ordered, 0.50), 4),
                "p95": round(percentile(ordered, 0.95), 4),
                "p99": round(percentile(ordered, 0.99), 4),
                "max": round(ordered[-1], 4),
            },
        }
