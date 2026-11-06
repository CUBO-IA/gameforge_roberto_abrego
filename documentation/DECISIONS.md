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
