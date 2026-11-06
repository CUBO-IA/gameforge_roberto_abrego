# Benchmarks

Se ejecutan manualmente; no forman parte de `pytest` para no hacer la suite
dependiente de la máquina.

```bash
python benchmark/bench_generation.py --count 50 --seed 1000
python benchmark/bench_simulation.py --frames 3000 --enemies 24
```

## Condiciones a registrar

- CPU, RAM, SO y versión de Python.
- Versión de pygame-ce (solo afecta a benchmarks de render; estos miden lógica).
- Comando exacto y parámetros.
- p50, p95, máximo y número de muestras.

## Qué miden

- `bench_generation.py`: tiempo de `generate_dungeon` incluyendo BFS y
  reintentos.
- `bench_simulation.py`: actualización de jugador, ataque, IA, separación y
  colisión, sin ventana ni render. Es una cota inferior del coste de frame.

No se comparan máquinas ni se declaran objetivos de FPS sin medir en el equipo
de destino.
