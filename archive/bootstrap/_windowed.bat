@echo off
set PY=C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe
set OUT=C:\git\GAMEFORGE\_windowed.txt
cd /d C:\git\GAMEFORGE
set PYTHONUNBUFFERED=1
echo == WINDOWED 240 FRAMES == > "%OUT%"
"%PY%" -m game --frames 240 --new-game --seed 5 --data-dir C:\Users\DellUser\AppData\Local\Temp\gameforge-window >> "%OUT%" 2>&1
echo WINDOWED_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
