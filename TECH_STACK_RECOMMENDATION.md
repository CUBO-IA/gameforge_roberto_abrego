# GAMEFORGE 2D — RECOMENDACIÓN FORMAL DEL STACK TECNOLÓGICO

**Documento:** `TECH_STACK_RECOMMENDATION.md`  
**Rol:** Arquitecto Principal de GameForge 2D  
**Fecha:** 2026-11-06  
**Estado:** PROPUESTA TÉCNICA OFICIAL  
**Marco de referencia:** Directivas de `directives/01_GLOBAL.md` a `04_INTEGRATION.md`, Contratos de `architecture/CONTRACTS.md` y resultados de `REPOSITORY_RESEARCH.md`.

---

## 1. Visión y Principios del Stack

La arquitectura de GameForge 2D responde a un principio rector inmutable: **máxima estabilidad, determinismo, verificabilidad y simplicidad explícita sobre abstracciones prematuras**. 

El stack tecnológico no debe seleccionarse por modas, sino por su capacidad comprobada de sostener un juego RPG de acción en tiempo real a 60 FPS estables (presupuesto $\le 16.67$ ms por fotograma), ejecutable en modo headless sin entorno gráfico en servidores de integración continua (CI) y mantenible por un equipo de agentes de software coordinados.

---

## 2. Recomendaciones Tecnológicas por Subsistema

### 2.1 Lenguaje Principal: Python 3.11+ (CPython)
- **Decisión:** **Python 3.11+** como lenguaje obligatorio y exclusivo para la lógica del juego.
- **Justificación:**
  1. **Optimizaciones del Intérprete (Specializing Adaptive Interpreter - PEP 659):** A partir de Python 3.11 y consolidado en 3.12 y 3.14, el bytecode se especializa dinámicamente, acelerando bucles de simulación pura en un 25-40% respecto a Python 3.10.
  2. **Tipado Estricto Gradual:** Uso sistemático de `from __future__ import annotations` y tipado estático verificado por `ruff` y análisis de contratos.
  3. **Portabilidad y Testabilidad:** Permite ejecutar la suite completa de 179 pruebas unitarias en menos de 2.0 segundos sin pasos de compilación intermedia.
- **Entornos validados en el proyecto:** Python 3.12 y Python 3.14 (64-bit).

---

### 2.2 Framework Multimedia y Capa de Presentación: Pygame CE (Community Edition >= 2.5)
- **Decisión:** **`pygame-ce>=2.5`** como única dependencia externa de runtime.
- **Evaluación comparativa con alternativas:**
  - *vs. Pygame Legacy (2.1.x):* Pygame clásico sufre de estancamiento en releases, falta de tipado oficial `.pyi`, problemas con compilaciones en Python 3.12+ y ausencia de soporte nativo para `FRect` y rendering moderno SDL2.
  - *vs. Python Arcade (3.x):* Arcade es un excelente framework basado en OpenGL/Shaders, pero impone una arquitectura acoplada a contextos GPU, no permite pruebas headless puras en entornos sin servidor X11/mesa sin complejidad añadida, y exigiría reescribir por completo la capa de renderizado ya funcional.
  - *vs. python-tcod:* tcod está orientado al paradigma de terminal virtual / consola ASCII de roguelikes clásicos por turnos, no a la acción en tiempo real libre de 360 grados de GameForge 2D.
- **Aislamiento Arquitectónico:** Pygame CE se utiliza **únicamente en la frontera de presentación**:
  - `game/app.py`: Bucle principal y control de reloj.
  - `game/render/`: Dibujo de superficies, lienzo virtual, HUD y partículas.
  - `game/input/`: Captura de eventos de teclado/ratón y conversión a acciones abstractas.
  - `game/scenes/`: Orquestación de transición de vistas.
  *Ningún módulo de lógica, mundo, matemáticas, inventario o persistencia importa Pygame*.

---

### 2.3 Simulación Física y Resolución de Colisiones: Motor Propio Tile-Based ($O(1)$)
- **Decisión:** **Mantener y consolidar el motor propio** de colisiones (`game/world/collision.py` y `game/world/spatial.py`).
- **Descarte de Pymunk:**
  - Pymunk (envoltorio CFFI de Chipmunk 2D) introduce cuerpos rígidos con masa, inercia continua, uniones y torsión.
  - En un RPG top-down clásico, el movimiento de entidades es controlado cinemáticamente por vectores de velocidad directa, sin fricción rotacional ni fuerzas de gravedad.
  - Incorporar Pymunk añadiría sobrecarga de cruce CFFI, problemas de determinismo con números en coma flotante y una dependencia binaria innecesaria.
