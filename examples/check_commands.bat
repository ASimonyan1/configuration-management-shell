@echo off
setlocal
call "%~dp0..\run.bat" --config config.json --vfs vfs.csv --prompt "commands> " --script scripts/stage4.txt
