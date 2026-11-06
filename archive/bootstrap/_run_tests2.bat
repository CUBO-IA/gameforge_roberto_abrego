@echo off
set PY=C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe
set OUT=C:\git\GAMEFORGE\_tests2.txt
cd /d C:\git\GAMEFORGE
set PYTHONUNBUFFERED=1
echo == COMPILEALL == > "%OUT%"
"%PY%" -m compileall -q game tests >> "%OUT%" 2>&1
echo COMPILE_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == PYTEST == >> "%OUT%"
"%PY%" -m pytest -q -p no:cacheprovider >> "%OUT%" 2>&1
echo PYTEST_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
