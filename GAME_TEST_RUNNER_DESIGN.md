# GAME_TEST_RUNNER_DESIGN.md — GAMEFORGE 2D
## Diseño del Sistema Propio de Pruebas Automatizadas de Videojuegos (GF-TR)

**Estado:** ESPECIFICACIÓN ARQUITECTÓNICA Y DE DISEÑO  
**Misión:** MISIÓN 006 — Investigación e Integración de Herramientas para Desarrollo 2D  
**Fecha:** 2026-11-07  
**Autor:** Director de Tecnología / Agente de Arquitectura e Integración  
**Proyecto:** GameForge 2D (RPG Modular en Python / Pygame CE)  

---

## 1. Visión y Objetivos Arquitectónicos

El **GameForge Test Runner (GF-TR)** es un sistema de pruebas automatizadas end-to-end diseñado específicamente para videojuegos 2D desarrollados en Python y Pygame CE.

### Justificación de una Solución Propia:
Las herramientas genéricas existentes en la industria presentan incompatibilidades insalvables con la arquitectura de GameForge:
- **Airtest / Poco:** Requieren frameworks pesados de visión por computadora (OpenCV), emuladores móviles y entornos con ventana física activa.
- **Selenium / Playwright:** Orientados exclusivamente a tecnologías web (DOM/HTML5 Canvas).
- **PyAutoGUI:** Depende del control del ratón y teclado a nivel del sistema operativo en ventanas reales, siendo inviable en servidores CI/CD sin monitor.

GF-TR resuelve esto desacoplando completamente el arnés de pruebas del núcleo del motor, operando a nivel de simulación pura en memoria sobre el controlador de video ficticio (`SDL_VIDEODRIVER=dummy`), con una velocidad medida de **~24.000 FPS** en el bucle de primitivas (5.000 frames en 0.207 s; ver `TOOLING_BENCHMARK.md`).

```
┌────────────────────────────────────────────────────────────────────────┐
│               ARQUITECTURA MODULAR DE GAMEFORGE TEST RUNNER (GF-TR)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│     HeadlessRunner    │ │ VirtualInputController│ │     ScenarioEngine    │
│  (Ciclo de Vida/Ticks)│ │  (Inyección Eventos)  │ │ (Carga de JSON / DSL) │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
            │                               │                               │
            └───────────────────────┬───────┴───────────────────────────────┘
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      NÚCLEO DEL JUEGO (GameForge App)                     │
│               Application -> Scene -> World -> Sim -> Entities           │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│     StateInspector    │ │  FrameCaptureEngine   │ │   TelemetryCollector  │
│(Aserciones Colisiones)│ │ (Snapshots Memoria)   │ │  (p95, FPS, Memoria)  │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
            │                               │                               │
            │                               ▼                               │
            │                   ┌───────────────────────┐                   │
            │                   │   VisualDiffEngine    │                   │
            │                   │(Perceptual / BLEND_SUB│                   │
            │                   └───────────┬───────────┘                   │
            │                               │                               │
            └───────────────────────┬───────┴───────────────────────────────┘
                                    ▼
                        ┌───────────────────────┐
                        │   RegressionReporter  │
                        │ (JSON / HTML / JUnit) │
                        └───────────────────────┘
```

---

## 2. Componentes Modulares del Sistema

### 2.1. `HeadlessRunner` (Gestor del Ciclo de Vida)
- **Función:** Inicializa y destruye de forma segura la instancia de `Application` de GameForge.
- **Aislamiento:** Fuerza las variables de entorno `SDL_VIDEODRIVER=dummy` y `SDL_AUDIODRIVER=dummy` antes de cargar Pygame.
- **Determinismo Temporal:** Ejecuta el bucle de juego frame a frame mediante pasos de tiempo fijos ($\Delta t = 1/60\text{ s} = 16.666\text{ ms}$), eliminando cualquier fluctuación de tiempo real del reloj del sistema operativo.
- **Cierre Seguro:** Implementa el protocolo de cierre `app.shutdown()` y `pygame.quit()`, limpiando handlers y liberando buffers de memoria en un bloque `try...finally`.

