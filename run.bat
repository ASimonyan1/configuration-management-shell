@echo off
setlocal
pushd "%~dp0"
python -m src.main %*
set "result=%errorlevel%"
popd
exit /b %result%
