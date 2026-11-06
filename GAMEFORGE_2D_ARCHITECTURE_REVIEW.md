# GAMEFORGE 2D — Revisión de arquitectura y auditoría del paquete inicial

**Documento:** GAMEFORGE_2D_ARCHITECTURE_REVIEW.md
**Fecha:** 2026-11-06
**Autor:** Agente arquitecto principal (MISIÓN 001)
**Estado:** BORRADOR PARA APROBACIÓN — nada de lo aquí propuesto se ha aplicado al repositorio.
**Alcance:** auditoría del paquete inicial, comparación tecnológica, arquitectura objetivo,
organización multiagente, skills, contratos, plan por fases, benchmark, riesgos y decisiones pendientes.

---

## Convenciones de este informe

- **[HECHO]**: verificado directamente en este entorno (comando ejecutado, archivo leído) o con fuente citada.
- **[FUENTE]**: afirmación verificada en documentación/web oficial; URL indicada.
- **[RECOMENDACIÓN]**: juicio técnico del arquitecto; requiere aprobación del director.
- **[PENDIENTE]**: dato no verificado; se indica qué verificación falta.

Entorno donde se realizó la auditoría: Windows 10 19043 x64, Python 3.12.10, pygame-ce 2.5.8, Git Bash.

---

# 1. AUDITORÍA DEL PAQUETE INICIAL

## 1.1 Qué contiene realmente el paquete

El paquete `GAMEFORGE_2D_AGENT_KIT` no es solo un kit de plantillas: incluye **dos capas**:

1. **Infraestructura de agentes** (el "kit" propiamente dicho):
   `AGENTS.md`, `directives/` (4), `architecture/CONTRACTS.md`, `prompts/` (4),
   `skills/` (7), `benchmark/` (2 scripts + METRICS.md), `references/OPEN_SOURCE_REFERENCES.md`,
   `documentation/` (4 docs), `assets/README.md`, `LICENSE` (MIT).
2. **Un vertical slice de juego ya implementado** ("La Fragua Olvidada" v0.1.0):
   `game/` (~5.400 líneas en 40 módulos), `tests/` (19 archivos), `game/data/config.json`,
   ejecutable con `python -m game`.

Esto condiciona toda la misión: **no se diseña desde cero; se decide si el slice existente
es la base correcta para el RPG completo** (ver §14, decisión D1).

## 1.2 Verificación ejecutada en este entorno [HECHO]

| Comprobación | Comando | Resultado |
|---|---|---|
| Suite de pruebas | `python -m pytest -q` | **112 passed** en 37.68 s |
| Smoke test sin ventana | `python -m game --headless --frames 60` | OK (exit 0) |
| Benchmark de generación | `python benchmark/bench_generation.py` | p50 17.14 ms, p95 29.62 ms, máx 149.06 ms (mapa 64×48, 11 salas, 30 enemigos) |
| Benchmark de simulación | `python benchmark/bench_simulation.py` | p50 9.17 ms, **media 12.57 ms, p95 32.75 ms, máx 506.92 ms** (3.000 frames, 24 enemigos; presupuesto 60 FPS = 16.67 ms) |
| Control de versiones | `git status` | **NO es un repositorio git** (no existe `.git`) |
| Dependencias | `pip show pygame-ce` | pygame-ce 2.5.8 instalado; Python 3.12.10 |

**Lectura del benchmark:** la media cabe en el presupuesto de 60 FPS, pero el **p95 lo excede
casi 2×** con solo 24 enemigos. No es un problema del slice actual (juega a ~60–80 FPS), pero
marca el techo de escalado: sin indexación espacial ni culling de actualización, el objetivo
"mapas grandes + NPCs autónomos" no se alcanza sobre esta base tal cual (ver §7 y §13).

## 1.3 Fortalezas verificadas del código existente

1. **Separación dominio/presentación REAL y verificada.** `grep -rn "import pygame"` confirma
   que pygame solo entra por `game/app.py`, `game/input/`, `game/render/` y `game/scenes/`.
   `core/`, `world/`, `entities/`, `systems/` y `persistence/` son puros y se prueban sin vídeo
   (`tests/conftest.py` fuerza `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy`).
2. **Sin smells graves:** cero `except Exception: pass`, cero `time.sleep` en `game/`;
   el bucle principal (`game/app.py:100-127`) limita `dt` a 50 ms, no hace I/O y reparte
   eventos de forma predecible.
3. **Determinismo y persistencia sólidos:** generación por semilla con validación BFS
   obligatoria (`game/world/generation.py:85-116`), guardado JSON atómico validado con
   versión de esquema, límites de tamaño y colecciones (`game/persistence/savegame.py`),
   clasificación SQLite idempotente.
4. **Contratos documentados y sincronizados con el código**
   (`architecture/CONTRACTS.md`, sección "v0.1.0"), con ADRs en `documentation/DECISIONS.md`.
5. **Configuración validada fuera del código** (`game/core/config.py`, `game/data/config.json`).
6. **Honestidad documental:** `README.md` declara limitaciones reales (una planta, resolución
   fija 1280×720, clasificación local, audio con degradación).

## 1.4 Debilidades y hallazgos

