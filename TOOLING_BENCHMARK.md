# TOOLING_BENCHMARK.md — GAMEFORGE 2D
## Benchmark Empírico de Rendimiento, Consumo de Recursos y Eficiencia de Herramientas

**Estado:** REPORTE DE MEDICIONES REPRODUCIBLES  
**Misión:** MISIÓN 006 — Investigación e Integración de Herramientas para Desarrollo 2D  
**Fecha de medición:** 2026-11-07  
**Proyecto:** GameForge 2D (RPG Modular en Python / Pygame CE)  

---

## 1. Entorno Real de Medición

Todas las cifras de este documento fueron obtenidas en esta máquina, invocando el intérprete del
entorno virtual del proyecto (`.venv/Scripts/python.exe`). No se trasladan cifras de otras fuentes.

| Componente | Versión verificada |
|:---|:---|
| Sistema operativo | Windows (x64) |
| Python | 3.14.5 |
| pygame-ce | 2.5.8 (SDL 2.32.10) |
| pytest | 9.1.1 |
| ruff | 0.17.4 |
| pyright | 1.1.414 (vía `npx`) |
| uv | 0.11.26 |
| FFmpeg | 8.1.1-full_build (gyan.dev) |
| Driver de video en pruebas | `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy` |
| Cronómetro | `time.perf_counter()` / `time.perf_counter_ns()` |
| Memoria | `tracemalloc` |

> **Nota de interpretación:** las cifras son de una sola máquina y de una sola sesión. Sirven para
> comparar órdenes de magnitud entre alternativas, no como garantía de rendimiento absoluto.

---

## 2. Calidad y Análisis Estático

### 2.1. Ruff (check)

Se ejecutó `.venv/Scripts/ruff.exe check . --output-format=json` tres veces, midiendo el proceso
completo (arranque incluido):

| Ejecución | Tiempo de pared | Código de salida | Tamaño JSON |
|:---|:---:|:---:|:---:|
| 1 | 96 ms | 1 | 618 bytes |
| 2 | 79 ms | 1 | 618 bytes |
| 3 | 84 ms | 1 | 618 bytes |

- **Mediana:** ~84 ms para todo el repositorio (código, tests y herramientas).
- **Violaciones detectadas en la primera pasada:** 1 (`B904` en `tests/test_mission_006_deliverables.py`).
  Se corrigió la causa (`raise ... from err`); la verificación posterior queda en 0 violaciones.
- **Conclusión:** la latencia es compatible con ejecutar Ruff tras cada edición sin penalización
  perceptible. La afirmación anterior de 55 ms no se reprodujo y se sustituye por esta medición.

### 2.2. Pyright

`npx --yes pyright --outputjson` sobre el repositorio completo:

| Métrica | Valor medido |
|:---|:---:|
| Archivos analizados | 139 |
| Tiempo de análisis reportado por Pyright | 3.54 s |
| Tiempo de pared (incluye arranque de `npx`) | 5.74 s |
| Errores | **112** |
| Warnings | 0 |

- **Hallazgo relevante:** el repositorio **no está tipado en limpio**. Los 112 errores son deuda
  previa, no una incompatibilidad de Pyright con Python 3.14 ni con Pygame CE.
- **Consecuencia para el plan:** la Fase 1 no puede exigir "0 errores" de inmediato; debe fijar una
  línea base, reduciremos por módulo (`game/core`, `game/world`, `game/entities`) y bloquear el
  aumento de errores mientras se corrige.
- **Coste offline:** la primera invocación de `npx --yes` descarga el paquete. Para uso sin red debe
  instalarse localmente (`npm i -D pyright` o el paquete `pyright` de PyPI).

### 2.3. Flake8 (referencia)

**No medido.** No está instalado en el entorno y no se instalará para esta misión. La comparación
"Ruff es 51 veces más rápido que Flake8" que aparecía en una versión anterior de este documento no
tenía medición local y se retira.

---

## 3. Suite de Pruebas (pytest)

Ejecución con el intérprete del proyecto:

