@echo off
set OUT=C:\git\GAMEFORGE\_proc.txt
echo == tasklist == > "%OUT%"
tasklist /FI "IMAGENAME eq python.exe" /V >> "%OUT%" 2>&1
echo == wmic == >> "%OUT%"
wmic process where "name='python.exe'" get ProcessId,CreationDate,UserModeTime,KernelModeTime,CommandLine >> "%OUT%" 2>&1
echo == DONE == >> "%OUT%"