| # | Hallazgo | Evidencia | Gravedad |
|---|---|---|---|
| A1 | **No hay repositorio git.** AGENTS.md exige entrega por rama/commit y flujo director→integrador→QA; sin git, ese flujo es imposible y no hay historial ni rollback. | `git status` → fatal [HECHO] | **CRÍTICO** |
| A2 | **`game/scenes/play.py` es un orquestador de 564 líneas** (input, combate, cofres, hoguera, altar, poción, toasts, guardado, fin de partida). Es el punto donde desembocaría todo el contenido nuevo (misiones, crafting, diálogo, multiplanta). | `wc -l`; índice de métodos [HECHO] | ALTO (crecimiento) |
| A3 | **Enemigos no son data-driven:** comportamiento por tipo hardcodeado en métodos `_update_slime/_update_wisp/_update_brute` (`game/entities/enemies.py:111-190`). Añadir tipos exige editar un único archivo propiedad de un solo agente → cuello de botella multiagente. | lectura directa [HECHO] | MEDIO |
| A4 | **Sin pathfinding.** La IA actual es distancia+línea de visión. Los objetivos del RPG (NPC autónomos, misiones, horarios) exigen navegación por el mapa. | `enemies.py`, `collision.py` [HECHO] | MEDIO (fase 2) |
| A5 | **p95 de simulación sobre presupuesto** (32.75 ms > 16.67 ms con 24 enemigos); sin spatial hashing, sin actualización selectiva de sistemas. | `bench_simulation.py` [HECHO] | MEDIO |
| A6 | **Residuos en la raíz:** ~15 `_*.bat`, `_*.txt`, `install.log`, `_diag*.txt` de sesiones de bootstrap anteriores; no están en `.gitignore`. | `ls` raíz [HECHO] | BAJO (higiene) |
| A7 | **Skills demasiado delgadas:** entre 3 y 24 líneas; les faltan propósito detallado, procedimientos, criterios de aceptación y referencias que exige la misión (§7 de este informe las rediseña). | lectura de `skills/` [HECHO] | MEDIO |
| A8 | **Sin definición de CI:** no hay workflow ni script único de "lint+test+bench" que un agente pueda ejecutar como verificación estándar. `ruff` está configurado en `pyproject.toml` pero no hay evidencia de uso sistemático. | inventario [HECHO] | MEDIO |
| A9 | **Benchmark de agentes incompleto:** `benchmark/METRICS.md` define rúbrica de puntuación pero no define tareas estándar ni procedimiento de ejecución comparable. | lectura [HECHO] | MEDIO |
| A10 | `requirements.txt` duplica `pyproject.toml` (puede desincronizarse). | lectura [HECHO] | BAJO |
| A11 | **Una sola planta por partida** aunque el generador ya acepta `floor` y escala enemigos con él (`generation.py:232`: `enemies_per_room + floor // 2`); el encadenamiento no existe a nivel de escenas. | lectura [HECHO] | BAJO (por diseño) |
| A12 | Ventana fija 1280×720 sin lienzo virtual; el objetivo "interfaz adaptable" requiere separar resolución lógica de física. | README §Limitaciones [HECHO] | BAJO (fase 4) |

**Conclusión de la auditoría:** la base es **notablemente mejor de lo que cabe esperar de un
kit inicial**: arquitectura limpia, 112 pruebas reales que pasan, determinismo, persistencia
segura. Los problemas reales son organizativos (A1 git, A7 skills, A9 benchmark) y de
escalado futuro (A2, A3, A4, A5), no de calidad del código presente.

---

# 2. COMPARACIÓN TECNOLÓGICA

## 2.1 Motor/framework de renderizado 2D

| Opción | Versión actual | Actividad | Licencia | Veredicto para GAMEFORGE |
|---|---|---|---|---|
| **Pygame CE** | 2.5.8 (ago 2026), soporta Python 3.10–3.15 | Muy activa; fork mantenido por los desarrolladores originales; publica benchmarks propios | LGPL-2.1-or-later | **MANTENER** [RECOMENDACIÓN]. Ya validado por el slice (112 tests). API estable, superficie mínima, ideal para tile-based top-down. |
| Pygame clásico | 2.5.x estancado desde 2024 | Prácticamente dormido; problemas de instalación en Python ≥3.13 | LGPL | Descartar [FUENTE: pyga.me/docs/pygame-api-diffs, consenso comunidad] |
| **Arcade** | 3.3.3 (oct 2025); 4.0 en desarrollo | Activa; render pyglet/OpenGL, sprites y tilemaps integrados | MIT | **Alternativa seria pero NO migrar**: exigiría reescribir render/escenas completos; su ventaja (GPU, sprites masivos) no es decisiva para un RPG tile-based con cientos de entidades; añade dependencia de pyglet. Documentar como plan B si se necesitara render GPU intensivo. [FUENTE: pypi.org/project/arcade, api.arcade.academy] |
| Pyglet | 2.1.19 | Mantenido | BSD | Solo relevante como base de Arcade; no usar directamente. |
| python-tcod | 21.2.2, port a SDL3 en 2025 | Muy activo | BSD (tcod) / LGPL (libtcod) | Solo si el juego derivara hacia roguelike de consola. No aplica a top-down gráfico. [FUENTE: python-tcod.readthedocs.io] |

## 2.2 Física y colisiones

| Opción | Estado | Veredicto |
|---|---|---|
| Colisión tile-based propia (actual) | Subdivisión de pasos + resolución por ejes (`world/collision.py`), determinista, testeada | **MANTENER** para el núcleo top-down. ADR-002 sigue siendo correcta. |
| **Pymunk 7.2.0** (nov 2025, wheels Py3.14) [FUENTE: pymunk.org changelog] | Muy mantenido, MIT, wrapper de Chipmunk2D | **No adoptar ahora**; revisar si aparecen: bloques empujables, cuerdas, plataformas con arrastre, física de proyectiles continua. Si ocurre, adoptar solo en el subsistema que lo necesite (no global). |
| ECS (python-esper) | Mantenimiento ligero; ecosistema pequeño | **No adoptar**: el diseño actual por composición de dataclasses ya es testeable; ECS añadiría indirección sin beneficio medido. |

## 2.3 Autoría de mapas

| Herramienta | Estado | Veredicto |
|---|---|---|
| **Tiled 1.12.2** (may 2026), muy activo [FUENTE: mapeditor.org] | Editor maduro, export JSON | **Adoptar en Fase 3** para mapas diseñados a mano (pueblos, mazmorras fijas) conviviendo con la generación procedural. |
| **PyTMX 3.31** (mantenido, Py≥3.9) [FUENTE: github.com/bitcraft/pytmx] | Cargador TMX para Python | Adoptar junto a Tiled cuando exista el primer mapa autoral. Verificar licencia exacta del tag adoptado. |
| LDtk 1.5.3 (activo) | Excelente UX, formato JSON propio | No adoptar: formato menos estándar que TMX y sin ventaja clara para top-down tile-based. |

## 2.4 Navegación e IA de NPC