```bash
.venv/Scripts/python.exe -m pytest -q
# 314 passed in 6.06s
```

| Métrica | Valor medido |
|:---|:---:|
| Tests recolectados y aprobados | **314** |
| Tiempo total | **6.06 s** |
| Tiempo medio por test | ~19.3 ms |
| Fallos / errores | 0 / 0 |

### 3.1. Limitación importante: intérprete equivocado

Al invocar el Python del sistema (`python -m pytest`) en lugar del `.venv`, la suite falla con
**11 errores de colección** (`ModuleNotFoundError: No module named 'pygame'`). No es un fallo del
código, pero sí una trampa real para agentes: **todo comando debe ejecutarse con el intérprete del
entorno virtual del proyecto**. Esta comprobación se incorpora al catálogo de agentes como
precondición.

---

## 4. Renderizado Headless (Pygame CE, driver dummy)

Bucle de 5.000 frames sobre una superficie de 640x360: `fill`, un `draw.rect`, `event.get()` y
`display.flip()` por frame.

| Parámetro | Valor medido |
|:---|:---:|
| Frames ejecutados | 5.000 |
| Tiempo total | **0.207 s** |
| Throughput | **~24.127 FPS** |
| Latencia por frame | **0.0414 ms** |
| Memoria adicional pico (`tracemalloc`, 600 frames) | **0.2 KB** |

- **Implicación:** un escenario de 300 frames (5 s de juego) cuesta del orden de **12 ms** de pared.
  Es viable ejecutar decenas de escenarios por suite sin afectar el ciclo de desarrollo.
- **Salvedad:** el escenario medido dibuja primitivas, no el juego completo con entidades, IA y
  audio. La cifra anterior de 11.499 FPS era más conservadora; el valor real depende de la carga.

---

## 5. Comparación Visual (diff de frames 640x360)

Métodos medidos sobre dos superficies idénticas del tamaño de un frame completo (230.400 píxeles):

| Método | Tiempo por operación | Observación |
|:---|:---:|:---|
| Comparación de bytes crudos (`surface.get_buffer().raw == ...`) | **0.503 ms** | Incluye la copia del buffer en cada acceso; no es gratis |
| Resta de superficies (`BLEND_SUB`) | **0.322 ms** | Genera máscara diagnóstica reutilizable |
| MD5 del buffer | **0.991 ms** | Más lento que la comparación directa y sin ventaja práctica |
| Pixelmatch | **No medido** | Requiere Node; no se instaló |

### 5.1. Decisión basada en la medición

La comprobación de bytes crudos **no es un atajo de 0.008 ms**: cuesta ~0.5 ms porque `raw` copia
921.600 bytes. Aun así, el coste total del pipeline de diff (bytes + `BLEND_SUB` si difieren) queda
en **~0.8 ms por frame comparado**, muy por debajo del presupuesto de 16.67 ms.

Se adopta por tanto:

1. **Fast path:** igualdad de buffers (0.50 ms) para el caso "sin cambios".
2. **Diagnóstico:** `BLEND_SUB` (0.32 ms) solo cuando hay diferencias, para producir la máscara.

No se incorpora ninguna librería externa de diff de imágenes. La comparación perceptual (dHash)
queda como trabajo futuro del Game Test Runner, no como dependencia.

---

## 6. Procesamiento de Imágenes: Pillow vs Pygame CE

Operación medida: crear una imagen RGBA de 256x256 y escalarla a 512x512 con vecino más próximo,
100 iteraciones. Pillow se ejecutó en entorno efímero (`uv run --with pillow`, Pillow 13.0.0) porque
**no forma parte del entorno del proyecto**:

| Implementación | Tiempo por iteración |
|:---|:---:|
| Pillow (`Image.new` + `resize(NEAREST)`) | **0.346 ms** |
| Pygame CE (`Surface` + `transform.scale`) | **0.398 ms** |

- **Corrección:** la afirmación previa de que Pillow era 8.4 veces más lento no se reproduce. El
  rendimiento es comparable.
