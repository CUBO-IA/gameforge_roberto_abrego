# Skill: Pygame CE

## Cuándo usar
Ventana, eventos, superficies, sprites, audio, renderizado 2D e input.

## Procedimiento
1. Verificar versión instalada y documentación correspondiente.
2. Inicializar display antes de convertir superficies.
3. Crear un bucle principal con eventos, actualización y render.
4. Limitar FPS y medir tiempo de frame.
5. Cargar recursos una vez y reutilizarlos.
6. Separar input, update y draw.
7. Cerrar limpiamente audio/display.

## Evitar
- Cargar imágenes en cada frame.
- Crear miles de objetos temporales sin medir.
- Bloquear el hilo principal.
- Consultar eventos desde múltiples subsistemas.
- Mezclar lógica de inventario o combate con código de dibujo.

## Pruebas
Probar lógica fuera de la ventana cuando sea posible. Para integración gráfica, usar modo dummy/headless solo si el entorno y el test lo soportan; documentar limitaciones.
