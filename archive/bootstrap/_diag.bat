@echo off
set OUT=C:\git\GAMEFORGE\_diag2.txt
echo == LOCALAPPDATA Programs == > "%OUT%"
dir /b "%LOCALAPPDATA%\Programs" >> "%OUT%" 2>&1
echo == WinGet Packages == >> "%OUT%"
dir /b "%LOCALAPPDATA%\Microsoft\WinGet\Packages" >> "%OUT%" 2>&1
echo == Program Files python == >> "%OUT%"
dir /b "C:\Program Files" 2>&1 | findstr /i "python git hub" >> "%OUT%"
echo == Program Files x86 == >> "%OUT%"
dir /b "C:\Program Files (x86)" 2>&1 | findstr /i "python git hub" >> "%OUT%"
echo == where python == >> "%OUT%"
where python >> "%OUT%" 2>&1
echo == where py == >> "%OUT%"
where py >> "%OUT%" 2>&1
echo == where git == >> "%OUT%"
where git >> "%OUT%" 2>&1
echo == registry HKCU == >> "%OUT%"
reg query "HKCU\Software\Python" /s >> "%OUT%" 2>&1
echo == registry HKLM == >> "%OUT%"
reg query "HKLM\Software\Python" /s >> "%OUT%" 2>&1
echo == DONE == >> "%OUT%"