### 2.2. `VirtualInputController` (Inyección Determinista de Eventos)
- **Función:** Sintetiza y publica eventos en la cola oficial de Pygame (`pygame.event.post()`) en números de fotograma exactos.
- **Capacidades de Entrada:**
  - Simulación de teclado: `press_key(key, duration_frames)`, `release_key(key)`.
  - Simulación de ratón: `move_mouse_to(x, y)`, `click_mouse(button)`.
  - Despacho de acciones de alto nivel: `move_direction(Vec2(x, y))`, `trigger_action("attack")`, `trigger_action("interact")`.
- **Determinismo:** Los eventos se despachan antes de que `app.update(dt)` invoque a `app.input.update()`, garantizando que cada frame procese exactamente la entrada programada.

### 2.3. `ScenarioEngine` (Motor de Escenarios de Prueba)
- **Función:** Carga definiciones declarativas de pruebas desde archivos JSON o scripts Python con una sintaxis concisa y legible.
- **Estructura del Escenario:**
  - `metadata`: Identificador, descripción, semilla procedural (`seed`) y duración máxima en frames.
  - `initial_state`: Posición de spawn forzada, inventario inicial, configuración de sala.
  - `timeline`: Lista de comandos temporizados por fotograma (inyecciones de entrada).
  - `expected_conditions`: Aserciones de estado requeridas al finalizar o en pasos intermedios.

### 2.4. `StateInspector` (Aserciones de Estados y Colisiones)
- **Función:** Inspecciona directamente las estructuras del modelo de juego sin depender de la capa gráfica.
- **Aserciones Disponibles:**
  - `assert_player_position(expected_pos, tolerance=2.0)`: Verifica coordenadas en espacio 2D.
  - `assert_entity_alive(entity_id)` / `assert_entity_dead(entity_id)`.
  - `assert_no_collision_with_walls(entity)`: Consulta el árbol espacial (`SpatialHash`) para certificar que el radio de colisión de la entidad no penetra ningún tile sólido.
  - `assert_inventory_contains(item_id, min_quantity)`.
  - `assert_quest_state(quest_id, expected_status)`.

### 2.5. `FrameCaptureEngine` (Captura Determinista)
- **Función:** Extrae capturas de pantalla de la superficie de renderizado `app.screen` en memoria RAM sin guardar obligatoriamente a disco salvo que sea necesario.
- **Modos de Captura:**
  - `SNAPSHOT_ON_STEP`: Captura al completar una fase del escenario.
  - `SNAPSHOT_ON_FAIL`: Captura de emergencia cuando una aserción lógica o colisión falla.
  - `SNAPSHOT_FINAL`: Captura al concluir el escenario completo.

### 2.6. `VisualDiffEngine` (Comparador Visual Perceptual)
- **Función:** Compara la captura del frame actual contra la imagen de referencia (*golden master*) prealmacenada en `tests/visual_baselines/`.
- **Estrategia de Comparación en Tres Capas (Three-Tier Diff):**
  1. **Nivel 1 — Coincidencia de Bytes Crudos (Fast Path):** Compara `s1.get_buffer().raw == s2.get_buffer().raw` en **0.503 ms** (medido; el coste lo domina la copia de 921.600 bytes de cada buffer). Si es idéntico, la prueba pasa con 0% de diferencia sin más cómputo.
  2. **Nivel 2 — Hash Perceptual (dHash / pHash):** Si los bytes difieren levemente, calcula una huella hash de 64 bits para discriminar pequeñas variaciones de redondeo en rasterizado de texto.
  3. **Nivel 3 — Resta Aritmética de Superficies (`BLEND_SUB`):** Si la diferencia supera el umbral de tolerancia, Pygame CE resta ambas superficies en **0.322 ms** (medido), generando una máscara de error donde los píxeles divergentes se tiñen de color magenta brillante (`#FF00FF`) para diagnóstico del agente.

