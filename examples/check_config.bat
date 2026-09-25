@echo off
setlocal
call "%~dp0..\run.bat" --vfs vfs.csv --prompt "manual> "
call "%~dp0..\run.bat" --vfs vfs.csv --script scripts/stage2.txt
call "%~dp0..\run.bat" --config config.json
call "%~dp0..\run.bat" --config config.json --vfs vfs_min.csv --prompt "cli> " --script scripts/stage2.txt
call "%~dp0..\run.bat" --config missing.json
call "%~dp0..\run.bat" --vfs vfs.csv --script missing.txt
