# Skill: Contenido Dirigido por Datos (Data-Driven Content)

## 1. Propósito
Estandarizar la definición, serialización y validación estricta de catálogos de contenido (enemigos, ítems, recetas de crafting, misiones y diálogos) mediante archivos de datos externos (JSON), desacoplando la creación de contenido del código fuente de simulación y evitando cuellos de botella de edición concurrente entre agentes.

## 2. Contexto de aplicación
Se aplica en `game/data/` (archivos `.json`), los catálogos en `game/entities/` (como `enemy_catalog.py`, `item_catalog.py`), `game/sim/` y los cargadores de configuración.
Es el pilar fundamental que permite a los agentes de gameplay o IA añadir contenido sin modificar las clases de lógica del motor.

## 3. Instrucciones
1. **Validación estricta al cargar (`from_dict`)**: Todo catálogo debe implementar un método de fábrica o clase catálogo que valide tipos, rangos, campos obligatorios y valores por defecto. Si un campo no es válido, lanzar un error específico (ej. `CatalogError`) con mensaje accionable indicando el archivo y campo defectuoso.
2. **Sin código ejecutable en archivos de datos**: No permitir `eval()`, `exec()`, imports dinámicos ni cadenas que representen código Python en los archivos JSON.
3. **Control de versiones de esquema**: Los archivos de catálogo complejos deben incluir un campo `"version": 1` para permitir futuras migraciones o compatibilidad hacia atrás.
4. **Identificadores estables y únicos**: Cada elemento del catálogo debe poseer un `id` alfanumérico único (ej. `slime_cave`, `iron_sword`, `quest_forge_altar`).
5. **Composición de comportamientos**: Los enemigos y entidades se definen combinando arquetipos o componentes genéricos (`melee`, `ranged`, `charger`) parametrizados por números (velocidad, daño, radio, cooldowns), nunca por nombres de métodos en Python.

## 4. Buenas prácticas
- **Inmutabilidad en memoria**: Cargar los catálogos en estructuras inmutables o `frozen dataclasses` para prevenir modificaciones accidentales durante la simulación.
- **Fail-Fast**: Cargar y validar todos los catálogos de datos al inicio de la aplicación o al instanciar el juego; no diferir la validación al momento del combate o interacción.
- **Cero dependencias de render**: Los datos definen atributos lógicos (vida, daño, velocidad, sprite_id simbólico). No contienen referencias directas a `pygame.Surface`.

## 5. Referencias técnicas
- `game/entities/enemy_catalog.py`: Implementación de referencia para catálogos validados.
- `game/data/enemies.json`: Ejemplo de catálogo data-driven.
- ADR-005: Separación de contenido en datos estructurados JSON.

## 6. Procedimientos
### Paso 1: Definición del esquema y dataclass inmutable
```python
@dataclass(frozen=True)
class ItemDefinition:
    item_id: str
    name: str
    max_stack: int
    heal_value: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ItemDefinition:
        if not isinstance(data.get("item_id"), str):
            raise CatalogError("item_id debe ser un string válido")
        return cls(
            item_id=data["item_id"],
            name=str(data.get("name", "")),
            max_stack=int(data.get("max_stack", 1)),
            heal_value=float(data.get("heal_value", 0.0))
        )
```
### Paso 2: Carga del catálogo completo con validación
```python
def load_item_catalog(path: Path) -> dict[str, ItemDefinition]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    catalog = {}
    for entry in raw.get("items", []):
        item = ItemDefinition.from_dict(entry)
        catalog[item.item_id] = item
    return catalog
```

## 7. Criterios de aceptación
- Es posible añadir un nuevo enemigo, ítem o receta modificando únicamente archivos en `game/data/`, sin tocar ningún archivo `.py`.
- Errores claros y descriptivos si un archivo JSON tiene sintaxis corrupta o campos con tipos incorrectos.
- Cobertura de pruebas unitarias para cada cargador de catálogo.

## 8. Pruebas recomendadas
- `tests/test_enemy_catalog.py`: Verificación de casos felices y manejo de errores (campos faltantes, valores negativos, tipos erróneos).
- Pruebas de integración asegurando que todas las entidades referenciadas en `config.json` y `data/*.json` existen y son válidas.