- **Características del Sistema Propio:**
  - Descomposición ortogonal de movimiento en ejes X e Y separados.
  - Algoritmo anti-tunneling con subdivisión de pasos si $\Delta > 4.0$ píxeles.
  - Partición espacial mediante **Spatial Hash** con celdas de 64×64 píxeles: reduce las comprobaciones de separación entre entidades de $O(N^2)$ a $O(N)$ amortizado.
  - Rendimiento verificado: simulación de 100 entidades simultáneas en $< 0.4$ ms por frame.

---

### 2.4 Arquitectura de Entidades: Catálogos Data-Driven vs. ECS Completo (Esper)
- **Decisión:** **Arquitectura Híbrida Data-Driven con Dataclasses Inmutables**.
- **Evaluación frente a Esper (ECS puro):**
  - Esper es una biblioteca ECS pura de alta calidad (~600 líneas, MIT), pero introducir un ECS completo en este punto fragmentaría el estado de las entidades en decenas de componentes desacoplados, multiplicando las llamadas de indirección y complicando el seguimiento de bugs en tareas multiagente.
  - Nuestro enfoque actual centraliza la configuración de entidades en `game/data/enemies.json`, deserializándola al arrancar en catálogos inmutables (`enemy_catalog.py`). La entidad tiene estado cinemático explícito y una máquina de estados finita (FSM) genérica.
- **Veredicto:** Mantener el modelo actual de entidades livianas. Estudiar los principios de Esper para componer sistemas auxiliares aislados (por ejemplo, efectos de estado como veneno, congelación o quemadura temporales).

---

### 2.5 Autoría y Generación de Mapas: Enfoque Híbrido (Tiled Map Editor + Generador Procedural BFS)
- **Decisión:** **Modelo Híbrido Dual**.
  1. **Niveles Narrativos y Fijos (Pueblos, Interiores, Arenas de Jefes):** Diseñados con **Tiled Map Editor** (herramienta visual externa).
     - Se exportan en formato estándar **Tiled JSON** (no TMX).
     - Se cargan mediante nuestro módulo nativo `game/world/tiled_loader.py` (sin depender de `pytmx`).
  2. **Mazmorras y Catacumbas (Exploración Infinita):** Generadas proceduralmente en código puro (`game/world/generation.py`).
     - Algoritmo de colocación de salas rectangulares no solapadas con corredores ortogonales.
     - Determinismo estricto basado en semilla (`random.Random(seed)`).
     - Validación topológica obligatoria mediante Flood Fill BFS: el generador descarta cualquier mapa donde el spawn, el altar o los cofres queden aislados por muros.
     - Rendimiento comprobado: generación y validación de una planta de 64×48 tiles en $\approx 2.2$ ms.

---

### 2.6 Inteligencia Artificial y Navegación: A\* Propio con Cuota de CPU y Caché LRU
- **Decisión:** **A\* Nativo en Python Puro con Cuota por Frame**.
- **Descarte de dependencias externas (`pathfinding`, `python-tcod`):**
  - La librería `pathfinding` de PyPI instancia nodos de cuadrícula como objetos de clase Python pesados, saturando la memoria y el garbage collector.
  - `python-tcod` requiere arrastrar el ecosistema completo de NumPy y librerías CFFI.
- **Especificaciones del A\* Propio (`game/ai/astar.py`):**
  - Implementación con `heapq` nativo y tuplas ligeras `(f_score, h_score, col, row)`.
  - Cuota máxima de CPU por frame (`budget_ms <= 1.5 ms`). Si se agota el tiempo, devuelve la mejor aproximación calculada.
  - Caché LRU basada en tuplas `(floor_id, target_tile)` para compartir caminos calculados hacia el jugador entre enemigos cercanos.

---

### 2.7 Persistencia de Datos: Arquitectura Dual (JSON Atómico + SQLite)
- **Decisión:** **Formato Dual según la Naturaleza del Dato (ADR-004 y ADR-008)**.
  1. **Partidas en Curso (Save Slots 1, 2 y 3):** Archivos **JSON con escritura atómica**.
     - Escritura en `.save.tmp` y sustitución atómica mediante `os.replace()`.
     - Versionado de esquema (`schema_version: 1`) con validación estructural completa al cargar.
     - Cero corrupción de partidas por cierre abrupto o interrupción de proceso.
  2. **Estadísticas de Partidas y Clasificación (Hall of Fame):** Base de datos **SQLite local** (`persistence/scores.py`).
     - Almacenamiento relacional de puntuación, tiempo de juego, enemigo abatido y resultado (victoria/derrota).
     - Consultas indexadas y ordenadas eficientes sin dependencias externas (SQLite viene en la biblioteca estándar de Python).

---

