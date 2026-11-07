# Directiva global (01_GLOBAL.md)

## Propósito
Construir un RPG 2D de alcance incremental que demuestre la capacidad de los agentes para diseñar, implementar, integrar, depurar y probar un producto jugable de alta calidad en Python.

## Principios
1. **Primero vertical slice; después expansión modular**: No abordar sistemas complejos sin un núcleo jugable verificado.
2. **Control de versiones obligatorio**: Todo desarrollo se realiza en ramas cortas por tarea; ninguna entrega se acepta sin commit rastreable e historial limpio.
3. **Simplicidad explícita antes que abstracciones prematuras**: Código legible, directo y modular sobre jerarquías innecesarias.
4. **Python es el lenguaje principal**: Las dependencias nativas o externas se permiten exclusivamente cuando aportan valor medible comprobado por benchmark y cuenten con licencia compatible.
5. **No confundir cantidad de código con calidad**: Módulos pequeños con responsabilidades únicas y acotadas.
6. **Toda funcionalidad debe tener un criterio de aceptación observable y verificable**.
7. **Verificación estándar obligatoria**: Ningún cambio se integra si `tools/verify.py` no termina en verde (lint, pruebas y benchmarks).
8. **Los sistemas deben poder probarse sin abrir una ventana**: Simulación, lógica, generación y persistencia deben operar de forma pura y desacoplada de la interfaz gráfica.
9. **Decisiones arquitectónicas registradas**: Todo cambio en contratos compartidos o tecnologías clave debe constar en un ADR o contrato formal.

## Alcance del proyecto
- Mundo 2D explorable por plantas interconectadas.
- Mapas procedurales navegables y generación reproducible por semilla.
- Personajes animados, combate en tiempo real y retroalimentación de impacto.
- Inventario, looteo y recetas de fabricación (crafting).
- NPCs autónomos con rutinas y búsqueda de rutas (A*).
- Misiones y diálogos basados en catálogos de datos.
- Persistencia atómica de partida y clasificaciones locales.
- Interfaz adaptable con escalado por lienzo virtual.

## Calidad y disciplina
- Tipado gradual obligatorio en todas las firmas públicas e interfaces (`from __future__ import annotations`).
- Nombres descriptivos y ausencia de variables mágicas.
- Errores explícitos y accionables (cero `except Exception: pass`).
- Pruebas deterministas para lógica.
- Assets con procedencia y licencia obligatoriamente registradas en `assets/README.md`.
