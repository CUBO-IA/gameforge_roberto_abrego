@echo off
set PY=C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe
set OUT=C:\git\GAMEFORGE\_smoke.txt
cd /d C:\git\GAMEFORGE
set PYTHONUNBUFFERED=1
echo == SMOKE 120 HEADLESS == > "%OUT%"
"%PY%" -m game --headless --frames 120 --new-game --seed 3 --data-dir C:\Users\DellUser\AppData\Local\Temp\gameforge-smoke >> "%OUT%" 2>&1
echo SMOKE_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == SMOKE 300 HEADLESS == >> "%OUT%"
"%PY%" -m game --headless --frames 300 --new-game --seed 42 --data-dir C:\Users\DellUser\AppData\Local\Temp\gameforge-smoke2 >> "%OUT%" 2>&1
echo SMOKE2_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