```python
# Algoritmo de Generación de Diff Visual en Memoria (Pygame CE Nativo)
def generate_visual_diff(actual_surf: pygame.Surface, golden_surf: pygame.Surface, tolerance_ratio=0.001) -> tuple[bool, float, pygame.Surface | None]:
    # 1. Comprobación de bytes crudos
    if actual_surf.get_buffer().raw == golden_surf.get_buffer().raw:
        return True, 0.0, None

    w, h = actual_surf.get_size()
    total_pixels = w * h

    # 2. Resta de superficies mediante BLEND_SUB nativo
    diff_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    diff_surf.blit(actual_surf, (0, 0))
    diff_surf.blit(golden_surf, (0, 0), special_flags=pygame.BLEND_SUB)

    # 3. Conteo de píxeles diferentes
    # En Pygame CE, surfarray o un barrido rápido determina el ratio de cambio
    pixels_diff = count_nonzero_pixels(diff_surf)
    ratio = pixels_diff / total_pixels

    if ratio <= tolerance_ratio:
        return True, ratio, None

    # 4. Generar máscara de diagnóstico coloreada en magenta
    mask_surf = create_highlight_mask(actual_surf, diff_surf)
    return False, ratio, mask_surf
```

### 2.7. `TelemetryCollector` (Métricas de Rendimiento y Profiling)
- **Función:** Mide con precisión de nanosegundos el rendimiento de cada frame ejecutado durante el escenario.
- **Métricas Registradas:**
  - Percentiles de latencia de frame: $p50$, $p95$, $p99$ y tiempo máximo.
  - FPS equivalentes sostenidos en headless.
  - Memoria asignada pico y delta mediante `tracemalloc`.
  - Recolección de basura: Ciclos del Garbage Collector ejecutados durante la prueba.

### 2.8. `RegressionReporter` (Informes y Volcado de Excepciones)
- **Función:** Genera informes legibles para humanos y resúmenes estructurados en JSON consumibles directamente por Claude Code y otros agentes.
- **Gestión de Crashes (*Crash Dumps*):**
  Si el juego lanza una excepción no controlada (`ZeroDivisionError`, `KeyError`, etc.), GF-TR captura:
  1. El stack trace completo con valores de variables locales.
  2. El número de frame exacto en el que ocurrió el colapso.
  3. Los últimos 10 eventos de entrada inyectados.
  4. Una captura de pantalla PNG del estado visual del juego justo antes de caer.

---

## 3. Especificación Declarativa de Escenarios de Prueba

A continuación se define el esquema canónico de un escenario de prueba en formato JSON (`tests/scenarios/player_combat_and_loot.json`):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "id": "scenario_combat_and_loot_001",
  "description": "Prueba de movimiento, ataque a un esqueleto, recepción de daño y apertura de cofre",
  "config": {
    "seed": 1042,
    "map": "hub_town",
    "timeout_frames": 300,
    "headless": true
  },
  "initial_state": {
    "player_spawn": { "x": 100.0, "y": 150.0 },
    "player_hp": 100,
    "inventory": []
  },
  "input_timeline": [
    { "frame": 1, "action": "move", "vector": [1.0, 0.0] },
    { "frame": 40, "action": "move", "vector": [0.0, 0.0] },
    { "frame": 45, "action": "press", "key": "SPACE" },
    { "frame": 46, "action": "release", "key": "SPACE" },
    { "frame": 60, "action": "move", "vector": [0.0, 1.0] },
    { "frame": 90, "action": "move", "vector": [0.0, 0.0] },
    { "frame": 95, "action": "press", "key": "E" },
    { "frame": 96, "action": "release", "key": "E" }
  ],
  "assertions": [
    {
      "at_frame": 40,
      "type": "player_position",
      "expected": { "x": 180.0, "y": 150.0 },
      "tolerance": 5.0
    },
    {
      "at_frame": 55,
      "type": "enemy_state",
      "enemy_id": "skeleton_01",
      "status": "DEAD"
    },
    {
      "at_frame": 100,
      "type": "chest_state",
      "coords": [200.0, 210.0],
      "opened": true
    },
    {
      "at_frame": 100,
      "type": "inventory_item_present",
      "item_id": "iron_key",
      "min_count": 1
    }
  ],
  "visual_validation": {
    "capture_at_frames": [45, 100],
    "max_allowed_pixel_diff_ratio": 0.0005,
    "golden_reference_dir": "tests/visual_baselines/combat_and_loot/"
  }
}
```

---

## 4. Integración Fluida con pytest

GF-TR se diseña para integrarse nativamente en la infraestructura de pruebas existente del proyecto sin romper los contratos actuales:

### 4.1. Fixture de pytest (`conftest.py`)
```python
import pytest
from tools.test_runner.runner import GameTestRunner

