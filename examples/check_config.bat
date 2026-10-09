@echo off
setlocal
pushd "%~dp0.."
call run.bat --vfs data/cli.csv --prompt "cli> " --script scripts/stage2.txt --config config.json
set "result=%errorlevel%"
popd
exit /b %result%
