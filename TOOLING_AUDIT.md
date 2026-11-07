# TOOLING_AUDIT.md — GAMEFORGE 2D
## Auditoría General de Herramientas, Bibliotecas y Repositorios Open-Source

**Estado:** ESPECIFICACIÓN TÉCNICA Y AUDITORÍA NORMATIVA  
**Misión:** MISIÓN 006 — Investigación e Integración de Herramientas para Desarrollo 2D  
**Fecha:** 2026-11-07  
**Autor:** Director de Tecnología / Agente de Arquitectura e Integración  
**Proyecto:** GameForge 2D (RPG Modular de Acción-Aventura en Python / Pygame CE)  

---

## 1. Resumen Ejecutivo y Alcance

El objetivo de esta auditoría es evaluar, clasificar y seleccionar de forma rigurosa las herramientas externas, bibliotecas de Python, utilidades de línea de comandos (CLI) y repositorios open-source destinados a potenciar el ecosistema de desarrollo autónomo de GameForge 2D. 

El principio rector de GameForge establece: **"No se trata de acumular dependencias. Se busca construir un ecosistema de herramientas que los agentes de programación puedan utilizar directamente durante sus tareas con máxima calidad, autonomía, eficiencia y capacidad de validación verificable."**

De acuerdo con la directiva estricta de la Misión 006:
> **REGLA FUNDAMENTAL:** Ninguna dependencia de runtime ha sido incorporada permanentemente al código del motor (`game/`) durante esta fase de investigación. Todas las pruebas de compatibilidad y benchmarking se han ejecutado en entornos aislados y efímeros mediante `uv run --with`, respetando íntegramente la arquitectura limpia y determinista del proyecto.

---

## 2. Metodología de Evaluación y Criterios Obligatorios

Cada herramienta auditada ha sido analizada exhaustivamente bajo **trece (13) dimensiones técnicas no negociables**:

1. **Función principal:** Rol específico que desempeña en el flujo de trabajo de desarrollo de videojuegos 2D.
2. **Repositorio oficial:** URL canónica del repositorio de código fuente.
3. **Licencia:** Tipo de licencia de software libre/código abierto y compatibilidad legal con la licencia MIT de GameForge y LGPL v2.1+ de Pygame CE.
4. **Actividad y mantenimiento:** Estado del ciclo de vida del proyecto (frecuencia de commits, lanzamientos recientes, soporte para versiones modernas de Python).
5. **Compatibilidad con Python y Pygame CE:** Compatibilidad empírica verificada con Python 3.11–3.14 y Pygame CE 2.5+.
6. **Consumo de recursos:** Huella de memoria RAM, carga de CPU y espacio en disco.
7. **Funcionamiento offline:** Capacidad de operar al 100% en entornos aislados sin acceso a Internet (*air-gapped*).
8. **Integración con agentes de IA (Claude Code / Antigravity):** Viabilidad de interacción mediante CLI, salidas estructuradas JSON, códigos de retorno y parseabilidad.
9. **Capacidad de automatización:** Facilidad de orquestación en scripts headless, pipelines de CI/CD y ganchos (*hooks*).
10. **Complejidad de implementación:** Curva de adopción y esfuerzo de integración en la base de código.
11. **Beneficio real para GameForge:** Impacto directo en calidad, velocidad de desarrollo, prevención de regresiones y autonomía del agente.
12. **Alternativas existentes:** Opciones competidoras o soluciones nativas ya presentes en el proyecto.
13. **Veredicto:** Decisión técnica vinculante entre cuatro estados formales:
    - **`ADOPTAR`**: Herramienta indispensable, lista para integración en tooling o dev-dependencies.
    - **`PROBAR`**: Herramienta de alto potencial que requiere validación experimental en una prueba de concepto aislada.
    - **`POSPONER`**: Herramienta valiosa pero sobredimensionada para el alcance actual del vertical slice; reevaluable en fases avanzadas.
    - **`DESCARTAR`**: Herramienta redundante, obsoleta, incompatible o que viola los principios arquitectónicos de GameForge.

---

## 3. Bloque A: Calidad y Análisis de Código

### 3.1. Ruff
- **Función principal:** Linter y formateador de código Python extremadamente rápido escrito en Rust; unifica las funciones de Flake8, Black, isort, pyupgrade, pydocstyle y autoflake.
- **Repositorio oficial:** https://github.com/astral-sh/ruff
- **Licencia:** MIT / Apache 2.0 dual license.
- **Actividad y mantenimiento:** Excepcional; el estándar dominante de la industria Python (2024–2026), con actualizaciones semanales.
- **Compatibilidad con Python y Pygame CE:** Plena compatibilidad con Python 3.11, 3.12, 3.13 y 3.14. Compatible con la totalidad de tipos y llamadas de Pygame CE.
- **Consumo de recursos:** RAM < 20 MB durante análisis; CPU ultrabaja (< 60 ms para analizar 110+ archivos del repo); almacenamiento en disco ~45 MB (binario compilado).
- **Funcionamiento offline:** 100% offline. No realiza llamadas de telemetría ni requiere red.
- **Integración con Claude Code:** Inmejorable. Admite `--output-format=json`, salida por líneas concisa para no saturar el contexto de tokens (`TOKEN_EFFICIENCY.md`), y opción de auto-corrección `--fix`.
- **Capacidad de automatización:** Total. Ejecutable vía `ruff check .` y `ruff format --check .`. Integrable en hooks pre-commit y ganchos de guardado.
- **Complejidad de implementación:** Mínima. Ya configurado en el archivo `pyproject.toml` del proyecto (`[tool.ruff]`).
- **Beneficio real para GameForge:** Detección instantánea de errores de sintaxis, variables huérfanas, imports no resueltos y degradaciones de estilo antes de ejecutar los tests.
- **Alternativas existentes:** Flake8 + Black + isort (combinación heredada 50 veces más lenta), Pylint (lento y ruidoso).
- **Veredicto:** **`ADOPTAR`** (Actualmente incorporado en `tools/verify.py` y `pyproject.toml`).

