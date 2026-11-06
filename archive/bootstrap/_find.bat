@echo off
set OUT=C:\git\GAMEFORGE\_find.txt
echo == Python dir == > "%OUT%"
dir /b "%LOCALAPPDATA%\Programs\Python" >> "%OUT%" 2>&1
echo == Python312 tree == >> "%OUT%"
dir /b "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" >> "%OUT%" 2>&1
echo == Git cmd == >> "%OUT%"
dir /b "C:\Program Files\Git\cmd\git.exe" >> "%OUT%" 2>&1
echo == Git bin == >> "%OUT%"
dir /b "C:\Program Files\Git\bin\git.exe" >> "%OUT%" 2>&1
echo == versions == >> "%OUT%"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" --version >> "%OUT%" 2>&1
"C:\Program Files\Git\cmd\git.exe" --version >> "%OUT%" 2>&1
echo == gh search == >> "%OUT%"
dir /b "C:\Program Files" 2>&1 | findstr /i "github" >> "%OUT%"
echo == DONE == >> "%OUT%"
