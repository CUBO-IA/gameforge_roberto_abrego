@echo off
set PY=C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe
set OUT=C:\git\GAMEFORGE\_bench.txt
cd /d C:\git\GAMEFORGE
set PYTHONUNBUFFERED=1
echo == BENCH GENERATION == > "%OUT%"
"%PY%" benchmark\bench_generation.py --count 50 --seed 1000 >> "%OUT%" 2>&1
echo BENCH_GEN_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == BENCH SIMULATION == >> "%OUT%"
"%PY%" benchmark\bench_simulation.py --frames 3000 --enemies 24 --seed 7 >> "%OUT%" 2>&1
echo BENCH_SIM_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