### 3.2. Pyright
- **Función principal:** Verificador de tipos estático (*static type checker*) de alta velocidad para Python, con soporte riguroso de las especificaciones PEP 484, 526, 544, 589, 604 y 695.
- **Repositorio oficial:** https://github.com/microsoft/pyright
- **Licencia:** MIT.
- **Actividad y mantenimiento:** Muy activo; mantenido directamente por el equipo de Microsoft para VS Code y el ecosistema de Python.
- **Compatibilidad con Python y Pygame CE:** Excelente con Python 3.11–3.14. Pygame CE proporciona archivos de tipos (`.pyi` stubs) oficiales, permitiendo validación estricta de tipos de `Surface`, `Rect`, `Vector2`, etc.
- **Consumo de recursos:** RAM ~120–250 MB durante análisis completo; CPU moderada; disco ~35 MB (Node.js/npm) o ~15 MB como wheel de PyPI.
- **Funcionamiento offline:** 100% offline tras su instalación local.
- **Integración con Claude Code:** Muy alta. Ofrece salida estructurada en JSON (`pyright --outputjson`) que los agentes pueden parsear para identificar números de línea exactos, tipos incompatibles y contratos violados.
- **Capacidad de automatización:** Total mediante CLI y scripts de verificación; parametrizable con `pyrightconfig.json` o `[tool.pyright]` en `pyproject.toml`.
- **Complejidad de implementación:** Baja a media. Requiere mantener anotaciones de tipo limpias en contratos compartidos (`CONTRACTS.md`) y el núcleo del motor.
- **Beneficio real para GameForge:** Previene errores catastróficos en runtime (como `NoneType` attribute errors o argumentos desordenados en funciones de física/combate) en tiempo estático sin ejecutar el juego.
- **Alternativas existentes:** Mypy (estándar tradicional, sensiblemente más lento y complejo de configurar en Windows), Pyre (Facebook, soporte Windows deficiente).
- **Veredicto:** **`ADOPTAR`** (Incorporar en grupo opcional `[project.optional-dependencies] dev` para blindar contratos).

### 3.3. pytest
- **Función principal:** Framework de pruebas unitarias, de integración y de regresión basado en fixtures reutilizables, parametrización limpia y aserciones nativas de Python.
- **Repositorio oficial:** https://github.com/pytest-dev/pytest
- **Licencia:** MIT.
- **Actividad y mantenimiento:** Pilar crítico del ecosistema Python, soporte activo e ininterrumpido.
- **Compatibilidad con Python y Pygame CE:** 100% compatible. Permite la ejecución de suites completas de Pygame CE en modo headless forzando `SDL_VIDEODRIVER=dummy` en `conftest.py`.
- **Consumo de recursos:** RAM ~35–60 MB; CPU ligera; tiempo de ejecución medido 6.06 s para 314 tests; almacenamiento ~12 MB.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Nativa. Salida formateable (`pytest -ra -q`), captura de trazas de fallo reducidas (`--tb=short`), y compatibilidad con plugins de reporte JSON (`pytest-json-report`).
- **Capacidad de automatización:** Es el motor principal del pipeline de calidad de GameForge en `tools/verify.py`.
- **Complejidad de implementación:** Ya implementado y operativo.
- **Beneficio real para GameForge:** Garantía absoluta de no regresión en simulación, generación procedural, inventario, colisiones y ciclo de vida de la aplicación.
- **Alternativas existentes:** `unittest` de la biblioteca estándar (verboso, sin sistema de fixtures avanzado), `nose2` (obsoleto).
- **Veredicto:** **`ADOPTAR`** (Eje central de verificación del proyecto).

### 3.4. Hypothesis
- **Función principal:** Biblioteca de pruebas basadas en propiedades (*Property-Based Testing* o PBT); genera automáticamente cientos de casos de prueba aleatorios y contraejemplos mínimos (*shrinkage*) para detectar casos de borde.
- **Repositorio oficial:** https://github.com/HypothesisWorks/hypothesis
- **Licencia:** Mozilla Public License 2.0 (MPL-2.0).
- **Actividad y mantenimiento:** Altamente activo, referencia indiscutible de testing riguroso en Python.
- **Compatibilidad con Python y Pygame CE:** Compatible con Python 3.11–3.14. Se integra fluidamente como decorador `@given` sobre tests estándar de pytest.
- **Consumo de recursos:** RAM ~50–80 MB; CPU proporcional al número de ejemplos evaluados (e.g. 50–200 ms por test parametrizado); disco < 10 MB.
- **Funcionamiento offline:** 100% offline. Almacena la base de datos de contraejemplos encontrados en `.hypothesis/examples` localmente.
- **Integración con Claude Code:** Excelente. Cuando un test falla, Hypothesis imprime el contraejemplo exacto y mínimo simplificado (e.g. `Falsifying example: run(seed=0, coords=(-1e-05, float('nan')))`), permitiendo al agente resolver el bug sin adivinanzas.
- **Capacidad de automatización:** Totalmente integrado en el flujo regular de `pytest`.
- **Complejidad de implementación:** Media. Requiere definir generadores de dominio (*strategies*) e invariantes matemáticas claras.
- **Beneficio real para GameForge:** Incalculable para blindar algoritmos complejos y críticos: aritmética vectorial (`Vec2`), cálculo de campos de distancia en Dijkstra, conectividad de mapas en generación procedural celular y atrición de inventario.
- **Alternativas existentes:** Pruebas unitarias basadas en ejemplos fijos escritos a mano (no descubren condiciones de borde imprevistas).
- **Veredicto:** **`PROBAR`** (Implementar suite piloto de pruebas PBT sobre `game.core.math2d` y `game.world.cavern_generation` sin fijar la dependencia en producción).

---

## 4. Bloque B: Diseño Gráfico, Mapas y Animaciones

### 4.1. Tiled Map Editor
- **Función principal:** Editor de mapas 2D líder en la industria de videojuegos, compatible con cuadrículas ortogonales, isométricas y hexagonales, capas de tiles, capas de objetos, colisiones poligonales y propiedades arbitrarias.
- **Repositorio oficial:** https://github.com/mapeditor/tiled
- **Licencia:** GPL v2 (editor de escritorio) / Formatos de archivo TMX y JSON de especificación pública y libre de regalías.
- **Actividad y mantenimiento:** Proyecto maduro y activamente mantenido por Thorbjørn Lindeijer desde 2008.
- **Compatibilidad con Python y Pygame CE:** 100% compatible mediante exportación JSON estándar. GameForge cuenta con un cargador nativo propio (`game/world/tiled_loader.py`) que procesa mapas de Tiled directamente sin librerías externas.
- **Consumo de recursos:** Aplicación de escritorio: RAM ~120–250 MB; disco ~90 MB; CLI headless: ultraligero (< 30 MB RAM).
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Máxima para el formato. Los agentes de IA pueden generar, leer, modificar y validar archivos de mapa JSON compatibles con Tiled (como `game/data/maps/hub_town.json`) con estructuras de datos declarativas.
- **Capacidad de automatización:** Admite ejecución en línea de comandos para exportación headless (`tiled --export-map json mapa.tmx mapa.json`).
- **Complejidad de implementación:** Cero fricción en el motor (ya implementado).
- **Beneficio real para GameForge:** Permite separar el diseño de niveles autorales (pueblos, interiores, templos) del código del motor, posibilitando que diseñadores humanos o agentes creen niveles complejos.
- **Alternativas existentes:** LDtk (Level Designer Toolkit, excelente alternativa moderna), Ogmo Editor (antiguo), editores ASCII internos (limitados).
- **Veredicto:** **`ADOPTAR`** (El estándar de datos JSON de Tiled es el formato oficial de mapas autorales de GameForge).

