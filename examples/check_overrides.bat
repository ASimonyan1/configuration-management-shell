@echo off
setlocal
pushd "%~dp0.."
call run.bat --vfs data/override.csv --prompt "" --script scripts/exit.txt --config config.json
set "result=%errorlevel%"
popd
exit /b %result%
