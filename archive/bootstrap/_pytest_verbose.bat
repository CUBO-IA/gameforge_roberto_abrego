@echo off
set PY=C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe
set OUT=C:\git\GAMEFORGE\_pytest_verbose.txt
cd /d C:\git\GAMEFORGE
taskkill /F /PID 3052 > "%OUT%" 2>&1
set PYTHONUNBUFFERED=1
echo == PYTEST VERBOSE == >> "%OUT%"
"%PY%" -m pytest -vv -x -p no:cacheprovider >> "%OUT%" 2>&1
echo PYTEST_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