| Opción | Estado | Veredicto |
|---|---|---|
| **A\* propio sobre grid** | — | **RECOMENDADO**: mapa ≤ ~128×128 por planta, presupuesto por frame, caché de rutas, rectificado con steering; testeable con semillas, sin dependencias. Es ~150 líneas. |
| `pathfinding` (brean/python-pathfinding, ~382 estrellas) | Mantenida, PyPI `pathfinding` | Descartar como dependencia: crea un `Node` por celda (coste de objetos en mapas grandes) y no permite presupuestar por frame; útil como referencia de pruebas. |
| networkx | Mantenido | Demasiado general y pesado para hot-path de juego. |
| Behaviour trees (py_trees) | Mantenido (robótica) | No adoptar: FSM + utilidad simple cubren el diseño actual con menos maquinaria. |

## 2.5 Persistencia, audio, empaquetado

- **Persistencia**: mantener JSON atómico versionado (partida) + SQLite (clasificación/telemetría local) [RECOMENDACIÓN]. Verificar necesidad de migraciones con esquema de misiones en Fase 2.
- **Audio**: mantener mezclador de pygame-ce con SFX sintetizados; añadir música por archivos OGG en Fase 4 **solo con licencia registrada** en `assets/README.md` (ADR-003 se mantiene hasta entonces).
- **Empaquetado**: PyInstaller es la vía estándar para juegos pygame [FUENTE: pyglet/pygame docs y comunidad]; evaluar en Fase 5, no antes.
- **Python**: mantener suelo `>=3.11` (actual) y desarrollar en 3.12. Los datos públicos muestran ganancias modestas y dependientes de la carga en 3.13 (incluso regresiones puntuales) y JIT/free-threading experimentales: **no perseguir 3.13/3.14 por rendimiento** [FUENTE: benchmarks públicos 2024-2026, enlaces en §6]. Pygame CE cubre hasta 3.15 si hiciera falta.

---

# 3. ARQUITECTURA RECOMENDADA

## 3.1 Principios rectores (revisados)

1. **Conservar el núcleo validado**: capas `core/input/world/entities/systems/persistence`
   sin pygame; `render/scenes/app` como única frontera del framework. Verificado en §1.3.
2. **Descomponer el orquestador**: lo que hoy vive en `PlayScene` se reparte en *sistemas*
   de simulación puros (ordenados, testeables, sin pygame) que la escena limita a invocar.
3. **Datos antes que código para contenido**: enemigos, objetos, misiones y diálogos pasan a
   ficheros de datos (JSON) con catálogos validados; el código lee, no define.
4. **El mundo es multiplanta desde el diseño de datos**: `floor` ya existe en generador y
   guardado; formalizar `World` como raíz de plantas encadenadas.
5. **Presupuesto de simulación explícito**: cada sistema declara coste objetivo; el bucle
   mide (frame-time p50/p95) y existe presupuesto de actualización (staggering) para IA lejana.
6. **Sin bus de eventos global** mientras quepa llamadas directas (ADR-006 vigente); si las
   misiones/logros/audio reactivo lo exigen, evaluar un bus tipado acotado como cambio de contrato.

## 3.2 Cambios estructurales propuestos sobre el código existente

1. **Nuevo `game/sim/` (o reutilizar `systems/` ampliado)** con sistemas de simulación puros:
   `combat_system`, `interaction_system`, `quest_system`, `crafting_system`, `floor_system`
   (encadenado de plantas). `PlayScene` se reduce a traducción input→intenciones y render.
2. **`game/data/` se convierte en catálogo**: `enemies.json`, `items.json`, `quests.json`,
   `recipes.json`, `dialogues.json` con `from_dict` validado (mismo patrón que `GameConfig`).
   Los enemigos se definen por datos + componentes de comportamiento reutilizables
   (mover/perseguir/disparar/melee), eliminando métodos por tipo (A3).
3. **Nuevo `game/ai/`**: `astar.py` (grid, presupuestado, cacheable), `steering.py`,
   `behavior.py` (FSM data-driven), `schedules.py` (horarios NPC). Sin pygame.
4. **`game/world/` gana escala**: `spatial.py` (spatial hash para consultas de proximidad),
   actualización por proximidad (IA lejana a baja frecuencia), y opcional carga por chunks
   cuando existan mapas Tiled autorales.
5. **`game/render/` gana resolución lógica**: lienzo virtual + escalado (interfaz adaptable),
   manteniendo la pre-renderización de mapa estático y cachés existentes.
6. **`tools/` nuevo**: script único `verify.py` (lint+test+bench) y generador de informes de
   tarea; es la verificación estándar que todo agente debe ejecutar (A8).

## 3.3 Diagrama de componentes (objetivo)

```
                    ┌────────────────────────────────────────────────┐
                    │                app.py (ciclo)                  │
                    │  dt limitado · eventos · escena activa · flip  │
                    └──────┬───────────────────────────┬─────────────┘
                           │ invoca                    │ posee servicios
                           ▼                           ▼
   ┌──────────┐    ┌──────────────┐          ┌──────────────────┐
   │  input/  │───▶│   scenes/    │─────────▶│   persistence/   │
   │ acciones │    │ (flujo UI,   │          │ JSON+SQLite      │
   └──────────┘    │  orquesta)   │          └──────────────────┘
                   └──────┬───────┘
                          │ traduce intenciones ←→ estado
                          ▼
         ┌─────────────────────────────────────┐
         │        sim/  (sistemas puros)       │
         │  combat · interact · quest · craft  │
         │  floor(chained) · loot              │
         └───┬──────────┬──────────┬───────────┘
             │          │          │
             ▼          ▼          ▼
       ┌──────────┐ ┌────────┐ ┌──────────────┐
       │ world/   │ │entities│ │     ai/      │
       │ tilemap  │ │player  │ │ astar(cuota  │
       │ collision│ │enemy   │ │   por frame) │
       │ generation│ │npc     │ │ steering     │
       │ spatial  │ │item    │ │ behavior(FSM)│
       │          │ │        │ │ schedules    │
       └──────────┘ └────────┘ └──────────────┘
             │          │
             ▼          ▼
       ┌─────────────────────────┐     ┌──────────────┐
       │      core/ (sin pygame) │     │   data/      │
       │ config · math2d · clock │     │ enemies.json │
       └─────────────────────────┘     │ quests.json  │
                                      │ items.json … │
                   ┌──────────────────┴──────────────┐
                   │          render/ (lee estado)   │
                   │ tiles · entities · hud · light  │
                   │ effects · audio · ui (canvas    │
                   │ virtual escalable)              │
                   └─────────────────────────────────┘

   Flujo de dependencia (sin ciclos):
   core ◀ world ◀ entities ◀ ai ◀ sim ◀ scenes ◀ app
                     ▲                ▲
                     └── data (catálogos validados al cargar)
   pygame SOLO en: input, render, scenes, app   [HECHO hoy; se conserva]
```

