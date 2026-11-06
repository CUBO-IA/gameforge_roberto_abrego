# Directiva de integración

## Flujo
1. Director crea tarea y asigna responsable.
2. Especialista inspecciona contexto y contratos.
3. Especialista implementa en su ámbito.
4. Especialista ejecuta pruebas y entrega diff/commit.
5. Integrador revisa conflictos y contratos.
6. QA ejecuta pruebas de regresión.
7. Director acepta o devuelve con hallazgos.

## Prohibiciones
- No hacer merge sin pruebas relevantes.
- No resolver conflictos borrando trabajo ajeno sin inspección.
- No cambiar nombres o firmas públicas unilateralmente.
- No actualizar dependencias globales sin autorización.
- No marcar una tarea como lista por haber generado archivos.

## Informe de entrega
- Objetivo y alcance.
- Archivos creados/modificados.
- Interfaces afectadas.
- Dependencias añadidas y motivo.
- Pruebas ejecutadas y resultado.
- Riesgos y trabajo pendiente.