- **Criterio de elección:** Pillow se justifica por **capacidades** (I/O de formatos, paletas,
  recorte por canal alfa, metadatos), no por velocidad. Pygame CE sigue siendo la opción dentro del
  bucle de juego.

---

## 7. Procesamiento de Audio con FFmpeg CLI

Síntesis de una onda senoidal de 440 Hz de 1 segundo y codificación directa a OGG Vorbis
(`libvorbis -q:a 4`):

| Métrica | Valor medido |
|:---|:---:|
| Tiempo de pared (proceso completo) | **58.6 ms** |
| Código de salida | 0 |
| Tamaño resultante | **5.2 KB** |

La cifra anterior (165 ms, 9.4 KB) no se reprodujo. El orden de magnitud se mantiene: decenas de
milisegundos por clip, adecuado para procesamiento por lotes.

---

## 8. Proyección en Hardware de Gama Baja (no medido)

Esta sección es una **proyección**, no una medición: no se dispone de un equipo con iGPU en esta
sesión.

| Parámetro | Presupuesto | Observación |
|:---|:---:|:---|
| Frame a 60 FPS | 16.67 ms | Presupuesto objetivo |
| Simulación + dibujado del juego | ~3.6 ms (p95 histórico del repo) | Dato del benchmark de simulación del proyecto, no de este informe |
| RAM del juego en ejecución | ~35 MB (estimación) | Debe confirmarse con `tracemalloc` en una sesión con ventana real |
| Suite `verify.py` | < 30 s | Medido parcialmente: pytest 6.06 s + Ruff 0.1 s |

---

## 9. Eficiencia de Tokens (estimación, no medición)

No se midió con un tokenizador real. Las cifras de la versión anterior de este documento eran
estimaciones presentadas como mediciones y se retiran. La regla operativa que sí se mantiene:

- Preferir `--output-format=json`, `-q`, `--tb=short` y `--statistics`.
- Ruff produce ~618 bytes de JSON cuando hay una sola violación: coste de contexto despreciable.
- Pyright produce un JSON grande (112 errores): debe filtrarse con `jq`/Python antes de volcarlo al
  contexto del agente.

---

## 10. Limitaciones de estas Mediciones

1. **Una sola máquina y una sola sesión.** Sin repetición estadística suficiente para percentiles.
2. **Windows únicamente.** No se midió Linux ni macOS.
3. **Sin GPU real.** Todo el render se midió con `SDL_VIDEODRIVER=dummy`; no refleja presentación
   con VSync ni composición de ventana.
4. **Sin audio real.** `SDL_AUDIODRIVER=dummy`; no se midió latencia de reproducción.
5. **Pyright no está limpio** (112 errores): su coste puede variar al corregir la base.
6. **Pillow no está instalado en el proyecto**: se midió en entorno efímero.
7. **Pixelmatch, Flake8, pymunk, py_trees, pygame_gui y pyfxr no se midieron.**
8. **No se probó el Game Test Runner**: aún no existe; este informe mide solo sus primitivas.

---

## 11. Reproducción

```bash
# Suite completa (usar el intérprete del proyecto)
.venv/Scripts/python.exe -m pytest -q

# Lint con tiempo de pared
time .venv/Scripts/ruff.exe check . --output-format=json

# Tipado (primera ejecución requiere red para npx)
npx --yes pyright --outputjson

# Primitivas de render headless y diff: ver scripts citados en GAME_TEST_RUNNER_DESIGN.md
```

---

## 12. Resumen de Cifras Verificadas

| Métrica | Valor |
|:---|:---:|
| Tests aprobados | 314 en 6.06 s |
| Ruff (repo completo) | 79–96 ms |
| Pyright (139 archivos) | 3.54 s de análisis, 112 errores base |
| Render headless | ~24.000 FPS (0.041 ms/frame) |
| Diff por buffer | 0.503 ms |
| Diff por `BLEND_SUB` | 0.322 ms |
| Pillow vs Pygame (escalado 2x) | 0.346 ms vs 0.398 ms |
| FFmpeg síntesis + OGG 1 s | 58.6 ms, 5.2 KB |
