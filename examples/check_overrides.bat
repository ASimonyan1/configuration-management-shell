@echo off
setlocal
call "%~dp0..\run.bat" --config config.json --vfs vfs_min.csv --prompt "cli> " --script scripts/stage2.txt
call "%~dp0..\run.bat" --config config.json --vfs vfs.csv --prompt "emu> " --script scripts/stage2.txt