## 3.4 Rendimiento: cómo medir y qué exigir (sin optimizar antes de tiempo)

1. **Medición ya existe** (`benchmark/`) y se conserva como puerta de regresión:
   - `bench_simulation.py`: p50/p95/max frame-time con N enemigos → umbrales de CI:
     p95 ≤ 16.67 ms con 100 entidades (objetivo Fase 3) [RECOMENDACIÓN de umbral].
   - `bench_generation.py`: p95 de generación ≤ 100 ms para 128×96 [RECOMENDACIÓN].
2. **Presupuesto por sistema**: cuando `sim/` exista, medir cada sistema por separado
   (envoltorio de reloj en modo debug) antes de repartir staggering.
3. **Indexación espacial primero, chunks después**: el spatial hash resuelve el cuello actual
   (consultas O(n²) de separación/ataque); los chunks solo si los mapas Tiled lo exigen.
4. **RAM**: medir con `tracemalloc` en el bench (añadir al script) en vez de asumir.
5. Regla de oro del kit, que se mantiene: **medir antes de optimizar**; ningún agente optimiza
   sin un número que demuestre el problema.

---

# 4. DIAGRAMA DE COMPONENTES (resumen visual alternativo por capas)

```
┌─────────────────────── CAPA PRESENTACIÓN (pygame) ───────────────────────┐
│ app.py · scenes/(menu,play,help,board,results) · render/* · input/*      │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ lee estado / traduce acciones
┌─────────────────────── CAPA SIMULACIÓN (pura) ───────────────────────────┐
│ sim/(combat,interact,quest,craft,floor,loot) · entities/* · ai/*         │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ usa
┌─────────────────────── CAPA MUNDO (pura) ────────────────────────────────┐
│ world/(tilemap,collision,generation,spatial,camera)                      │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ usa
┌──────────── CAPA BASE (pura) ─┴─────────────┐  ┌── DATOS ────────────────┐
│ core/(config,math2d) · persistence/         │  │ data/*.json (catálogos) │
└─────────────────────────────────────────────┘  └─────────────────────────┘
```

---

# 5. ESTRUCTURA DE DIRECTORIOS DEFINITIVA (PROPUESTA — no aplicada)

La estructura propuesta **conserva el paquete original intacto** y muestra la reorganización
objetivo. La migración sería gradual (Fase 1) y aprobada por separado.

```
GAMEFORGE/
├── AGENTS.md                     # reglas del kit (revisado, §8)
├── GAMEFORGE_2D_ARCHITECTURE_REVIEW.md   # este informe
├── LICENSE · README.md · pyproject.toml
├── directives/                   # 01_GLOBAL … 04_INTEGRATION (revisados)
├── architecture/
│   ├── CONTRACTS.md              # registro único de interfaces (§10)
│   └── OWNERSHIP.md              # matriz archivo↔agente (§9.3)   [NUEVO]
├── tasks/                        # tablero de tareas file-based   [NUEVO]
│   ├── BOARD.md
│   └── reports/                  # informes de entrega por tarea
├── prompts/                      # prompts de agentes (actualizados)
├── skills/                       # skills rediseñadas (§7)
├── documentation/
│   ├── ARCHITECTURE.md · DECISIONS.md · DEPENDENCIES.md · TESTING.md
│   └── PHASES.md                 # plan por fases vivo           [NUEVO]
├── references/                   # catálogo verificado (§6)
├── benchmark/
│   ├── bench_generation.py · bench_simulation.py · METRICS.md
│   └── agent_tasks/              # suite de tareas estándar (§12) [NUEVO]
├── tools/
│   └── verify.py                 # lint+test+bench en un comando  [NUEVO]
├── assets/
│   └── README.md                 # registro de licencias (se amplía en F4)
├── game/
│   ├── __main__.py · app.py
│   ├── core/         config.py · math2d.py
│   ├── input/        actions.py
│   ├── world/        tilemap · tiles · collision · generation · camera
│   │                 + spatial.py            [NUEVO F3]
│   ├── entities/     player · enemies(→datos) · projectiles · interactables · items · npc.py [NUEVO F2]
│   ├── ai/           astar · steering · behavior · schedules     [NUEVO F2]
│   ├── sim/          combat · interact · quest · crafting · floor · loot [NUEVO F1-F2]
│   ├── systems/      inventory (existente; se fusiona en sim/ al migrar)
│   ├── persistence/  paths · savegame · scores
│   ├── render/       tiles · entity · hud · ui · light · effects · audio · fonts · background
│   │                 + canvas virtual escalable [NUEVO F4]
│   ├── scenes/       base · menu · play(reducida) · help · leaderboard · results
│   └── data/         config.json + enemies.json · items.json · quests.json ·
│                     recipes.json · dialogues.json                 [NUEVO F2]
└── tests/                        # espejo de game/ + fixtures por sistema
```

**Cambios frente a la estructura actual** (todos graduales): nuevos `ai/`, `sim/`, `tools/`,
`tasks/`, catálogos JSON en `data/`, `OWNERSHIP.md`; `play.py` pierde ~2/3 de su código en
favor de `sim/`; `systems/inventory` se reubica dentro de `sim/` manteniendo la API pública
(contrato) para no romper tests.

---

# 6. CATÁLOGO DE REPOSITORIOS Y LICENCIAS

Política heredada del kit (vigente): no copiar código/assets sin verificar licencia;
registrar versión/commit; revalidar antes de congelar entorno.

## 6.1 Dependencias y herramientas del stack

