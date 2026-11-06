@echo off
set PY=C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe
set OUT=C:\git\GAMEFORGE\_tests.txt
cd /d C:\git\GAMEFORGE
echo == PYTHON VERSION == > "%OUT%"
"%PY%" --version >> "%OUT%" 2>&1
echo == PIP INSTALL == >> "%OUT%"
"%PY%" -m pip install --disable-pip-version-check pygame-ce pytest >> "%OUT%" 2>&1
echo PIP_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == PIP LIST == >> "%OUT%"
"%PY%" -m pip list >> "%OUT%" 2>&1
echo == COMPILEALL == >> "%OUT%"
"%PY%" -m compileall -q game tests >> "%OUT%" 2>&1
echo COMPILE_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == PYTEST == >> "%OUT%"
"%PY%" -m pytest -q >> "%OUT%" 2>&1
echo PYTEST_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
