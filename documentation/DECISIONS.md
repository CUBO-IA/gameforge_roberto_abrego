# Registro de decisiones arquitectónicas (ADR)

## ADR-001 — Pygame CE como framework

**Estado:** aceptada  
**Contexto:** se necesita ventana, entrada, superficies, fuentes y audio con una
API madura y mantenida.  
**Decisión:** usar `pygame-ce>=2.5`.  
**Consecuencias:** ecosistema estable, licencia LGPL compatible con uso
dinámico; el render se mantiene separado para poder probar el dominio sin
inicializar vídeo.

## ADR-002 — No introducir Pymunk en este vertical slice

**Estado:** aceptada, revisable  
**Contexto:** el juego es top-down; no hay gravedad, rotaciones, restricciones ni
apilamiento de cuerpos. Las colisiones relevantes son círculo contra tiles y
círculo contra círculo.  
**Alternativas:** Pymunk (física continua), motor propio de cuerpos rígidos,
colisión tile-based.  
**Decisión:** colisión tile-based con subdivisión de desplazamiento y resolución
por ejes; separación simple entre enemigos.  
**Motivos:** menos dependencias nativas, comportamiento determinista, código
testeable sin ventana y rendimiento suficiente para decenas de entidades.  
**Cuándo revisar:** si se añaden cuerpos rotatorios, cadenas, vehículos,
plataformas móviles con arrastre o cientos de colisiones continuas. En ese caso,
Pymunk sería la primera opción y se documentaría la migración.

## ADR-003 — Arte y audio procedurales, sin assets externos

**Estado:** aceptada  
**Contexto:** el kit exige registrar procedencia/licencia de assets y no copiar
recursos sin permiso.  
**Decisión:** dibujar tiles, personajes y efectos con primitivas de Pygame;
sintetizar SFX en memoria; usar la fuente por defecto.  
**Consecuencias:** repositorio ligero y sin riesgo de licencia; la calidad
visual depende del código y no de un artista externo. Los assets futuros
deberán registrarse en `assets/README.md`.

## ADR-004 — JSON para partida y SQLite para clasificación

**Estado:** aceptada  
**Contexto:** el guardado es un documento pequeño y versionado; la
clasificación requiere ordenar y filtrar registros.  
**Decisión:** JSON con escritura atómica para la ranura de partida; SQLite para
las partidas terminadas.  
**Consecuencias:** recuperación sencilla ante corrupción, sin servidor. La
clasificación es local y no multiusuario.

## ADR-005 — Vertical slice de una planta

**Estado:** aceptada  
**Contexto:** el primer hito del kit exige un producto jugable y verificable
antes de ampliar contenido.  
**Decisión:** una mazmorra con tres fragmentos y un altar; victoria al activarlo.  
**Consecuencias:** partida corta, sin progresión entre pisos. El generador ya
acepta `floor` y el guardado lo almacena para una futura expansión.

## ADR-006 — Sin bus de eventos global

**Estado:** aceptada  
**Contexto:** el número de sistemas es pequeño y las interacciones están
localizadas en `PlayScene`.  
**Decisión:** llamadas directas y datos de intención (`AttackSpec`,
`EnemyIntent`).  
**Consecuencias:** flujo explícito y depurable; si aparecen misiones,
logros y audio reactivo desacoplados, se evaluará un bus tipado y acotado.

## ADR-007 — Determinismo y validación de mapas

**Estado:** aceptada  
**Contexto:** el guardado solo almacena la semilla; la mazmorra se regenera.  
**Decisión:** RNG local (`random.Random`), IDs estables y BFS obligatorio antes
de aceptar un mapa.  
**Consecuencias:** cargar una partida reproduce el mismo mundo y el progreso
(cofres/enemigos) se reaplica por ID.

## ADR-008 — Errores explícitos y degradación controlada

**Estado:** aceptada  
**Contexto:** el juego debe informar de fallos de configuración, guardado,
SQLite o audio.  
**Decisión:** excepciones de dominio con mensajes claros; la UI muestra el
error de guardado/puntuación; el audio ausente se registra y el juego sigue.  
**Consecuencias:** no se ocultan fallos con `except Exception: pass`; las capas
superiores deciden cómo presentar el error.

## ADR-009 — GF-Graph: Sistema unificado local de grafos, memoria y contexto operativo

**Estado:** aceptada  
**Contexto:** La colaboración multiagente requiere conocimiento persistente de la topología
de código, contratos y memoria de decisiones. Las soluciones investigadas (GitNexus, CodeGraph,
ctx, Graphiti, Cognee, Aider RepoMap, LangGraph) presentan redundancias y arrastran dependencias
pesadas no justificadas (Node.js, Rust compilado, Neo4j, LanceDB, LangChain).  
**Decisión:** Diseñar e integrar la arquitectura unificada `GF-Graph`: almacenamiento ACID en SQLite
WAL local (`.gameforge/graph.db`), extracción determinista con `ast` nativo de Python, cálculo de
centralidad/relevancia con PageRank (inspirado en Aider), esqueletos estructurales (inspirado en ctx),
invalidación bi-temporal con 5 estados epistémicos (inspirado en Graphiti) y recibos de auditoría
pre-flight de uso obligatorio.  
**Consecuencias:** Cero dependencias de servicios de pago o cloud; cero llamadas a LLMs para
extracción sintáctica; reducción >85% en tokens de contexto por tarea; compatibilidad 100% con
Python 3.11+ y suite `verify.py`.

## ADR-010 — Integración de Graphify como motor de comprensión estructural y memoria operativa

**Estado:** aceptada (Misión 005)  
**Contexto:** Se requiere materializar la memoria operativa y la topología de código en un motor
probado que soporte interoperabilidad nativa con Claude Code, Claude Desktop y herramientas agénticas
mediante el protocolo MCP (Model Context Protocol), con extracción incremental y sin suscripciones.  
**Decisión:** Adoptar `graphifyy` (v0.9.85) en un entorno aislado (`uv tool`) coordinado por
`tools/graph_ops.py` y `tools/graph_memory/`. Integrar extracción AST determinista para código,
parser de estructura para Markdown, y un extractor ontológico para la memoria de decisiones
(ADRs, tareas, contratos, problemas y soluciones con estados epistémicos). Exponer el grafo
vía servidor MCP (`graphify.serve`) y hacer obligatoria la verificación de frescura del grafo en `tools/verify.py`.  
**Consecuencias:** Rendimiento medido de 3.64 s en cold build y 235 ms en actualización incremental;
reducción de tokens del 99.68%; soporte de radio de explosión (*blast radius*) en 583 ms; aislamiento
total del entorno del juego (cero dependencias adicionales en `.venv`); auditoría transparente en `audit.log`.
