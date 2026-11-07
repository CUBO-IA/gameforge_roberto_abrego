# TOOLING_INTEGRATION_PLAN.md — GAMEFORGE 2D
## Plan de Incorporación por Etapas, Gestión de Dependencias y Mitigación de Riesgos

**Estado:** ESPECIFICACIÓN TÉCNICA Y ROADMAP NORMATIVO  
**Misión:** MISIÓN 006 — Investigación e Integración de Herramientas para Desarrollo 2D  
**Fecha:** 2026-11-07  
**Autor:** Director de Tecnología / Agente de Arquitectura e Integración  
**Proyecto:** GameForge 2D (RPG Modular en Python / Pygame CE)  

---

## 1. Visión y Filosofía de Incorporación Progresiva

Para evitar la desestabilización del motor GameForge 2D y cumplir con el mandato de no acumular dependencias innecesarias, la integración de herramientas se estructura en un **plan de adopción gradual en cinco (5) etapas secuenciales**.

Cada etapa define:
- Prerrequisitos técnicos bloqueantes.
- Herramientas a integrar y su modo de aislamiento.
- Criterios de promoción y validación comprobable.
- Estrategia de contingencia y marcha atrás (*rollback*).
- Definición formal de terminado (*Definition of Done - DoD*).

```
┌────────────────────────────────────────────────────────────────────────┐
│               ROADMAP DE INCORPORACIÓN POR FASES (GAMEFORGE 2D)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 0: INVESTIGACIÓN, AUDITORÍA Y BENCHMARKING (MISIÓN 006 ACTUAL)    │
│  - Sin cambios en motor ni dependencias de runtime. Entornos efímeros. │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 1: CALIDAD ESTÁTICA, TIPADO Y BLINDAJE DE CONTRATOS               │
│  - Incorporación formal de Pyright en dev tooling y pyproject.toml.    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 2: ARNÉS AUTOMATIZADO DE PRUEBAS (GAME TEST RUNNER - GF-TR)       │
│  - Implementación de GF-TR (headless runner, inyección, diff visual).  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 3: PIPELINE DE ASSETS, EMPAQUETADO Y MULTIMEDIA                   │
│  - Integración de Pillow en dev tooling; orquestación FFmpeg CLI.      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 4: TOOLING AVANZADO DE SIMULACIÓN Y AUDIO PROCEDURAL              │
│  - Pruebas PBT con Hypothesis en matemáticas; pyfxr en asset bake.    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Desglose de Fases de Incorporación

### Fase 0: Investigación, Auditoría y Aprobación (Misión 006 — Estado Actual)
- **Objetivo:** Analizar, medir y seleccionar el conjunto mínimo de herramientas sin modificar el motor ni añadir dependencias permanentes.
- **Acciones:**
  - Auditoría técnica completa de las 21+ herramientas candidatas (`TOOLING_AUDIT.md`).
  - Pruebas de compatibilidad empírica y benchmarking con `uv run --with` (`TOOLING_COMPATIBILITY.md` y `TOOLING_BENCHMARK.md`).
  - Diseño de la arquitectura de pruebas y catálogo de agentes (`GAME_TEST_RUNNER_DESIGN.md` y `AGENT_TOOL_CATALOG.md`).
- **DoD:** Todos los entregables creados, verificados mediante tests automáticos, y aprobación formal del Director.

---

### Fase 1: Calidad Estática, Tipado y Blindaje de Contratos
- **Prerrequisito:** Aprobación formal de los resultados de la Fase 0.
- **Herramientas a Incorporar:**
  - `pyright` (incorporado como herramienta de desarrollo mediante script o paquete opcional en `[project.optional-dependencies] dev`).
  - Configuración canónica de `pyrightconfig.json` o `[tool.pyright]` en `pyproject.toml`.
  - Consolidación de reglas de Ruff (`ruff.lint.select = ["E", "F", "I", "W", "UP", "B", "SIM", "PIE"]`).
- **Beneficio Técnico:** Detección en tiempo de guardado de incompatibilidades de tipo entre contratos compartidos (`CONTRACTS.md`) y el código del juego.
- **Riesgo:** Generación masiva de alertas de tipado falsas en código dinámico antiguo de Pygame.
  - *Mitigación:* Modo `strict` para `game.core`, `game.world` y `game.entities`; modo `basic` temporal para `game.scenes`.
- **Estado real (2026-11-07, tras T-1002):** `pyright` analiza 149 archivos con el venv del proyecto y reporta **46 errores** (antes 112). `game/core` y `game/world` están en **0**. La línea base vive en `pyright_baseline.json` y la puerta en `tools/typecheck.py`.
- **DoD:**
  - `tools/verify.py` ejecuta `tools/typecheck.py` y falla si el total supera la línea base o si `game/core`/`game/world` dejan de estar en 0.
  - `game/core` y `game/world` en 0 errores (cumplido); `game/render`, `game/app.py`, `game/ai` y tests conservan deuda documentada.
  - 100% de los tests unitarios continúan pasando en verde.
- **Nota offline:** `npx --yes pyright` descarga el paquete en la primera ejecución. Para entornos sin red, instalar `pyright` localmente en el grupo `dev`.

---

### Fase 2: Arnés Automatizado de Pruebas (Game Test Runner — GF-TR)
- **Estado:** MVP entregado en T-1001 (`tools/test_runner/`, 2 escenarios piloto, `verify.py`).
  Pendiente para cerrar la fase: dHash, informe HTML, baseline visual versionado y escenarios multi-escena.
- **Prerrequisito:** Fase 1 completada con tipado limpio. *(Nota: el MVP se adelantó porque no depende
  del tipado; la Fase 1 sigue pendiente por la línea base de 112 errores de Pyright.)*
- **Herramientas a Incorporar:**
  - Creación del paquete interno `tools/test_runner/` (sin librerías externas de runtime).
  - Implementación de `HeadlessRunner`, `VirtualInputController` y `VisualDiffEngine`.
  - Creación del directorio de escenarios `tests/scenarios/` y baselines `tests/visual_baselines/`.
  - Integración de fixture `game_runner` en `tests/conftest.py`.
- **Beneficio Técnico:** Capacidad de que los agentes validen mecánicas completas de juego (moverse, abrir cofres, derrotar enemigos) sin interacción humana y sin abrir ventanas de escritorio.
- **Riesgo:** Divergencias de redondeo de punto flotante en renderizado de texto entre diferentes CPUs que disparen falsos positivos en diff visual.
  - *Mitigación:* Estrategia *three-tier* con tolerancia perceptual y máscaras de exclusión para texto dinámico (e.g. contadores de FPS o tiempo).
- **DoD:**
  - Escenario piloto `player_open_chest.json` ejecutado y validado en < 50 ms.
  - Detección probada de regresión intencionada.
  - Integración en `tools/verify.py`.

---

### Fase 3: Pipeline de Recursos, Empaquetado y Multimedia
- **Prerrequisito:** Fase 2 completada.
- **Herramientas a Incorporar:**
  - Adición de `pillow` al grupo de desarrollo `[project.optional-dependencies] dev`.
  - Creación de script de empaquetado de atlas de texturas `tools/pack_spritesheets.py`.
  - Creación de wrapper CLI de normalización de audio con FFmpeg `tools/process_audio.py`.
  - Integración con el catálogo y base de datos de SQLite en `tools/asset_hub/`.
- **Beneficio Técnico:** Los agentes pueden recibir carpetas de fotogramas PNG individuales o archivos de audio sin procesar y compilarlos automáticamente en atlas y archivos OGG normalizados conformes a las especificaciones del juego.
- **Riesgo:** Dependencia de que el sistema operativo tenga FFmpeg instalado en PATH.
  - *Mitigación:* Comprobación en `tools/process_audio.py`: si `ffmpeg` no está disponible, emitir aviso y omitir paso sin romper el build general.
- **DoD:**
  - Empaquetador de atlas genera texturas optimizadas y manifiestos `gf-anim-v1` válidos.
  - Assets procesados pasan la validación de `tools/validate_character.py`.

---

### Fase 4: Tooling Avanzado de Simulación y Audio Procedural
- **Prerrequisito:** Fase 3 completada.
- **Herramientas a Incorporar:**
  - Pruebas de propiedades con `hypothesis` (suite opcional `tests/pbt/`).
  - Evaluación de generador de efectos sonoros procedurales `pyfxr` en `tools/sfx_gen.py`.
- **Beneficio Técnico:** Detección de casos extremos en generación de mapas celulares y algoritmos de pathfinding A*; síntesis instantánea de SFX por código.
- **Riesgo:** Aumento del tiempo total de la suite de pruebas debido a la generación combinatoria de Hypothesis.
  - *Mitigación:* Marcar los tests de Hypothesis con `@pytest.mark.pbt` y ejecutarlos únicamente en pipelines de CI nocturnos o comandos explícitos de verificación profunda (`pytest -m pbt`).
- **DoD:**
  - Algoritmos matemáticos de `game.core.math2d` y generación de cavernas auditados por 1,000+ casos aleatorios sin colapsos.

---

## 3. Criterios Formales de Promoción de Herramientas (Gating)

Para que una herramienta pase formalmente de la categoría **`PROBAR`** a **`ADOPTAR`**, debe satisfacer los siguientes cuatro (4) criterios de validación:

1. **Evidencia de Cero Impacto en Runtime:** La herramienta no debe añadir bytes ni sobrecarga al paquete final del juego distribuido al usuario (`dependencies` de `pyproject.toml` intacto).
2. **Determinismo y Estabilidad:** Debe ofrecer un comportamiento 100% determinista sin depender de servicios de red, llamadas de telemetría ni servidores remotos.
3. **Eficiencia Temporal y de Recursos:** No debe incrementar el tiempo de ejecución de `tools/verify.py` en más de 3 segundos ni requerir más de 250 MB de memoria RAM.
4. **Interoperabilidad con Agentes:** Debe ser integrable en un script con entrada y salida estandarizada (JSON o códigos de retorno conformes al estándar POSIX), sin intervención interactiva de usuario.

---

## 4. Matriz de Riesgos Técnicos y Mitigaciones

| Riesgo Técnico Identificado | Probabilidad | Impacto | Estrategia de Mitigación Arquitectónica |
|:---|:---:|:---:|:---|
| **Contaminación de Dependencias:** Un agente instala paquetes en runtime por error. | Baja | Alto | Directiva estricta en `01_GLOBAL.md` y verificación en `tools/verify.py` que comprueba que `[project.dependencies]` solo contenga `pygame-ce>=2.5`. |
| **Falsos Positivos en Diff Visual:** Diferencias sub-píxel por rasterizado de fuentes. | Media | Medio | Tolerancia perceptual en `VisualDiffEngine` ($< 0.05\%$ ratio de cambio) y separación de capas de UI volátil. |
| **Tiempo Excesivo en Pruebas PBT:** Hypothesis ralentiza el ciclo de desarrollo diario. | Media | Medio | Aislamiento en suite específica `@pytest.mark.pbt`, excluida de `verify.py` rápido diario. |
| **Falta de FFmpeg en Máquinas Nuevas:** El comando falla al no encontrar el binario. | Media | Bajo | Degradación elegante: el script detecta la ausencia de FFmpeg y reporta advertencia informativa sin abortar el flujo principal. |
| **Deriva del Grafo de Conocimiento:** Cambios en scripts desincronizan el grafo de Graphify. | Baja | Alto | Gancho obligatorio pre-flight y post-flight en `verify.py` que ejecuta `graph_ops.py verify --strict`. |

---

## 5. Estrategia de Rollback y Contención de Daños

En caso de que cualquier herramienta incorporada cause inestabilidad, bloqueos de CI o comportamientos no deterministas:

1. **Protocolo de Marcha Atrás Inmediata:**
   - La inclusión de herramientas en `[project.optional-dependencies] dev` se gestiona mediante commits atómicos reversibles.
   - Si una herramienta de dev falla, se revierte el commit correspondiente sin tocar el código de `game/`.
2. **Aislamiento en Ramas de Herramientas:**
   - Todo nuevo runner o script en `tools/` se desarrolla en una rama independiente y se valida contra los 314 tests existentes antes de integrarse a la rama principal.
3. **Conservación de Baselines:**
   - Las imágenes de referencia visual y esquemas JSON se versionan en Git con etiquetas inmutables, permitiendo regresar a la versión previa ante cualquier alteración de renderizado.