| Proyecto | URL | Licencia | Actividad | Uso previsto | Recomendación |
|---|---|---|---|---|---|
| Pygame CE | github.com/pygame-community/pygame-ce | LGPL-2.1-or-later [FUENTE: repo] | 2.5.8 ago-2026; Py 3.10–3.15 | Motor 2D principal | **Adoptada ya**; mantener |
| pytest | github.com/pytest-dev/pytest | MIT | Activo | Pruebas | Adoptada |
| ruff | github.com/astral-sh/ruff | MIT | Activo | Lint | Adoptada (exigir en `tools/verify.py`) |
| Arcade | github.com/pythonarcade/arcade | MIT | 3.3.3 oct-2025; 4.0 dev | Alternativa | Solo plan B documentado |
| pyglet | github.com/pyglet/pyglet | BSD | 2.1.x | Base de Arcade | No usar directo |
| Pymunk | github.com/viblo/pymunk | MIT | 7.2.0 nov-2025 | Física rígida | No adoptar (disparador definido en §2.2) |
| python-tcod | github.com/HexDecimal/python-tcod | BSD (tcod) | 21.2.2, SDL3 en 2025 | Roguelike consola | No aplica |
| Tiled | github.com/mapeditor/tiled | BSD (verificar tag exacto) | 1.12.2 may-2026 | Editor de mapas | Adoptar en F3 |
| PyTMX | github.com/bitcraft/pytmx | MIT (verificar tag) | 3.31 | Carga TMX | Adoptar con Tiled en F3 |
| LDtk | github.com/deepnight/ldtk | ISC/pago (verificar) | 1.5.3 | Editor | No adoptar |
| brean/python-pathfinding | github.com/brean/python-pathfinding | MIT (verificar) | Mantenida, ~382★ | Referencia A* | Referencia de pruebas; no dependencia |

## 6.2 Referencias de estudio y dependencias potenciales (verificadas 2026-11-06)

### RPGs completos en Python

| Proyecto | URL | Licencia | Actividad | Qué se aprovecha | Recomendación |
|---|---|---|---|---|---|
| The-Stolen-Crown-RPG | github.com/justinmeister/The-Stolen-Crown-RPG | **MIT** (verificada) | Antiguo (Python 2.7 / pygame 1.9), sin mantenimiento | Estructura completa de RPG: estados, combate por turnos, tienda, misiones, niveles | **Referencia de arquitectura** (conceptos, no código) |
| pyzelda-rpg | github.com/artemn0va/pyzelda-rpg | **MIT** (verificada) | Proyecto personal; último commit no verificado | El ejemplo más cercano al objetivo: top-down, mapas Tiled, cámara, animación, partículas, pathfinding, save/load | **Referencia de arquitectura** (F2–F3) |
| Python-2D-RPG | github.com/rrhan0/Python-2D-RPG | **NINGUNA** (verificado: sin LICENSE) | No verificado | — | **Solo lectura conceptual; prohibido reutilizar código** (sin licencia = todos los derechos reservados) |

### Framework y ejemplos

| Proyecto | URL | Licencia | Nota | Recomendación |
|---|---|---|---|---|
| pygame-ce `examples/` | github.com/pygame-community/pygame-ce | LGPL-2.1+ | Incluye ejemplos propios; topic `pygame-games` con 1000+ juegos | Referencia F1 |
| python-tcod + tutorial oficial | github.com/libtcod/python-tcod | **BSD-2** (verificada) | Activo (2.160+ commits); FOV, BSP, A* con backend C | Tutorial oficial = mejor guía verificada de arquitectura RPG/roguelike en Python (estado, acciones, datos). Referencia F2 |

### Generación procedural

| Proyecto | URL | Licencia | Nota | Recomendación |
|---|---|---|---|---|
| WaveFunctionCollapse | github.com/mxgmn/WaveFunctionCollapse | **MIT** (verificada; los tiles de ejemplo NO están cubiertos) | C#; canónico (~25.500★) | Solo estudio del algoritmo (F3: biomas por restricciones) |
| wfc (puerto Python) | github.com/baskiton/wfc | MIT | Esencialmente inactivo | Solo estudio |
| opensimplex | PyPI `opensimplex` (code.larus.se/lmas/opensimplex) | **MIT** | Última release may-2024 | **Candidata a dependencia** (ruido de biomas) en F3, previa medición |
| BSP dungeon | RogueBasin ("Basic BSP Dungeon Generation") + BSP de python-tcod | — | Artículos de referencia | Implementación propia (el generador actual ya hace salas+corredores) |

### IA, partículas, animación, ECS, diálogo

| Proyecto | URL | Licencia | Nota | Recomendación |
|---|---|---|---|---|
| python-pathfinding | github.com/brean/python-pathfinding | **MIT** (verificada) | Mantenida (234 commits, issues activos) | Ver D5: A* propio como principal; esta librería como alternativa si el profiling favorece no mantener código propio |
| py_trees | github.com/splintered-reality/py_trees | **BSD-3** (verificada) | Muy mantenida (2.6.x, CI), origen robótica | Solo referencia; FSM propia suficiente |
| bubbles (partículas) | github.com/jaynewey/bubbles | MIT | Señal débil (16★) | Referencia de diseño (emisor/renderer separados); el sistema propio ya cubre el slice |
| pygame-particles (Mekire) | github.com/Mekire/pygame-particles | — | **Archivado** | Descartado |
| pyganim | github.com/asweigart/pyganim | BSD-style (tipo exacto no verificado) | Sin mantener años | Descartado; clase `Animation` propia (~50 líneas, ver skill `assets_animation`) |
| esper (ECS) | github.com/benmoran56/esper | **MIT** (verificada) | Mantenida; 3.0 con breaking changes | Referencia; no adoptar (§2.2) salvo cambio de requisitos de entidades |
| YarnSpinner | github.com/YarnSpinnerTool/YarnSpinner | **MIT** (verificada) | Activo, pero runtime oficial C# | Solo estudio del formato `.yarn`; diálogo propio JSON en F2 |
| Ren'Py | github.com/renpy/renpy | MIT + porciones LGPL | Motor completo, no incrustable en pygame | Solo estudio conceptual |

**Top-5 de referencias para GAMEFORGE:** (1) pygame-ce + sus ejemplos; (2) tutorial oficial
de python-tcod (arquitectura); (3) The-Stolen-Crown-RPG (estructura de RPG, MIT);
(4) pyzelda-rpg (top-down + Tiled + save/load, MIT); (5) WaveFunctionCollapse (estudio WFC).

