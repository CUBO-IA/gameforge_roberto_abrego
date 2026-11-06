# AGENTS.md — GAMEFORGE 2D

## Misión
Desarrollar un videojuego RPG 2D funcional usando Python como lenguaje principal. Priorizar funcionamiento verificable, arquitectura sencilla y rendimiento estable sobre complejidad prematura.

## Orden de autoridad
1. Requisitos explícitos del usuario.
2. Directivas de `directives/`.
3. Contratos de `architecture/CONTRACTS.md`.
4. Tareas aprobadas por el agente director.
5. Preferencias locales del agente.

Si hay contradicción, detener el cambio y solicitar decisión; no reinterpretar silenciosamente.

## Reglas obligatorias
- Inspeccionar el repositorio antes de modificarlo.
- No sobrescribir ni eliminar trabajo existente sin autorización.
- No inventar APIs, archivos, resultados de pruebas ni funcionalidades.
- No añadir dependencias sin justificar necesidad, mantenimiento, licencia y coste.
- No copiar código o assets de repositorios externos sin revisar licencia.
- Mantener los módulos pequeños y con responsabilidades claras.
- Separar lógica de juego, renderizado, entrada, datos y persistencia.
- Evitar singletons globales y estado mutable compartido salvo justificación.
- No usar `except Exception: pass` ni ocultar errores.
- No introducir `sleep` en el bucle principal.
- No bloquear el hilo principal con carga, generación o I/O pesado.
- Mantener configuración y datos fuera del código cuando sea razonable.
- Añadir pruebas para comportamiento nuevo y regresiones corregidas.
- Ejecutar las pruebas relevantes después de cada cambio.
- Informar con honestidad qué se probó y qué no se pudo probar.

## Protocolo de trabajo
Antes de programar:
1. Resumir el estado actual del repositorio.
2. Identificar archivos afectados.
3. Proponer cambios mínimos.
4. Definir criterios de aceptación comprobables.
5. Esperar aprobación del director si la tarea modifica contratos compartidos.

Al terminar:
1. Resumir archivos modificados.
2. Explicar decisiones y dependencias nuevas.
3. Reportar comandos ejecutados y resultados reales.
4. Indicar limitaciones y riesgos.
5. No declarar completado si quedan criterios incumplidos.

## Coordinación multiagente
- Cada tarea debe tener un único agente responsable.
- Los agentes no editan archivos fuera de su ámbito asignado.
- No modificar simultáneamente archivos compartidos.
- Los cambios se entregan mediante rama/commit o diff revisable.
- El director integra; QA verifica; ningún agente se autoaprueba un cambio crítico.
- Compartir interfaces mediante contratos, no mediante supuestos.
- Si falta un contrato, proponerlo antes de implementarlo.

## Rendimiento
- Medir antes de optimizar.
- Evitar crear superficies, fuentes, sonidos o recursos pesados cada frame.
- Usar `convert()`/`convert_alpha()` cuando corresponda tras inicializar display.
- Limitar y perfilar el frame rate; no asumir un FPS objetivo sin medir.
- Preferir estructuras de datos simples y algoritmos adecuados.
- Para mapas grandes, evaluar chunks, spatial hashing y culling.
- Mantener el renderizado separado de la simulación cuando sea útil.

## Definición de terminado (DoD)
Una tarea está terminada solo si:
- cumple sus criterios de aceptación;
- no rompe contratos existentes;
- incluye pruebas apropiadas;
- pasa las pruebas ejecutadas;
- no deja placeholders en rutas funcionales;
- está documentada si cambia arquitectura, configuración o uso;
- informa cualquier prueba omitida.
