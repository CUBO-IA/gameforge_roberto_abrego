# Directiva global de eficiencia de tokens (TOKEN_EFFICIENCY.md)

## 1. Principio general

Todos los agentes deben optimizar el consumo de tokens, contexto y llamadas a herramientas sin sacrificar la calidad técnica, la precisión ni la seguridad.

La eficiencia es una responsabilidad permanente, no una optimización opcional.

## 2. Lectura selectiva

- No leer todo el proyecto al iniciar una tarea.
- Identificar primero los archivos directamente relacionados.
- Consultar README, contratos y directivas únicamente cuando sean relevantes.
- No volver a leer archivos cuyo contenido ya esté disponible en el contexto actual.
- Evitar imprimir archivos completos cuando basten fragmentos.
- Usar búsquedas específicas por símbolos, funciones o rutas.
- No inspeccionar dependencias completas si solo se necesita una interfaz concreta.

## 3. Investigación externa

- Investigar primero los repositorios con mayor relevancia.
- No repetir búsquedas que ya tengan resultados suficientes.
- Priorizar documentación oficial, README, ejemplos y código relevante.
- No descargar repositorios completos sin justificación.
- No investigar alternativas redundantes cuando ya exista una solución técnicamente adecuada.
- Registrar hallazgos en documentos para evitar repetir investigaciones.
- Diferenciar hechos comprobados de hipótesis.

## 4. Comunicación entre agentes

Los informes deben ser breves, estructurados y verificables.

Formato obligatorio:

- Objetivo.
- Trabajo realizado.
- Archivos modificados.
- Decisiones técnicas.
- Pruebas ejecutadas y resultados.
- Problemas pendientes.
- Próximo paso.

No incluir:
- Narraciones extensas del proceso.
- Repetición de instrucciones.
- Explicaciones genéricas.
- Código completo cuando basta indicar archivo y función.
- Resúmenes de información ya documentada.

Los agentes deben comunicarse mediante contratos y archivos compartidos, no mediante conversaciones repetitivas.

## 5. Prevención de duplicación

Antes de crear una función, módulo, sistema o herramienta:

1. Comprobar si ya existe.
2. Verificar si otro agente está trabajando en ello.
3. Consultar los contratos de arquitectura.
4. Reutilizar componentes existentes cuando corresponda.
5. Documentar únicamente cambios relevantes.

No duplicar sistemas por desconocimiento del trabajo de otros agentes.

## 6. Gestión del contexto

- Mantener las tareas pequeñas y delimitadas.
- Dividir trabajos grandes en subtareas independientes.
- Evitar cargar documentación completa en cada agente.
- Crear resúmenes técnicos persistentes para trabajos largos.
- Conservar decisiones importantes en DECISION_LOG.md.
- Descargar del contexto información histórica que ya esté documentada.
- Antes de cerrar una sesión, registrar el estado necesario para continuar sin repetir trabajo.

## 7. Uso eficiente de herramientas

- Agrupar búsquedas relacionadas cuando sea posible.
- Evitar ejecutar comandos redundantes.
- No repetir pruebas que no hayan sufrido cambios relevantes, salvo que se necesite verificar una regresión.
- Utilizar herramientas de inspección selectiva.
- No generar archivos temporales innecesarios.
- Evitar llamadas externas si la información local es suficiente.

## 8. Control de calidad

La reducción de tokens nunca justifica:

- Omitir pruebas importantes.
- Ignorar errores.
- Saltarse verificaciones de licencias.
- Inventar resultados.
- Eliminar documentación necesaria.
- Reducir la seguridad o mantenibilidad.
- Implementar soluciones sin comprender sus contratos.

## 9. Informes de eficiencia

Cada agente debe registrar:

- Tarea completada.
- Recursos consultados.
- Archivos modificados.
- Herramientas utilizadas.
- Trabajo reutilizado.
- Duplicaciones evitadas.
- Problemas pendientes.

No inventar cifras de tokens ni declarar ahorros que no se hayan medido.

## 10. Regla final

La prioridad es obtener el máximo resultado técnico con el mínimo consumo razonable de contexto, tokens, tiempo y recursos computacionales.

- Pensar antes de investigar.
- Investigar antes de implementar.
- Reutilizar antes de duplicar.
- Documentar antes de repetir.

---

## Directivas obligatorias

Antes de ejecutar cualquier tarea, consultar:
- `directives/TOKEN_EFFICIENCY.md`
- `directives/ARCHITECTURE.md` (o `directives/02_ARCHITECTURE.md`)
- `directives/QUALITY_AND_SECURITY.md` (o `directives/03_QUALITY_AND_SECURITY.md`)

Aplicar lectura selectiva y evitar investigaciones o implementaciones duplicadas.
