# Skill: Flujo Git para Coordinación Multiagente (Git Multiagent Workflow)

## 1. Propósito
Definir los procedimientos de control de versiones, nomenclatura de ramas, gestión de commits, resolución de conflictos y entrega formal de tareas para permitir el desarrollo colaborativo y concurrente de múltiples agentes de software sin pérdida de código ni colisiones en archivos compartidos.

## 2. Contexto de aplicación
Se aplica obligatoriamente en todas las operaciones del ciclo de vida del código:
- Creación de ramas y commits por parte de agentes especialistas.
- Integración y revisión por parte de QA/INTEGRADOR.
- Aprobación final y etiquetado por parte de DIRECTOR/ARQUITECTO.
- Gestión del tablero en `tasks/BOARD.md`.

## 3. Instrucciones
1. **Ramas cortas por tarea**: Cada agente debe trabajar en una rama aislada con la convención `task/T-XXX-descripcion-breve` derivada de `main` actualizado.
2. **Respeto a la matriz de propiedad (`architecture/OWNERSHIP.md`)**: Un agente solo tiene autorización para editar archivos dentro de su ámbito asignado en la tarea. No modificar archivos fuera de scope ni dependencias compartidas sin autorización expresa.
3. **Commits semánticos y atómicos**: Realizar commits pequeños con mensajes claros:
   - `feat(sim): implementar sistema de looteo de cofres (T-103)`
   - `fix(collision): corregir tunneling en esquinas diagonales (T-104)`
   - `test(catalog): anadir pruebas de validacion para enemies.json`
4. **Verificación previa a la entrega**: Antes de solicitar integración o declarar una tarea como `ENTREGADA`, el agente debe ejecutar obligatoriamente `tools/verify.py` y confirmar que termina con exit code 0.
5. **No rebase destructivo ni force-push en ramas compartidas**: Nunca ejecutar `git push --force` en `main`.

## 4. Buenas prácticas
- **Diffs pequeños y revisables**: Mantener los cambios bajo las 300 líneas de diff siempre que sea posible para facilitar la auditoría del integrador.
- **Sin residuos en el árbol de trabajo**: No hacer commit de archivos temporales (`.pyc`, `.tmp`, caches de pytest o benchmarks). Respetar `.gitignore`.
- **Integración continua local**: Integrar la rama `main` en la rama de la tarea antes de entregar para resolver cualquier posible divergencia de forma temprana.

## 5. Referencias técnicas
- `architecture/OWNERSHIP.md`: Matriz de asignación de rutas y responsabilidades por agente.
- `directives/04_INTEGRATION.md`: Directiva de integración de código.
- Guías canónicas de Git Flow y Conventional Commits.

## 6. Procedimientos
### Paso 1: Inicio de tarea y creación de rama
```bash
git checkout main
git pull
git checkout -b task/T-103-quest-system
```
### Paso 2: Desarrollo y verificación local
```bash
# Implementar cambios en game/sim/ y tests/
python tools/verify.py
```
### Paso 3: Commit con scope y tarea asociada
```bash
git add game/sim/quest.py tests/test_quest.py
git commit -m "feat(sim): implementar nucleo de misiones simples (T-103)"
```
### Paso 4: Creación de informe y entrega en tablero
- Documentar evidencia en `tasks/reports/T-103.md`.
- Mover tarea a columna `ENTREGADA` en `tasks/BOARD.md`.

## 7. Criterios de aceptación
- Historial de Git limpio, lineal y comprensible.
- Cada commit compila y pasa las pruebas (`tools/verify.py` verde).
- Cero conflictos de fusión no resueltos o código pisado entre agentes.
- Todo cambio rastreable a una tarea en `tasks/BOARD.md`.

## 8. Pruebas recomendadas
- Verificación de `git status` y `git log --graph --oneline` antes de cualquier integración.
- Ejecución de `tools/verify.py` en la rama integrada antes de fusionar definitivamente en `main`.