> **No verificados / inexistentes** (excluidos expresamente): "Dungeon of Potency" (no existe
> como tal), "pysurvival" como juego (es una librería ML), runtime Python oficial de Yarn
> Spinner, pybts (licencia/actividad sin confirmar). Ninguno entra en el plan.

---

# 7. SKILLS RECOMENDADAS

Principios del rediseño: (1) ninguna redundante — una responsabilidad, una skill;
(2) todas con la estructura completa exigida (propósito, contexto, instrucciones, buenas
prácticas, referencias, procedimientos, criterios de aceptación, pruebas);
(3) alineadas con fases; (4) las 7 actuales se conservan como núcleo y se expanden.

| Skill (directorio) | Propósito | Cambio propuesto |
|---|---|---|
| `pygame_ce` | Uso correcto del framework (display, surfaces, audio, eventos) | Expandir: convert/convert_alpha, límites de mixer, modo dummy, referencias oficiales, DoD |
| `python_game_architecture` | Límites dominio/framework, inyección, sin estado global | Expandir con el patrón `sim/` (sistemas puros) y reglas de dependencias del proyecto |
| `game_ai` | FSM/percepción/navegación presupuestada | Expandir: A* con presupuesto por frame, caché de rutas, spatial hash, tests con semilla |
| `game_physics` | Elección tile-based vs Pymunk; tunneling | Mantener; añadir disparador exacto de adopción de Pymunk (§2.2) |
| `procedural_generation` | Determinismo, validación BFS, semillas | Mantener; añadir multiplanta/biomas y umbrales del bench |
| `assets_animation` | Atlas, pivotes, licencias | Mantener; añadir registro obligatorio en `assets/README.md` |
| `testing_performance` | Pruebas y medición | Expandir: umbrales p95, `tools/verify.py`, tracemalloc |
| `data_driven_content` [NUEVA] | Catálogos JSON validados (enemigos/ítems/misiones/diálogo) | Nueva: patrón `from_dict` estricto, esquemas, versionado |
| `persistence_versioning` [NUEVA] | Guardados versionados, migraciones, corrupción | Nueva: extiende ADR-004/008 con recetas de migración |
| `ui_scaling` [NUEVA] | Lienzo virtual, escalado, layouts | Nueva (F4): resolución lógica vs física |
| `git_multiagent` [NUEVA] | Flujo git para agentes: ramas cortas, diff revisable, conflictos | Nueva (crítica tras hallazgo A1) |
| `qa_reporting` [NUEVA] | Informes de QA con severidades y evidencia reproducible | Nueva: formaliza `prompts/02_qa_agent.md` como skill |

Las skills nuevas no duplican las existentes: cubren responsabilidades que hoy nadie documenta
(datos, persistencia versionada, UI escalable, git multiagente, QA).

---

# 8. DIRECTIVAS GLOBALES REVISADAS

Las 4 directivas actuales son sólidas; se proponen enmiendas puntuales:

1. **01_GLOBAL**: añadir "el control de versiones es obligatorio desde Fase 0; toda entrega
   es un commit/rama revisable" y "ningún cambio sin `tools/verify.py` verde".
2. **02_ARCHITECTURE**: añadir la regla de dependencias objetivo (§3.3) y el principio
   "contenido en `data/`, no en código".
3. **03_QUALITY_AND_SECURITY**: añadir umbrales de rendimiento como criterio de aceptación
   (p95 del bench) y la obligación de registrar licencia de todo asset externo.
4. **04_INTEGRATION**: reemplazar "diff/commit" genérico por el flujo git concreto
   (rama corta → verificación → integrador → QA → director) y definir el tablero `tasks/`
   como mecanismo de comunicación.
5. **AGENTS.md**: sin cambios de fondo; enlazar `OWNERSHIP.md` como normativa de ámbitos.

---

# 9. ORGANIZACIÓN DE AGENTES

## 9.1 Evaluación de la división propuesta por la misión

La división de 10 roles (director, arquitecto, gameplay, gráficos, procedural, IA, física,
audio, QA, integrador) es **ineficiente para este proyecto** por tres razones:
(a) física y audio son subsistemas pequeños en un RPG tile-based (física ≈ ya resuelta por
tile-based; audio ≅ un módulo de mezcla); (b) agentes = coste de coordinación por archivo
compartido (`play.py`, `enemies.py` serían cuellos de botella); (c) el kit ya demostró que
el flujo director→especialista→QA funciona con menos roles.

## 9.2 Roles definitivos [RECOMENDACIÓN]

| Rol | Responsabilidad | Ámbito (archivos propios) |
|---|---|---|
| **DIRECTOR/ARQUITECTO** (fusión de 2) | Planifica, define contratos, aprueba cambios de contrato, asigna tareas, decide | `tasks/`, `architecture/`, `directives/` |
| **GAMEPLAY** | `entities/`, `sim/` (combate, interacción, misiones, crafting, loot, plantas) | `game/entities/`, `game/sim/`, `game/systems/` |
| **PRESENTACIÓN** (gráficos+audio fusionados) | `render/`, escenas de UI, lienzo virtual, mezcla de audio | `game/render/`, `game/scenes/`, `game/input/` |
| **PROCEDURAL** | Generación, biomas, validación, escalado de mapas | `game/world/generation.py`, `benchmark/bench_generation.py` |
| **IA/NPC** | A*, steering, FSM data-driven, horarios, diálogos (datos) | `game/ai/`, `game/data/enemies.json` (comportamientos) |
| **QA/INTEGRADOR** (fusión de 2) | Regresión, umbrales de bench, integración de ramas, informes | `tests/` (solo añade), `tools/verify.py` |

El **física** se asigna a Gameplay con la skill `game_physics`; si se dispara la adopción de
Pymunk (§2.2), se crea el rol físico puntual. El **audio** queda en Presentación hasta que
exista música/asset pipeline propio (entonces se valora separarlo).

## 9.3 Mecanismos

1. **Propiedad por archivo** (`architecture/OWNERSHIP.md`): cada ruta tiene un único agente
   responsable; los archivos compartidos (`CONTRACTS.md`, `data/*.json`, `config.json`)
   solo cambian vía propuesta aprobada por el director.
2. **Tablero de tareas file-based** (`tasks/BOARD.md`): columnas `propuesta/aprobada/
   en_curso/entregada/verificada`; cada tarea: objetivo, archivos permitidos, criterios de
   aceptación, agente, informe asociado (`tasks/reports/T-XXX.md`).