### 2.8 Resolución y Escalado Visual: Lienzo Virtual (Virtual Canvas 1280×720)
- **Decisión:** **Lienzo Virtual con Letterbox / Pillarbox Dinámico (`game/render/canvas.py`)**.
- **Justificación:**
  - El juego se renderiza siempre internamente a una resolución lógica fija de 1280×720 píxeles.
  - La capa del lienzo calcula automáticamente la relación de aspecto de la ventana física del usuario, escalando la imagen con aspecto perfecto y rellenando los bordes con bandas negras.
  - Función de transformación inversa `map_mouse_to_logical((x, y))`: la lógica del juego y las escenas reciben coordenadas normalizadas sin necesidad de saber a qué resolución física está jugando el usuario o si está en pantalla completa.

---

### 2.9 Herramientas de Desarrollo, Linting y Verificación (Dev & CI)
- **Gestor de Entorno y Paquetes:** **`uv`**. Gestión ultrarrápida de entornos virtuales y dependencias reproducibles mediante `uv.lock`.
- **Suite de Pruebas:** **`pytest >= 8`**. Pruebas deterministas, rápidas y modulares.
- **Linter y Formateador:** **`ruff >= 0.6`**. Análisis estático inmediato compatible con PEP 8 y reglas estrictas de imports y buenas prácticas.
- **Puerta de Calidad Única:** **`tools/verify.py`**. Script unificado que ejecuta linting, batería de 179+ tests y benchmarks de simulación en un solo comando.
- **Empaquetado y Distribución:** **`PyInstaller`** mediante especificación `gameforge.spec` y script `tools/build_dist.py`.

---

## 3. Matriz del Stack Oficial

| Subsistema | Tecnología Seleccionada | Tipo | Licencia | Estado |
|---|---|---|---|---|
| **Lenguaje Core** | Python 3.11+ (3.12 / 3.14) | Runtime | PSF | **Adoptado y validado** |
| **Multimedia y Display**| pygame-ce >= 2.5 | Dependencia PyPI | LGPL-2.1+ | **Adoptado y validado** |
| **Colisiones & Físicas** | Motor Propio + Spatial Hash | Interno (`game/world/`) | MIT (Proyecto) | **Adoptado y optimizado** |
| **Entidades & Datos** | Catálogos JSON + Dataclasses | Interno (`game/entities/`)| MIT (Proyecto) | **Adoptado y probado** |
| **Autoría de Mapas** | Tiled Map Editor (JSON format) | Herramienta Externa | Formato libre | **Adoptado (Loader propio)** |
| **Generación Procedural**| Generador BFS con semillas | Interno (`game/world/`) | MIT (Proyecto) | **Adoptado y verificado** |
| **Navegación IA** | A\* nativo cuotado + LRU | Interno (`game/ai/`) | MIT (Proyecto) | **Adoptado y verificado** |
| **Persistencia** | JSON Atómico + SQLite | Estándar Python | Estándar / Dominio público | **Adoptado y probado** |
| **Escalado de Pantalla** | Virtual Canvas 1280×720 | Interno (`game/render/`) | MIT (Proyecto) | **Adoptado y probado** |
| **Entorno & Bloqueo** | uv + uv.lock | Herramienta Dev | Apache-2.0 / MIT | **Adoptado y verificado** |
| **Testing & Lint** | pytest + ruff | Dependencias Dev | MIT | **Adoptado y verificado** |
| **Distribución** | PyInstaller (`gameforge.spec`)| Herramienta Dev | GPL / Apache (Output comercial libre)| **Adoptado y probado** |

---

## 4. Tecnologías Descartadas y Justificación Técnica

1. **`pymunk`:** Descartado para el bucle principal. Añade sobrecarga de CFFI y física de cuerpos rígidos que un RPG 2D en cuadrícula no necesita. Mantener como opción condicional exclusiva si en el futuro se diseñan mecánicas físicas avanzadas (ADR-002).
2. **`pytmx`:** Descartado. Nuestro loader nativo `game/world/tiled_loader.py` es más rápido, ligero, sin dependencias externas y evita la licencia restrictiva LGPLv3.
3. **`tilemap-generator`:** Descartado. Depende del ecosistema Node.js / JavaScript. Incompatible con nuestro runtime Python unificado.
4. **`python-tcod` (como librería):** Descartada la importación en runtime por arrastrar NumPy y dependencias CFFI de 40 MB. Se adoptan únicamente sus algoritmos puros (mapas de Dijkstra y Shadow Casting FOV).
5. **`py_trees`:** Descartado para el combate masivo a 60 FPS por sobrecarga de instanciación y recolección de basura. Se adopta la máquina de estados finitos (FSM) por arquetipos basada en datos.
6. **`Procedural-Maps`:** Descartado por infracción de licencia (repositorio sin licencia explícita, todos los derechos reservados). Se reimplementan los conceptos matemáticos (ruido multi-octava y matriz de biomas) en código limpio propio.
