# Skill: Procedural Generation

## Objetivo
Generar mapas reproducibles y jugables, no ruido aleatorio sin diseño.

## Requisitos
- Toda generación acepta una semilla.
- Mismo algoritmo + misma semilla + misma configuración producen el mismo mapa.
- Definir reglas de conectividad, accesibilidad y distribución.
- Separar generación de datos y renderizado.
- Validar que el punto inicial sea seguro y que objetivos sean alcanzables.

## Proceso
1. Definir representación del mapa.
2. Crear generador mínimo determinista.
3. Añadir validadores de conectividad y reglas.
4. Crear pruebas con semillas conocidas.
5. Medir tiempo y memoria para tamaños crecientes.