3. **Comunicación asincrónica por archivos** (funciona para agentes y es auditable): no hay
   herramienta externa obligatoria.
4. **Integración**: ramas cortas por tarea → `tools/verify.py` verde → integrador fusiona →
   QA ejecuta regresión + bench → director cierra la tarea.
5. **Prohibición de autoaprobación** (vigente del kit): quien implementa no aprueba.

---

# 10. CONTRATOS DE INTERFACES

Los contratos vigentes de `CONTRACTS.md` (v0.1.0) se mantienen. Adiciones propuestas para
el crecimiento (borradores; requieren aprobación antes de implementarse):

```text
## ai.astar (nuevo)
- find_path(map, start, goal, budget_ms) -> list[Vec2] | None
- Nunca excede budget_ms: devuelve la mejor ruta parcial o None.
- Misma (map, start, goal) => mismo resultado; sin estado global.
- Cache LRU por (floor, goal_tile) invalidada al cambiar el mapa.

## ai.behavior (nuevo)
- Un comportamiento se define por datos en data/enemies.json (estados, transiciones,
  parámetros); el motor de FSM no conoce tipos concretos de enemigo.
- tick(entity, ctx, dt) -> Intent; sin creación de objetos de render.

## sim.floor (nuevo)
- advance(dungeon_state, result) -> FloorTransition {spawn, theme, quests_spawned}
- Determinista por (seed, floor); el guardado persiste (seed, floor) como hoy.

## data catalogues (nuevo)
- Todo catálogo expone load_xxx(path) -> Catalog con validación estricta
  (mismo patrón que GameConfig: tipos, rangos, errores accionables).
- Versión de esquema por catálogo; desconocida => error explícito.

## render.canvas (nuevo, F4)
- Resolución lógica fija de diseño; el escalado a ventana es transparente
  para scenes/; transformación de coordenadas de ratón incluida.
```

Regla vigente que se conserva y refuerza: **ningún agente cambia un contrato compartido sin
propuesta + análisis de impacto + aprobación del director.**

---

# 11. PLAN DE DESARROLLO POR FASES

Cada fase termina con `tools/verify.py` verde (tests+lint+bench dentro de umbrales) y
entregas verificadas por QA. No se pasa de fase con criterios incumplidos (DoD del kit).

| Fase | Objetivo | Entregables clave | Criterios de salida |
|---|---|---|---|
| **F0 — Cimientos** | Control de versiones e higiene | `git init` + commit base; eliminar/ignorar residuos (A6); `tools/verify.py`; OWNERSHIP.md; `tasks/BOARD.md` | Historial limpio; verify.py verde; tablero operativo |
| **F1 — Refactor del orquestador** | Preparar crecimiento sin nuevas features | Extraer `sim/combat`, `sim/interact`, `sim/loot`, `sim/floor` desde `play.py`; enemigos data-driven (`enemies.json` + FSM genérica); play.py < 250 líneas | 112+ tests verdes; mismos benchmarks o mejores; contrato Inventory intacto |
| **F2 — Núcleo RPG** | Lo que convierte el slice en RPG | Multiplanta encadenada con temas; misiones (`quests.json`, `quest_system`); NPCs con A*+horarios; diálogo mínimo data-driven; crafting (`recipes.json`) | Partida 3 plantas completable; guardado/carga con misiones; A* p95 presupuesto |
| **F3 — Mundo grande** | Escala | Spatial hash; actualización selectiva (IA staggered); culling; mapas Tiled autorales vía PyTMX conviviendo con procedural; bench 100 entidades | p95 ≤ 16.67 ms @100 entidades y mapa 128×96 [umbral propuesto] |
| **F4 — Presentación y pulido** | Calidad perceptible | Lienzo virtual escalable; música OGG licenciada (registro en assets/); UI adaptable; balance con datos; multi-ranura de guardado | Resoluciones 16:9 variadas sin romper UI; licencias registradas |
| **F5 — Distribución** | Entrega | PyInstaller .exe; README de usuario; Smoke test del binario | El binario arranca y juega una partida completa en una máquina limpia |

---

# 12. BENCHMARK PARA EVALUAR A LOS AGENTES

Sobre la rúbrica existente (`benchmark/METRICS.md`: funcionalidad 25, integración 20,
calidad 15, autocorrección 15, rendimiento medido 15, autonomía 10 — se conserva):

**Suite de tareas estándar** (`benchmark/agent_tasks/`), diseñadas para comparar agentes
con contexto controlado:

| Tarea | Sistema objetivo | Qué mide | Verificación objetiva |
|---|---|---|---|
| T1: nuevo enemigo "espectro" SOLO con datos | `data/` | ¿respeta data-driven? | El diff no toca enemies.py; tests de catálogo pasan |
| T2: bug de inventario inyectado (stack overflow) | `sim/inventory` | Diagnóstico y regresión | Test de regresión añadido + explicación |
| T3: sistema de misiones mínimo | `sim/quest` | Contratos + pruebas | Contrato aprobado antes; cobertura de ramas |
| T4: optimizar separación de enemigos | `world/spatial` | Medir→optimizar→demostrar | p50/p95 antes/después en el informe |
| T5: migración de esquema de guardado v1→v2 | `persistence/` | Migraciones seguras | Fixture v1 carga; v1 corrupta → error claro |
| T6: pantalla de pausa con reasignación de teclas | `input/`,`ui/` | UI + contrato de acciones | Headless test del mapper; sin pygame en dominio |

**Procedimiento**: misma tarea, mismo contexto inicial (commit base), mismo presupuesto de
tiempo/ciclos; registrar todas las métricas de METRICS.md; publicar condiciones y limitaciones
(no comparar modelos sin controlar variables — regla vigente del kit).

---

