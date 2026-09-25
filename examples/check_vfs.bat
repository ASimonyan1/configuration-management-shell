@echo off
setlocal
call "%~dp0..\run.bat" --vfs vfs_min.csv --script scripts/vfs_min.txt
call "%~dp0..\run.bat" --vfs vfs_nested.csv --script scripts/vfs_nested.txt
call "%~dp0..\run.bat" --vfs vfs.csv --script scripts/stage3.txt
call "%~dp0..\run.bat" --vfs missing.csv
