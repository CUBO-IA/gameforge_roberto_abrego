@echo off
set PY=C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe
set OUT=C:\git\GAMEFORGE\_import_probe.txt
cd /d C:\git\GAMEFORGE
set PYTHONUNBUFFERED=1
echo == PROBE == > "%OUT%"
"%PY%" -c "import time,sys; t=time.time(); print('start'); import pygame; print('pygame', pygame.version.ver, round(time.time()-t,2)); import game.core.config as c; print('config', round(time.time()-t,2)); import game.app; print('app', round(time.time()-t,2)); import tests.test_headless_app; print('tests_import', round(time.time()-t,2))" >> "%OUT%" 2>&1
echo PROBE_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