# 13. RIESGOS TÉCNICOS

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Trabajo multiagente sin git → pérdida de trabajo/merge imposible | CIERTO hoy | CRÍTICO | F0 obligatorio antes de cualquier tarea (D2) |
| R2 | Techo de rendimiento de Python con cientos de entidades + IA | Media | Alto | Spatial hash + staggering + presupuestos; medir con bench; Pymunk/numpy solo si datos lo exigen |
| R3 | `play.py`/`enemies.py` como cuellos de botella de propiedad | Alta | Medio | F1: extracción a sim/ + data-driven (A2, A3) |
| R4 | Scope creep del RPG (misiones+diálogo+crafting a la vez) | Alta | Medio | Fases con DoD estricta; vertical por subsistema |
| R5 | Migraciones de guardado rotas al crecer el esquema | Media | Alto (usuarios) | T5 del benchmark; versión+fixtures desde F2 |
| R6 | Licencias de assets/música en F4 | Media | Legal | Registro obligatorio; default procedural (ADR-003) |
| R7 | Dependencias al declarar soporte multiplataforma sin probar | Media | Medio | Directriz vigente: no afirmar sin probar; CI local Windows + pruebas manuales Linux |
| R8 | Contenido data-driven mal validado → crashes en runtime | Media | Medio | Catálogos con validación estricta + tests por catálogo |
| R9 | Sobre-optimización prematura por parte de agentes | Media | Medio | Regla "medir antes" + revisión del integrador |
| R10 | Ventana fija → trabajo de UI desechado si se llega tarde a F4 | Baja | Medio | Definir lienzo virtual en contrato antes de F2 (barato ahora) |

---

# 14. DECISIONES QUE REQUIEREN APROBACIÓN DEL DIRECTOR

| # | Decisión | Opción recomendada | Alternativa descartada y por qué |
|---|---|---|---|
| **D1** | ¿Conservar "La Fragua Olvidada" v0.1.0 como base del RPG? | **Sí**: 112 tests reales, arquitectura verificada, persistencia segura. El coste de reempezar no tiene contrapartida. | Reescritura limpia: perdería valor verificado; ningún problema actual lo justifica |
| **D2** | Inicializar git y limpiar residuos (`_*.bat`, `install.log`, `_diag*`) | **Sí** (bloqueante: R1). Los residuos se archivan en `tasks/` o se borran con visto bueno. | Seguir sin git: inviable para multiagente |
| **D3** | Mantener Pygame CE (no migrar a Arcade) | **Sí** | Arcade 3.x: reescritura completa de render sin ventaja decisiva tile-based |
| **D4** | Física: tile-based propia; Pymunk solo con disparador definido | **Sí** (ADR-002 vigente) | Pymunk ahora: coste sin requisito |
| **D5** | A* propio presupuestado (no librería) | **Sí** | `pathfinding` pypi: objetos por celda, sin presupuesto por frame |
| **D6** | Contenido data-driven (enemigos/misiones/recetas/diálogos en JSON) | **Sí** (condición de escalabilidad multiagente) | Más código: cuellos de botella por archivo |
| **D7** | Fusionar roles: director+arquitecto; gráficos+audio; QA+integrador (6 roles) | **Sí** | 10 roles: coordinación > valor en subsistemas pequeños |
| **D8** | Adoptar Tiled+PyTMX en F3 para mapas autorales | **Sí**, con verificación de licencia del tag | LDtk: formato propio sin ventaja |
| **D9** | Migrar `systems/`→`sim/` y reducir `play.py` en F1 | **Sí** | Mantener play.py: riesgo de god-scene creciente |
| **D10** | Umbral de rendimiento como criterio de aceptación (p95 ≤ 16.67 ms @100 entidades en F3) | **Sí** (número a calibrar con datos reales en F2) | Sin umbral: regresiones silenciosas |
| **D11** | Suelo Python `>=3.11`, desarrollo en 3.12; no perseguir 3.13+ por rendimiento | **Sí** | Actualizar por moda: ganancias modestas/carga-dependiente |

---

## Anexo A — Comandos ejecutados y resultados (evidencia de auditoría)

```
python --version                         → Python 3.12.10
pip show pygame-ce                       → pygame-ce 2.5.8
python -m pytest -q                      → 112 passed in 37.68s
python -m game --headless --frames 60    → OK (exit 0)
python benchmark/bench_generation.py     → p50 17.14ms · p95 29.62ms · max 149.06ms
python benchmark/bench_simulation.py     → p50 9.17ms · media 12.57ms · p95 32.75ms · max 506.92ms
git status                               → fatal: not a git repository
grep -rn "import pygame" game/           → solo app, input, render/*, scenes/*
grep -rn "except.*pass|time.sleep" game/ → sin resultados
wc -l game/**/*.py                       → 5.392 líneas totales; play.py 564
```

## Anexo B — Fuentes web consultadas (verificación 2026-11-06)

- Pygame CE: pypi.org/project/pygame-ce · github.com/pygame-community/pygame-ce/releases ·
  pyga.me/posts/2025/11/performance-comparisons · pyga.me/docs/pygame-api-diffs
- Arcade: pypi.org/project/arcade · api.arcade.academy · github.com/pythonarcade/arcade
- Pymunk: pymunk.org/en/latest/changelog.html (7.2.0, 2025-11-02)
- python-tcod: python-tcod.readthedocs.io · rogueliketutorials.com · github.com/libtcod/python-tcod
- Tiled: mapeditor.org (1.12.2, may 2026) · LDtk: ldtk.io (1.5.3)
- PyTMX: github.com/bitcraft/pytmx (v3.31) · pyglet: pypi.org/project/pyglet (2.1.19)
- Pathfinding: github.com/brean/python-pathfinding
- Catálogo de repos de §6.2: verificación individual de existencia y licencia en GitHub/PyPI
  (The-Stolen-Crown-RPG, pyzelda-rpg, python-tcod, WFC, opensimplex, py_trees, bubbles,
  esper, YarnSpinner, renpy); fechas exactas de último commit no siempre visibles → marcadas.
- Python 3.12/3.13: python.org docs + benchmarks públicos (resumen en §2.5)

## Anexo C — Qué NO se hizo

- No se modificó ni eliminó ningún archivo del paquete original.
- No se implementó ningún sistema del juego (regla de la misión).
- No se ejecutaron pruebas gráficas con ventana real (solo headless/dummy); el juego
  completo con ventana NO ha sido jugado en esta auditoría — verificar en F0 con humano.
- Las licencias marcadas "verificar" no se han confirmado aún contra el texto legal del tag
  exacto; se hará antes de adoptar cada dependencia nueva.