@pytest.fixture
def game_runner(tmp_path):
    """Fixture oficial para ejecutar escenarios headless de GameForge."""
    runner = GameTestRunner(workspace_data_dir=tmp_path)
    yield runner
    runner.teardown()
```

### 4.2. Uso en Tests Automatizados
```python
def test_combat_and_loot_scenario(game_runner):
    scenario_path = "tests/scenarios/player_combat_and_loot.json"
    result = game_runner.run_scenario(scenario_path)
    
    assert result.passed, f"Falló el escenario: {result.errors}"
    assert result.telemetry.p95_frame_time_ms < 5.0, "Degradación de rendimiento"
    assert result.visual_diff.ratio < 0.001, "Regresión visual detectada"
```

### 4.3. Parámetros de Línea de Comandos para pytest
- `pytest -m scenario`: Ejecuta exclusivamente la suite de escenarios de jugabilidad.
- `pytest --update-goldens`: Actualiza deliberadamente las capturas de referencia tras una modificación artística aprobada.
- `pytest --visual-report`: Genera un informe interactivo HTML con las capturas de pantalla y máscaras de diferencias.

---

## 5. Criterios de Aceptación del Runner

El GameForge Test Runner se considerará completamente verificado si:
1. Permite ejecutar 300 frames de simulación continua en menos de 100 ms en modo headless.
2. Es capaz de detectar intencionadamente un fallo de colisión (e.g. un jugador atravesando una pared).
3. Es capaz de detectar una regresión gráfica intencionada de 1 solo sprite alterado.
4. Genera reportes estructurados en formato JSON limpios para el contexto de Claude Code.
5. No introduce ninguna dependencia permanente externa en el runtime del juego.

---

## 6. Estado de Implementación (MVP entregado)

El MVP del GF-TR ya existe en `tools/test_runner/` y no añade dependencias al proyecto:

| Módulo | Responsabilidad |
|:---|:---|
| `runner.py` | `HeadlessRunner` (arranque, escena, `step(dt fijo)`) y `run_scenario`. |
| `input.py` | `VirtualInputController`: teclas, clics y vectores publicados en la cola de Pygame. |
| `scenario.py` | Esquema, carga y validación estricta de escenarios JSON. |
| `inspector.py` | 8 aserciones de estado (`player_position`, `player_z_above`, `no_wall_collision`, `enemy_dead`, `any_chest_opened`, `inventory_*`, `player_alive`). |
| `capture.py` | Captura en memoria, comparación por buffers y máscara `BLEND_SUB`. |
| `telemetry.py` | p50/p95/p99/máx por frame, FPS equivalente y pico de `tracemalloc`. |
| `cli.py` | `python -m tools.test_runner --scenario <path> --json`. |

**Escenarios piloto:** `tests/scenarios/jump_and_survive.json` y `tests/scenarios/chest_loot.json`.
**Integración:** `tools/verify.py` ejecuta todos los escenarios como paso bloqueante (omitible con
`--skip-scenarios`); la suite de pytest los cubre en `tests/test_game_test_runner.py`.

### Diferencias respecto al diseño completo (pendientes declarados)

- **No implementado:** hash perceptual (dHash/pHash), informe HTML, grabación de vídeo y escenarios
  multi-escena. El diff actual es igualdad de buffers + ratio exacto de píxeles + máscara.
- **Línea base visual opcional:** sin `--baseline-dir` no se compara contra golden masters; la captura
  se guarda solo si se pasa `--artifacts`.
- **Una escena por escenario:** el runner termina cuando la escena cambia (victoria/muerte), y las
  aserciones posteriores se reportan como no evaluadas.
- **Rutas relativas:** los assets se resuelven desde el directorio de trabajo; ejecutar desde la raíz
  del repositorio (`tools/verify.py` ya lo garantiza con `cwd=ROOT`).