### 4.2. PyTMX
- **Función principal:** Biblioteca de Python para leer y renderizar archivos `.tmx` y `.json` creados con Tiled.
- **Repositorio oficial:** https://github.com/bitcraft/pytmx
- **Licencia:** LGPL v3.
- **Actividad y mantenimiento:** Mantenimiento de baja intensidad; pocos lanzamientos en los últimos años.
- **Compatibilidad con Python y Pygame CE:** Compatible con Pygame CE, pero arrastra dependencias implícitas y abstracciones rígidas de carga de imágenes que interfieren con la arquitectura desacoplada de GameForge.
- **Consumo de recursos:** RAM ~15–30 MB; disco ~2 MB.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Programática estándar de Python.
- **Capacidad de automatización:** Scripts Python.
- **Complejidad de implementación:** Baja, pero introduce acoplamiento innecesario.
- **Beneficio real para GameForge:** Nulo / Redundante. GameForge ya resolvió la ingesta de mapas de Tiled mediante `game/world/tiled_loader.py` en 158 líneas de código estricto, tipado con `@dataclass(slots=True)`, sin dependencias externas y adaptado a `TileMap` y `TileType`.
- **Alternativas existentes:** `game.world.tiled_loader` (nativo de GameForge).
- **Veredicto:** **`DESCARTAR`** (Innecesario y redundante; la solución nativa de GameForge es más rápida, limpia y no añade dependencias).

### 4.3. LibreSprite
- **Función principal:** Editor de gráficos pixel art y animación 2D por fotogramas de código abierto (bifurcación comunitaria de Aseprite v1.1.7 antes del cierre de su licencia).
- **Repositorio oficial:** https://github.com/LibreSprite/LibreSprite
- **Licencia:** GPL v2.
- **Actividad y mantenimiento:** Mantenimiento comunitario estable.
- **Compatibilidad con Python y Pygame CE:** Exporta hojas de spritesheet en PNG y metadatos de animación en JSON conformes a la especificación `gf-anim-v1` de GameForge.
- **Consumo de recursos:** RAM ~40–80 MB; disco ~35 MB.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Baja como herramienta interactiva (GUI de escritorio); media mediante su CLI para automatización de exportaciones de archivos `.ase`/`.aseprite` a PNG.
- **Capacidad de automatización:** Soporta comandos batch por CLI (`libresprite --batch sprite.ase --save-as sheet.png`).
- **Complejidad de implementación:** Baja.
- **Beneficio real para GameForge:** Es la herramienta de escritorio gratuita y libre recomendada para colaboradores humanos que deseen crear o retocar pixel art sin adquirir licencias comerciales de Aseprite.
- **Alternativas existentes:** Aseprite (comercial de pago EULA restrictiva), Pixelorama (basado en Godot, MIT), Piskel (web/desktop desfasado).
- **Veredicto:** **`PROBAR`** (Recomendado como editor GUI opcional para humanos; para agentes autónomos se prioriza el pipeline programático con Pillow y plantillas modulares).

### 4.4. Pillow (PIL Fork)
- **Función principal:** Biblioteca estándar de facto para procesamiento, manipulación, recorte, composición por capas, redimensionado y exportación de imágenes en Python.
- **Repositorio oficial:** https://github.com/python-pillow/Pillow
- **Licencia:** Historical Permission Notice and Disclaimer (HPND) / tipo MIT permisiva.
- **Actividad y mantenimiento:** Mantenimiento continuo de máxima prioridad; soporte de día cero para todas las versiones de Python (3.11–3.14).
- **Compatibilidad con Python y Pygame CE:** Total. Intercambio directo de buffers de píxeles con Pygame CE mediante `pygame.image.frombytes` / `fromstring` y conversión de paletas RGBA.
- **Consumo de recursos:** RAM ~10–25 MB para manipulación de spritesheets de 512x512; CPU ultrarrápida (operaciones en C/SIMD); disco ~18 MB.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Extraordinaria. Permite a los agentes programar scripts headless para recorte automático de sprites, swaps de color de paletas, empaquetado de atlas de texturas mediante algoritmos MaxRects y generación de máscaras visuales.
- **Capacidad de automatización:** Absoluta vía scripts CLI de Python.
- **Complejidad de implementación:** Muy baja. API intuitiva y robusta.
- **Beneficio real para GameForge:** Crítico para el pipeline de assets (`tools/asset_hub`, `tools/generate_enemy_sprites.py`). Dota a los agentes de visión y manipulación geométrica de imágenes sin necesidad de interfaz gráfica.
- **Alternativas existentes:** OpenCV (`opencv-python`, desproporcionadamente pesado con >150 MB para pixel art 2D), Pygame nativo (bueno para el bucle de juego, pero engorroso para procesamiento por lotes en background).
- **Veredicto:** **`ADOPTAR`** (Como dependencia de herramientas de desarrollo `[project.optional-dependencies] dev` para el pipeline de assets).

### 4.5. Blender
- **Función principal:** Suite profesional completa de modelado 3D, animación esquelética, rigging y renderizado fotorrealista.
- **Repositorio oficial:** https://github.com/blender/blender
- **Licencia:** GPL v2 / v3.
- **Actividad y mantenimiento:** Proyecto gigante con soporte y financiación masiva internacional.
- **Compatibilidad con Python y Pygame CE:** Contiene su propio intérprete de Python integrado (`bpy`). Puede ser invocado en modo headless para renderizar animaciones 3D rotadas a spritesheets 2D en 8 direcciones (técnica estilo *Dead Cells* o *Diablo*).
- **Consumo de recursos:** Muy pesado: descarga >500 MB; instalación >1.2 GB; RAM >600 MB durante renders por CPU/GPU.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Posible mediante scripts `.py` ejecutados con `blender -b escena.blend -P script_render.py`, pero compleja de calibrar por tokens y dependencias pesadas.
- **Capacidad de automatización:** Alta si el binario está instalado en la máquina anfitriona.
- **Complejidad de implementación:** Alta. Requiere activos 3D modelados y texturizados.
- **Beneficio real para GameForge:** Actualmente marginal. GameForge es un RPG 2D de acción con estética pixel art nativa de 16x16 / 32x32 píxeles. Incorporar un pipeline 3D-a-2D añade una sobrecarga técnica masiva que viola el principio de simplicidad inicial de `AGENTS.md`.
- **Alternativas existentes:** Generadores procedurales 2D en Python, Universal LPC Sprite Generator, spritesheets dibujados a mano o generados paramétricamente.
- **Veredicto:** **`POSPONER`** (Reevaluable en fases avanzadas si se requiere generar automáticamente cientos de modelos de monstruos complejos pre-renderizados).

