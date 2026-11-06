@echo off
set OUT=C:\git\GAMEFORGE\_net.txt
echo == tasklist python == > "%OUT%"
tasklist /FI "IMAGENAME eq python.exe" >> "%OUT%" 2>&1
echo == curl pypi == >> "%OUT%"
curl -sS -I --max-time 20 https://pypi.org/simple/ >> "%OUT%" 2>&1
echo CURL_EXIT=%ERRORLEVEL% >> "%OUT%"
echo == DONE == >> "%OUT%"
