@echo off
set OUT=C:\git\GAMEFORGE\_env.txt
echo == CPU == > "%OUT%"
wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors /format:list >> "%OUT%" 2>&1
echo == RAM == >> "%OUT%"
wmic ComputerSystem get TotalPhysicalMemory /format:list >> "%OUT%" 2>&1
echo == OS == >> "%OUT%"
wmic os get Caption,Version,BuildNumber /format:list >> "%OUT%" 2>&1
echo == PY == >> "%OUT%"
"C:\Users\DellUser\AppData\Local\Programs\Python\Python312\python.exe" -c "import platform,pygame;print(platform.platform());print('python',platform.python_version());print('pygame-ce',pygame.version.ver,'SDL',pygame.version.SDL)" >> "%OUT%" 2>&1
echo == DONE == >> "%OUT%"
