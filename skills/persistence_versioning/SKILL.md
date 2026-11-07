# Skill: Persistencia y Versionado de Partidas (Persistence & Versioning)

## 1. Propósito
Diseñar, gestionar y migrar sistemas de almacenamiento seguro para partidas guardadas y clasificaciones locales, garantizando operaciones atómicas sin pérdida de datos, detección de corrupción de archivos y compatibilidad hacia atrás entre diferentes versiones del juego.

## 2. Contexto de aplicación
Se aplica en `game/persistence/` (`savegame.py`, `scores.py`, `paths.py`), los manejadores de estado de escena y las pruebas de serialización en `tests/test_savegame.py` y `tests/test_scores.py`.

## 3. Instrucciones
1. **Guardado atómico en disco**: Nunca escribir directamente sobre el archivo de guardado definitivo. Escribir primero en un archivo temporal en el mismo directorio (ej. `.save.tmp`) y reemplazar atómicamente mediante `os.replace()` o `Path.replace()`.
2. **Número de versión explícito**: Todo payload JSON guardado debe incluir la cabecera obligatoria `"version": N` (entero ascendente) y metadatos de creación (timestamp, semilla).
3. **Validación estricta al cargar**: Validar tamaños máximos de archivo (evitar ataques por consumo de memoria), tipos de datos esperados y rangos válidos antes de instanciar el estado del juego.
4. **Manejo de corrupción**: Si el archivo JSON está corrupto, truncado o contiene valores imposibles, capturar el error y lanzar una excepción controlada (`SaveError`), preservando el archivo corrupto con un sufijo `.bak` para diagnóstico humano.
5. **Migraciones lineales**: Al incrementar la versión del esquema de guardado, implementar una función pura de migración `migrate_v1_to_v2(data: dict) -> dict` con pruebas automatizadas que garanticen que una partida antigua se adapta al nuevo modelo.

## 4. Buenas prácticas
- **Rutas seguras multiplataforma**: Utilizar `game/persistence/paths.py` para resolver directorios de datos de usuario respetando estándares de SO (AppData en Windows, XDG en Linux).
- **Persistencia desacoplada del motor de render**: El archivo de guardado solo almacena estado de datos puros (número de piso, vida, inventario, estado de cofres y misiones). Nunca serializar objetos Pygame ni superficies.
- **SQLite para tablas e históricos**: Utilizar SQLite local para tablas de clasificación y estadísticas idempotentes, y JSON para el volcado del estado de la partida activa.

## 5. Referencias técnicas
- `architecture/CONTRACTS.md`: Contratos de `game.persistence.savegame` y `game.persistence.scores`.
- ADR-004: Serialización JSON atómica para partidas guardadas.
- ADR-008: Uso de SQLite local para tablas de clasificación.

## 6. Procedimientos
### Paso 1: Guardado atómico con reemplazo seguro
```python
def save_atomic(target_path: Path, data: dict[str, Any]) -> None:
    temp_path = target_path.with_suffix(".tmp")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    temp_path.replace(target_path)
```
### Paso 2: Validación y migración de versión
```python
def load_and_migrate(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    version = data.get("version", 0)
    if version == 1:
        data = migrate_v1_to_v2(data)
        version = 2
    if version != CURRENT_SCHEMA_VERSION:
        raise SaveError(f"Versión de esquema no soportada: {version}")
    return data
```

## 7. Criterios de aceptación
- El juego se puede guardar y cargar en cualquier momento recuperando el estado exacto del jugador, inventario y planta.
- Una interrupción forzada o fallo de energía durante el guardado nunca deja un archivo corrupto en el destino final.
- Partidas guardadas en versiones anteriores siguen siendo jugables mediante migradores automáticos.
- Errores de lectura reportan mensajes claros al usuario sin cuelgues inesperados.

## 8. Pruebas recomendadas
- `tests/test_savegame.py`: Pruebas de ciclo completo guardar-cargar, validación de campos, archivos corruptos y rechazo de versiones incompatibles.
- `tests/test_scores.py`: Pruebas de inserción y consulta en base de datos SQLite.
- Prueba simulada de fallo de disco durante escritura de archivo temporal.
