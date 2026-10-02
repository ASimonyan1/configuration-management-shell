@echo off
setlocal
call "%~dp0..\run.bat" --config config.json --vfs vfs_min.csv --prompt "min> " --script scripts/vfs_min.txt
call "%~dp0..\run.bat" --config config.json --vfs vfs_nested.csv --prompt "deep> " --script scripts/vfs_nested.txt
call "%~dp0..\run.bat" --config config.json --vfs vfs.csv --prompt "full> " --script scripts/stage3.txt
