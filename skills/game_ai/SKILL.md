# Skill: Game AI

## Objetivo
Implementar comportamientos legibles, depurables y eficientes para NPC y enemigos.

## Orden recomendado
1. Máquina de estados finitos para comportamiento básico.
2. Percepción simple por distancia, línea de visión y eventos.
3. Navegación sobre grid o grafo.
4. Utility AI o planificación solo cuando el diseño lo justifique.

## Reglas
- Separar percepción, decisión y acción.
- No ejecutar búsqueda de caminos completa cada frame.
- Usar límites de actualización y caché.
- Hacer deterministas las pruebas mediante semilla/reloj controlado.
- Proveer estados de depuración visibles en logs o herramientas internas.
