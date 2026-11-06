# Calidad, seguridad y robustez

- Validar archivos de guardado antes de usarlos.
- No ejecutar código contenido en archivos de datos.
- Limitar tamaños y cantidades de datos cargados.
- Manejar rutas de archivos con `pathlib`.
- No almacenar secretos ni claves API en el repositorio.
- No descargar ni ejecutar código externo automáticamente.
- Registrar licencias de bibliotecas y assets.
- Mantener pruebas para serialización, carga corrupta y versiones antiguas.
- Evitar dependencias abandonadas o con licencia incompatible.
- No afirmar compatibilidad multiplataforma sin probarla.
- No afirmar rendimiento objetivo sin medición reproducible.

## Criterios mínimos de aceptación
- Inicio y cierre limpios.
- Entrada de teclado funcional.
- Movimiento y colisión reproducibles.
- Interacción con objeto.
- Inventario actualizable.
- Guardado y carga correctos.
- Pruebas automatizadas para reglas de dominio.
- Sin errores críticos conocidos en el flujo principal.