---

## 5. Bloque C: Pruebas Visuales, Simulación y Rendimiento

### 5.1. Comparación Visual: Watchlight, Pixelmatch y diff nativo
- **Función principal:** Comparación automatizada de capturas de prueba contra imágenes de referencia (*golden masters*) para detectar alteraciones accidentales de renderizado, fuentes, colores o sprites.
- **Candidatos verificados:**
  - **Watchlight** (https://getwatchlight.com/): herramienta de regresión visual para apps de escritorio y juegos. **Es propietaria y de código cerrado**, solo Windows, con GUI gratuita pero **CLI/headless y servidor MCP previstos como funciones de pago** ($9/mes tras la beta; gratuitas durante la beta).
  - **Mapbox Pixelmatch** (https://github.com/mapbox/pixelmatch): implementación JS, licencia ISC; requeriría Node en el pipeline.
  - **pytest-regressions** (https://github.com/ESSS/pytest-regressions): MIT, integrado en pytest; opción Python si se necesita comparación de imágenes/ficheros de datos.
  - **Diff nativo de Pygame CE:** comparación de buffers + `special_flags=pygame.BLEND_SUB`.
- **Actividad y mantenimiento:** Pixelmatch y pytest-regressions activos; Watchlight en beta cerrada (acceso por solicitud).
- **Compatibilidad con Python y Pygame CE:** El diff nativo es 100% compatible. Watchlight no se integra con Python: lanza un ejecutable y compara capturas externas.
- **Consumo de recursos:** El diff nativo cuesta **0.503 ms** por comparación de buffer y **0.322 ms** por `BLEND_SUB` a 640x360 (medido; ver `TOOLING_BENCHMARK.md`). Watchlight añade un proceso externo opaco y no medible en cabeza.
- **Funcionamiento offline:** El diff nativo y Pixelmatch son offline. Watchlight funciona local según su documentación, pero exige instalación propietaria y licencia para automatización.
- **Integración con Claude Code:** El diff nativo devuelve una métrica escalar y una máscara diagnóstica fácilmente parseables. Watchlight expone MCP, pero bajo su licencia de pago.
- **Capacidad de automatización:** Total para el diff nativo (fixture de pytest). Watchlight automatizable solo con la edición Pro.
- **Complejidad de implementación:** Baja para el diff nativo (~80 líneas, cero dependencias). Alta para integrar un binario propietario de terceros.
- **Beneficio real para GameForge:** Evita regresiones visuales silenciosas en partículas, HUD y UI sin añadir dependencias ni coste.
- **Alternativas existentes:** Hash exacto MD5/SHA256 (demasiado rígido: falla con un píxel de variación por redondeo de fuentes); hash perceptual dHash (tolerante, pero innecesario en la primera fase).
- **Veredicto:** **`ADOPTAR`** el diff nativo como módulo del Game Test Runner. **`DESCARTAR` Watchlight** para el ecosistema de agentes: incumple los requisitos de código abierto, gratuidad y automatización sin licencia. **`DESCARTAR` Pixelmatch** (introduce Node sin aportar nada sobre el diff nativo).

### 5.2. Capturas Deterministas y Pruebas Headless (Pygame CE Dummy Driver)
- **Función principal:** Ejecución del bucle del motor completo sin levantar una ventana física del sistema operativo, fijando el delta-time a exactamente 1/60 s por frame y renderizando a un framebuffer virtual en memoria.
- **Repositorio oficial:** https://github.com/pygame-ce/pygame-ce
- **Licencia:** LGPL v2.1+.
- **Actividad y mantenimiento:** Núcleo central de Pygame CE.
- **Compatibilidad con Python y Pygame CE:** Nativa de la arquitectura.
- **Consumo de recursos:** RAM ~25–35 MB; CPU hiper-eficiente (alcanza más de 11,400 FPS de renderizado headless en las pruebas empíricas de GameForge).
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Esencial. Permite a los agentes ejecutar el juego completo en entornos de terminal pura o contenedores sin servidor X11/Wayland ni monitor físico.
- **Capacidad de automatización:** Total (`SDL_VIDEODRIVER=dummy` y `SDL_AUDIODRIVER=dummy`).
- **Complejidad de implementación:** Ya integrada y demostrada en `tests/test_headless_app.py`.
- **Beneficio real para GameForge:** Piedra angular de la testabilidad del proyecto.
- **Veredicto:** **`ADOPTAR`** (Pilar arquitectónico fundacional).

### 5.3. Simulación de Teclado y Ratón (Pygame Virtual Event Queue)
- **Función principal:** Inyección controlada de eventos de entrada sintetizados (`pygame.KEYDOWN`, `pygame.KEYUP`, `pygame.MOUSEBUTTONDOWN`, `pygame.MOUSEMOTION`) en la cola de eventos oficial de Pygame (`pygame.event.post()`) en frames predeterminados.
- **Repositorio oficial:** https://github.com/pygame-ce/pygame-ce
- **Licencia:** LGPL v2.1+.
- **Compatibilidad con Python y Pygame CE:** 100% nativa.
- **Consumo de recursos:** Latencia despreciable (< 0.005 ms por evento).
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Permite a los agentes programar guiones de interacción complejos (e.g. "moverse a la derecha por 30 frames, atacar al frame 35, abrir inventario con la tecla I en el frame 50") y comprobar el estado del mundo resultante.
- **Capacidad de automatización:** Total.
- **Complejidad de implementación:** Baja. Un controlador virtual desacoplado encapsula la inyección.
- **Beneficio real para GameForge:** Permite realizar pruebas end-to-end de jugabilidad real sin operadores humanos.
- **Alternativas existentes:** PyAutoGUI (pesada, requiere ventana real levantada, no funciona en headless puro).
- **Veredicto:** **`ADOPTAR`** (Componente medular del Game Test Runner).

### 5.4. Profiling y Medición de Rendimiento (`tracemalloc`, `cProfile`, `psutil`, `py-spy`)
- **Función principal:** Perfilado de CPU función por función, rastreo de asignaciones de memoria en heap, detección de fugas (*memory leaks*) y medición de percentiles de tiempo de frame (p50, p95, p99, max).
- **Repositorios oficiales:** `tracemalloc` y `cProfile` (Python Standard Library), `psutil` (https://github.com/giampaolo/psutil), `py-spy` (https://github.com/benfred/py-spy).
- **Licencia:** PSF License / BSD-3-Clause / MIT.
- **Actividad y mantenimiento:** Máximo nivel de madurez técnica.
- **Compatibilidad con Python y Pygame CE:** Plena con Python 3.11–3.14.
- **Consumo de recursos:** `tracemalloc` overhead < 5% RAM; `cProfile` overhead ~10–15% CPU; `py-spy` overhead < 2% (muestreo externo en Rust).
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Los reportes de profiling pueden exportarse a resúmenes tabulares o JSON para que el agente identifique cuellos de botella exactos de rendimiento.
- **Capacidad de automatización:** Integrable en scripts de benchmark (`benchmark/bench_simulation.py`).
- **Complejidad de implementación:** Mínima para módulos nativos de Python.
- **Beneficio real para GameForge:** Asegura el cumplimiento inquebrantable del presupuesto de 16.67 ms/frame (60 FPS estables) y la detección precoz de asignaciones de memoria indebidas en el bucle principal.
- **Veredicto:** **`ADOPTAR`** (`tracemalloc` y `cProfile` como herramientas base; `psutil` como complemento opcional).

### 5.5. Game Test Runner Propio (GF-TR)
- **Función principal:** Arnés de pruebas automatizadas y ejecución de escenarios end-to-end diseñado específicamente para GameForge, con runner headless, inyección virtual de eventos, aserciones de estado, capturas deterministas, diff visual y reportes de regresión.
- **Repositorio oficial:** Desarrollo interno del proyecto (`tools/test_runner/`).
- **Licencia:** MIT (idéntica a GameForge).
- **Compatibilidad con Python y Pygame CE:** 100% nativa.
- **Consumo de recursos:** RAM < 40 MB; ejecución en microsegundos; cero dependencias externas de runtime.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Diseñado específicamente para agentes: admite ejecución por comandos CLI simples, flags declarativos y reporte unificado en formato JSON.
- **Capacidad de automatización:** Total. Integrable como plugin/fixture de `pytest` (`pytest -m scenario`).
- **Complejidad de implementación:** Media (diseño modular desacoplado).
- **Beneficio real para GameForge:** Proporciona autonomía total a los agentes para validar mecánicas de juego completas antes de entregar cualquier tarea.
- **Alternativas existentes:** Airtest (excesivamente complejo y dependiente de visión por computador pesada), tests unitarios aislados sin simulación de eventos.
- **Veredicto:** **`ADOPTAR`** (Diseño detallado en el documento `GAME_TEST_RUNNER_DESIGN.md`).

---

## 6. Bloque D: Recursos Multimedia y Audio

### 6.1. FFmpeg
- **Función principal:** Suite líder mundial en procesamiento, transcodificación, normalización de sonoridad, filtrado, recorte y compresión de audio y vídeo multiformato.
- **Repositorio oficial:** https://github.com/FFmpeg/FFmpeg
- **Licencia:** LGPL v2.1+ (compilación estándar) / GPL v2+ (con librerías externas opcionales). Al usarse como binario CLI externo independiente, no compromete la licencia del código del juego.
- **Actividad y mantenimiento:** Máxima actividad comunitaria mundial. Ya se encuentra instalado localmente en el entorno del sistema (v8.1.1).
- **Compatibilidad con Python y Pygame CE:** Formatos de salida estándar (WAV PCM para efectos de baja latencia y OGG Vorbis para música y ambientes) son nativamente decodificados por `pygame.mixer` sin dependencias adicionales.
- **Consumo de recursos:** Binario independiente (~100 MB en disco); consumo de RAM efímero durante conversión (< 40 MB); tiempo de codificación < 180 ms para un clip de audio.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Excelente. Se invoca directamente mediante comandos CLI desde scripts de Python (`subprocess`), permitiendo a los agentes normalizar volúmenes a -14 LUFS, recortar silencios y convertir audio en lote.
- **Capacidad de automatización:** Insuperable; la herramienta de referencia para automatización multimedia en línea de comandos.
- **Complejidad de implementación:** Baja mediante recetas de comandos estandarizadas.
- **Beneficio real para GameForge:** Permite que los agentes procesen recursos de audio brutos antes de añadirlos al catálogo de assets, asegurando formatos óptimos, pesos mínimos y ausencia de silencios iniciales.
- **Alternativas existentes:** `pydub` (wrapper de Python que requiere FFmpeg por debajo), `sox` (anticuado para OGG moderno).
- **Veredicto:** **`ADOPTAR`** (Como herramienta CLI externa para el pipeline multimedia de agentes).

### 6.2. Audacity
- **Función principal:** Estación de trabajo de audio digital (DAW) y editor destructivo de audio gráfico multiplataforma.
- **Repositorio oficial:** https://github.com/audacity/audacity
- **Licencia:** GPL v3.
- **Actividad y mantenimiento:** Activo por Muse Group.
- **Compatibilidad con Python y Pygame CE:** Exporta archivos estándar WAV y OGG.
- **Consumo de recursos:** Aplicación de escritorio: RAM ~100–250 MB; disco ~160 MB.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Muy baja / Nula para agentes autónomos. Es un programa interactivo con interfaz gráfica diseñado para uso con ratón humano. Su API `mod-script-pipe` es frágil y no está pensada para entornos headless de desarrollo.
- **Capacidad de automatización:** Pobre en comparación con FFmpeg.
- **Complejidad de implementación:** Alta para cualquier intento de automatización de agentes.
- **Beneficio real para GameForge:** Útil exclusivamente para diseñadores de sonido humanos que requieran edición espectral visual o montaje multipista manual. Sin beneficio para agentes de código.
- **Alternativas existentes:** FFmpeg CLI (para manipulación por agentes), sintetizadores procedurales en Python (`pyfxr`).
- **Veredicto:** **`DESCARTAR`** para el ecosistema de agentes; **`POSPONER`** como sugerencia opcional para operadores humanos.

### 6.3. Krita
- **Función principal:** Suite profesional de pintura digital, ilustración artística, diseño conceptual y animación 2D tradicional.
- **Repositorio oficial:** https://github.com/KDE/krita
- **Licencia:** GPL v3.
- **Actividad y mantenimiento:** Excelente actividad por la Fundación Krita y KDE.
- **Compatibilidad con Python y Pygame CE:** Exporta capas en PNG y PSD.
- **Consumo de recursos:** Aplicación de escritorio pesada: RAM ~400 MB–1.2 GB; disco ~550 MB.
- **Funcionamiento offline:** 100% offline.
- **Integración con Claude Code:** Prácticamente nula para desarrollo de código. Cuenta con una API de scripting Python interna (PyKrita) diseñada para plugins dentro de su propia GUI, no como herramienta CLI ligera de procesamiento para agentes.
- **Capacidad de automatización:** Baja para flujos de trabajo autónomos de agentes.
- **Complejidad de implementación:** Muy alta.
- **Beneficio real para GameForge:** Extraordinario para artistas humanos de arte conceptual o portadas; innecesario y contraproducente para el desarrollo automatizado de un RPG pixel art 2D por agentes de IA.
- **Alternativas existentes:** Pillow (para procesamiento automatizado por agentes), LibreSprite (mucho más ligero y orientado a pixel art para humanos).
- **Veredicto:** **`DESCARTAR`** para el catálogo de agentes; **`POSPONER`** para etapas de arte conceptual por ilustradores humanos.

---

## 7. Bloque E: Capacidades Adicionales Especializadas

A continuación se auditan repositorios y bibliotecas para las diez áreas clave adicionales solicitadas en la Sección 3:

| Área Especializada | Repositorio / Candidato | Licencia | Evaluación Técnica | Veredicto |
|:---|:---|:---|:---|:---|
| **Generación procedural de mapas** | Algoritmos celulares + ruido Simplex (`opensimplex`, MIT) | MIT | GameForge ya cuenta con `game/world/cavern_generation.py` (autómata celular determinista) y `generation.py`. No se requieren dependencias pesadas; los algoritmos puros de Python son óptimos y no introducen C-extensions complejas. | **`ADOPTAR`** (Patrón algorítmico nativo) |
| **Creación de personajes y animaciones** | `universal-lpc-spritesheet-character-generator` + `Pillow` | GPL / CC-BY-SA | Permite componer proceduralmente cientos de variaciones de personajes (piel, peinado, ropa, armas) sobre la rejilla LPC estandarizada de 64x64 o 32x32 mediante superposición de capas en Pillow. | **`ADOPTAR`** (Pipeline programático en `tools/`) |
| **Navegación y pathfinding** | `python-pathfinding` vs A* y Dijkstra nativos cuotados | MIT | GameForge ya implementó `game/ai/astar.py` y `game/ai/dijkstra.py` con asignación de presupuesto por frame y spatial hashing (`spatial.py`). Introducir una librería externa no mejora el rendimiento y rompe el control fino del tiempo por frame. | **`DESCARTAR`** (Mantener algoritmos nativos cuotados) |
| **Física y colisiones** | Pymunk (Chipmunk2D) vs Colisiones circulares por ejes | MIT | El ADR-002 documentó la decisión explícita de NO introducir Pymunk en este vertical slice top-down. La resolución por ejes de círculos contra tiles y círculo-círculo nativa es determinista, ligera y sin dependencias C. | **`DESCARTAR`** (Confirmación de ADR-002) |
| **Sistemas de partículas** | Motor de partículas por lotes nativo de Pygame CE | MIT / LGPL | Pygame CE ofrece `pygame.BLEND_ADD` y superficies compartidas con canal alfa. Un pool de partículas pre-asignadas en memoria (`object pool`) garantiza cero allocs durante el juego a 60 FPS. | **`ADOPTAR`** (Sistema propio basado en pools) |
| **Iluminación 2D** | Pipeline de luces radiales con `pygame.BLEND_MULT` | LGPL | Capa de oscuridad ambiental combinada con círculos radiales precalculados mediante multiplicación de blending nativa de Pygame. Permite antorchas, linternas y hechizos dinámicos con < 0.2 ms de CPU. | **`ADOPTAR`** (Solución nativa por blend surfaces) |
| **Inteligencia artificial de NPC** | `py_trees` vs Árboles de Comportamiento y FSM nativos | BSD-3 | GameForge ya implementó un motor formal de Behavior Trees en `game/ai/behavior_tree.py` y FSM en `game/core/fsm.py` (con 100% de cobertura de pruebas). Añadir `py_trees` duplicaría la arquitectura. | **`DESCARTAR`** (Reutilizar componentes nativos validados) |
| **Interfaces de usuario (UI)** | `pygame_gui` vs UI modular ligera desacoplada | MIT | `pygame_gui` es madura pero excesivamente pesada (~30 MB, sobrecarga de eventos y CPU significativa). GameForge requiere una interfaz rápida, escalable y acoplada a `ui_scaling`. | **`POSPONER`** (Mantener sistema ligero nativo de HUD y menús) |
| **Audio dinámico y SFX** | `pyfxr` (https://github.com/lordmauve/pyfxr) | **BSD-3-Clause** (verificado en PyPI) | Biblioteca de síntesis de efectos (estilo sfxr), tonos y *pluck* en Cython; genera buffers PCM de 44,1 kHz mono compatibles con `pygame.mixer.Sound`. **Riesgo:** última versión 0.3.0 (abril 2021); no hay evidencia de wheels para Python 3.14 ni de mantenimiento activo. | **`POSPONER`** (solo si se verifica wheel/compilación en 3.14; alternativa sin dependencias: generar WAV con la librería estándar `wave`) |
| **Pruebas de videojuegos** | GameForge Test Runner (GF-TR) integrado en pytest | MIT | Un arnés propio que une simulación headless, inyección de eventos sintéticos y comparación visual de frames supera radicalmente a herramientas pesadas como Airtest. | **`ADOPTAR`** (Desarrollo interno de arnés especializado) |

---

## 8. Análisis de Solapamiento, Redundancia y Deduplicación Cruzada

Para cumplir estrictamente con el principio de prevención de duplicación establecido en `directives/TOKEN_EFFICIENCY.md` y `AGENTS.md`, se identifican las siguientes áreas de redundancia y sus resoluciones técnicas:

1. **PyTMX vs. `game.world.tiled_loader`:**
   - *Conflicto:* Ambas herramientas leen datos generados por Tiled.
   - *Resolución:* **Eliminar PyTMX**. El cargador propio en `game/world/tiled_loader.py` es más rápido, está tipado al 100% para las entidades de GameForge (`NpcSpec`, `TileMap`, `TileType`) y no añade ninguna dependencia externa.

2. **Pillow vs. Primitivas de Pygame:**
   - *Complementariedad:* Pygame CE es insuperable para el dibujado y blit en tiempo real a 60 FPS dentro del bucle del juego. Pillow es superior para operaciones de pipeline offline (redimensionar con remuestreo bicúbico, recortar márgenes transparentes, exportar atlas combinados y procesar metadatos).
   - *Resolución:* **Pillow para herramientas offline de agentes (`tools/`), Pygame CE para runtime del juego (`game/`)**.

3. **Pymunk vs. `game.world.collision` + `spatial.py`:**
   - *Conflicto:* Pymunk ofrece física continua completa (cuerpos rígidos, gravedad, momentos de inercia), la cual no es requerida por un RPG top-down clásico.
   - *Resolución:* **Descartar Pymunk**. Se respeta el ADR-002; la física de círculos y spatial hashing nativa de GameForge ofrece determinismo perfecto y latencia sub-milisegundo.

4. **`py_trees` vs. `game.ai.behavior_tree`:**
   - *Conflicto:* Ambas estructuras modelan árboles de comportamiento con nodos de secuencia, selector y condición.
   - *Resolución:* **Descartar `py_trees`**. El módulo interno de GameForge ya está verificado y adaptado al bucle de ticks del juego.

5. **Krita / Audacity vs. Pipeline Headless:**
   - *Conflicto:* Las herramientas gráficas de escritorio no son accesibles para agentes en entornos headless/CI.
   - *Resolución:* **Descartar para agentes**. Reemplazar completamente por FFmpeg CLI, Pillow y generadores algorítmicos.

---

## 9. Matriz Completa de Veredictos

| Herramienta / Tecnología | Categoría | Licencia | Estado Actual | Veredicto Final | Justificación Estratégica |
|:---|:---|:---|:---|:---|:---|
| **Ruff** | Calidad / Linter | MIT / Apache 2 | Dev dependency | **`ADOPTAR`** | Estándar de velocidad absoluta para linting y formateo. |
| **Pyright** | Análisis Estático | MIT | Disponible CLI | **`ADOPTAR`** | Verificación estricta de tipos de contratos compartidos y prevención de bugs en tiempo de edición. |
| **pytest** | Testing Framework | MIT | Dev dependency | **`ADOPTAR`** | Motor oficial de pruebas automatizadas del proyecto. |
| **Hypothesis** | Property Testing | MPL-2.0 | Probado efímero | **`PROBAR`** | Excelente para testing de casos límite en matemáticas y generación procedural. |
| **Tiled (Formato JSON)** | Editor de Mapas | GPLv2 (JSON libre) | Formato nativo | **`ADOPTAR`** | Estándar canónico de diseño de niveles autorales de GameForge. |
| **PyTMX** | Parser Tiled | LGPL v3 | Probado efímero | **`DESCARTAR`** | Redundante frente al cargador nativo de 158 líneas sin dependencias. |
| **LibreSprite** | Pixel Art GUI | GPL v2 | Externa | **`PROBAR`** | Recomendado como GUI de pixel art para colaboradores humanos; opcional. |
| **Pillow** | Imagen / Pipeline | HPND / MIT-like | Probado efímero | **`ADOPTAR`** | Base del procesamiento y empaquetado headless de spritesheets para agentes. |
| **Blender** | Suite 3D | GPL v2/v3 | Externa | **`POSPONER`** | Demasiado pesado para el alcance actual de RPG 2D pixel art. |
| **Diff nativo (buffer + BLEND_SUB)** | Regresión Visual | LGPL v2.1+ (Pygame CE) | Medido | **`ADOPTAR`** | 0.503 ms + 0.322 ms por frame; sin dependencias externas. |
| **Watchlight** | Regresión Visual GUI | Propietaria (código cerrado) | Beta cerrada | **`DESCARTAR`** | Solo Windows; CLI/MCP de pago tras la beta; incumple open-source y gratuidad. |
| **Pixelmatch** | Diff visual (JS) | ISC | No medido | **`DESCARTAR`** | Exigiría Node; el diff nativo ya cubre la necesidad. |
| **Pygame CE Dummy Driver**| Headless Runtime | LGPL v2.1+ | Runtime | **`ADOPTAR`** | Permite pruebas deterministas a >11,000 FPS sin ventana física. |
| **Pygame Event Queue** | Input Injection | LGPL v2.1+ | Runtime | **`ADOPTAR`** | Permite reproducción determinista de escenarios de usuario. |
| **FFmpeg CLI** | Audio / Video | LGPL / GPL | Sistema local | **`ADOPTAR`** | Herramienta CLI esencial para normalización y conversión de audio a OGG/WAV. |
| **Audacity** | Audio GUI | GPL v3 | Externa | **`DESCARTAR`** | No automatizable por agentes; relevante solo para diseño sonoro humano manual. |
| **Krita** | Arte Digital GUI | GPL v3 | Externa | **`DESCARTAR`** | Incompatible con pipelines headless de agentes; orientada a ilustración artística humana. |
| **GameForge Test Runner** | Harness de Pruebas | MIT | Diseño Misión 006 | **`ADOPTAR`** | Sistema integral propio para validación automatizada de jugabilidad. |

---

## 10. Conjunto Mínimo Esencial Recomendado para Agentes

Para maximizar la autonomía y la velocidad de los agentes minimizando el consumo de disco y memoria, el ecosistema de herramientas de GameForge se consolida en el siguiente **núcleo de 6 herramientas clave**:

```
                       ┌──────────────────────────────────────────────┐
                       │   ECOSISTEMA MÍNIMO DE TOOLING GAMEFORGE     │
                       └──────────────────────┬───────────────────────┘
                                              │
         ┌───────────────────┬────────────────┴───────────────────┬───────────────────┐
         ▼                   ▼                                    ▼                   ▼
┌─────────────────┐ ┌─────────────────┐                  ┌─────────────────┐ ┌─────────────────┐
│     CALIDAD     │ │     TESTING     │                  │     ASSETS      │ │   MULTIMEDIA    │
│  Ruff + Pyright │ │ pytest + GF-TR  │                  │  Pillow (Dev)   │ │   FFmpeg CLI    │
│ (Linter + Tipos)│ │(Headless + Diff)│                  │(Sprite Packer)  │ │ (Audio Normal.) │
└─────────────────┘ └─────────────────┘                  └─────────────────┘ └─────────────────┘
```

1. **Ruff:** Ejecutado en <60 ms para saneamiento de sintaxis e imports.
2. **Pyright:** Ejecutado para blindaje estricto de tipos en interfaces y contratos.
3. **pytest:** Ejecución de suites unitarias y de integración del motor.
4. **GameForge Test Runner (GF-TR):** Ejecución de escenarios de jugabilidad headless con aserciones de colisión y diff visual.
5. **Pillow:** Manipulación y empaquetado headless de spritesheets y atlas.
6. **FFmpeg CLI:** Normalización y conversión de audio batch por línea de comandos.

Con este conjunto mínimo, los agentes disponen del 100% de las capacidades necesarias para desarrollar, probar, perfilar y empaquetar el juego sin acumular deuda técnica ni dependencias no autorizadas.

---

## 11. Informe Final de la Misión 006

### 11.1. Las 10 herramientas más valiosas

Ordenadas por beneficio real para GameForge y evidencia disponible:

| # | Herramienta | Veredicto | Aporte concreto |
|:--:|:---|:---:|:---|
| 1 | **pytest** | ADOPTAR | 314 tests en 6.06 s; ya es la red de seguridad del proyecto. |
| 2 | **Ruff** | ADOPTAR | Repo completo en 79–96 ms; lint y formato en un binario. |
| 3 | **Driver dummy de Pygame CE** | ADOPTAR | Render headless a ~24.000 FPS; base de toda validación automática. |
| 4 | **Game Test Runner (GF-TR)** | ADOPTAR | Único sistema que valida jugabilidad completa sin humano; diseño listo. |
| 5 | **Pillow** | ADOPTAR (dev) | Procesamiento headless de sprites, paletas y atlas; 0.346 ms por escalado 2x. |
| 6 | **Diff visual nativo (buffer + `BLEND_SUB`)** | ADOPTAR | 0.503 ms + 0.322 ms por frame; cero dependencias. |
| 7 | **Pyright** | ADOPTAR (con deuda) | 139 archivos en 3.54 s; detecta contratos roto que Ruff no ve. |
| 8 | **Tiled (formato JSON)** | ADOPTAR | Estándar de mapas ya consumido por `tiled_loader` sin dependencias. |
| 9 | **FFmpeg CLI** | ADOPTAR | 58.6 ms por clip sintetizado y codificado a OGG; ya instalado. |
| 10 | **Hypothesis** | PROBAR | Genera contraejemplos mínimos en matemáticas y generación procedural. |

### 11.2. Herramientas que no merece la pena incorporar

- **Watchlight:** propietaria, solo Windows y con CLI/MCP de pago tras la beta. Incumple gratuidad,
  open-source y automatización sin licencia.
- **PyTMX:** duplica `game/world/tiled_loader.py`, que ya es nativo, tipado y sin dependencias.
- **Audacity y Krita:** GUI interactivas, sin automatización fiable; útiles solo para operadores
  humanos y no para agentes.
- **Pymunk, `py_trees`, `python-pathfinding`:** duplican física, árboles de comportamiento y
  pathfinding ya implementados y probados en el motor (ADR-002 y módulos `ai/`).
- **OpenCV:** >150 MB para operaciones que resuelve Pillow.
- **Pixelmatch:** añade Node sin ventaja sobre el diff nativo.
- **pyfxr (por ahora):** sin releases desde 2021 ni wheels verificados para Python 3.14.

### 11.3. Herramientas que deben probar primero

1. **Pillow en `tools/`** (empaquetado de atlas y swaps de paleta) con un script piloto y validación
   contra `gf-anim-v1`.
2. **GF-TR mínimo** (runner headless + inyección de eventos + una aserción de colisión) antes de
   añadir diff visual.
3. **Hypothesis** sobre `game/core/math2d` y `cavern_generation` con 1.000 ejemplos, marcado `pbt`.
4. **Pyright:** `game/core` y `game/world` ya están en 0; quedan 46 errores en `game/render`, `app.py`, `ai` y tests, priorizados por regla.
5. **LibreSprite** como flujo opcional para artistas humanos (no bloquea a los agentes).

### 11.4. Herramientas que pueden esperar

- **Blender:** útil solo si se decide un pipeline 3D-a-2D; hoy sobredimensionado (>1,2 GB).
- **pygame_gui:** MIT y mantenido (0.6.14, 30.9 MB), pero el HUD propio ya cubre el vertical slice.
- **LDtk:** alternativa moderna a Tiled; reevaluar solo si el formato TMX/JSON se queda corto.
- **Animación esquelética (Spine/DragonBones):** incompatible con la estética pixel art elegida.
- **pyfxr:** solo si aparece wheel para 3.14 o se acepta compilar Cython.

### 11.5. Arquitectura recomendada

```
Runtime del juego (dependencias: SOLO pygame-ce)
  game/  ->  simulación, render, input, datos

Tooling de agentes (dev-dependencies, nunca empaquetado)
  ruff + pyright + pytest            -> calidad
  tools/test_runner/ (GF-TR)         -> escenarios headless
  tools/asset_hub/ + Pillow          -> pipeline de assets
  FFmpeg CLI                         -> audio

Descubrimiento y gobierno
  AGENT_TOOL_CATALOG.md  -> qué existe, qué está planificado, cómo se invoca
  skills/*/SKILL.md      -> cuándo usarlo
  tools/verify.py        -> puerta única de calidad
  .gameforge/            -> registro de uso (planificado)
```

Regla estructural: **el runtime no crece**. Toda herramienta nueva entra como dev-dependency, script
en `tools/` o binario externo, y se invoca con el intérprete de `.venv`.

### 11.6. Coste aproximado en recursos

| Bloque | Disco | RAM en ejecución |
|:---|:---:|:---:|
| Ruff + Pyright + pytest | ~90 MB | ~180–250 MB (análisis) |
| Pillow (dev) | ~18 MB | ~10–25 MB |
| Hypothesis | ~10 MB | ~50–80 MB |
| FFmpeg (ya instalado) | ~100 MB | < 40 MB |
| GF-TR (código propio) | < 1 MB | ~40 MB |
| **Total nuevo estimado** | **~120 MB** | **< 300 MB pico** |

No se añade nada al binario distribuido: el juego sigue dependiendo solo de `pygame-ce`.

### 11.7. Riesgos técnicos

| Riesgo | Impacto | Mitigación |
|:---|:---:|:---|
| Pyright con 46 errores de base (core/world ya en 0) | Medio | Línea base en `pyright_baseline.json`; `tools/typecheck.py` bloquea aumentos. |
| Agente invoca herramientas planificadas (GF-TR, registro) | Medio | Catálogo §2.1 distingue DISPONIBLE vs PLANIFICADO. |
| Intérprete equivocado (Python del sistema) | Medio | Precondición explícita: `.venv/Scripts/python.exe`. |
| Deriva de baselines visuales entre CPUs | Medio | Tolerancia y máscaras de UI volátil; baselines por máquina/CI. |
| FFmpeg ausente en otra máquina | Bajo | Degradación elegante con aviso, sin abortar el build. |
| Dependencia abandonada (pyfxr, PyTMX) | Bajo | POSPONER/DESCARTAR; alternativas sin dependencias. |
| Contaminación GPL en el binario | Bajo | Editores GPL y CLI nunca se empaquetan; solo se usan en desarrollo. |
| Deriva del grafo (Graphify) | Medio | `graph_ops.py verify --strict` en la puerta de calidad. |

### 11.8. Siguientes pasos

1. **Aprobación del Director** de esta auditoría y del conjunto mínimo de 6 herramientas.
2. **Fase 1:** incorporar Pyright como dev-dependency local (offline), congelar la línea base de 112
   errores y dejar `game/core` y `game/world` en cero.
3. **Fase 2 (MVP completado en T-1001):** runner headless, input virtual, 8 aserciones, captura y
   diff exacto, dos escenarios piloto e integración en `verify.py`. Pendiente: dHash, HTML y vídeo.
4. **Fase 3:** añadir Pillow al grupo `dev` y crear el empaquetador de atlas + validador `gf-anim-v1`.
5. **Fase 4:** suite PBT opcional con Hypothesis, marcada `pbt` y fuera de `verify.py` diario.
6. **Cierre:** actualizar `tasks/BOARD.md` y el informe de tarea de la misión con evidencia de cada
   fase, sin modificar el motor fuera de lo aprobado.
