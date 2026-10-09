@echo off
setlocal
call "%~dp0..\run.bat" --config config.json --vfs vfs.csv --prompt "cli> " --script scripts/stage2.txt
