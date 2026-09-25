@echo off
setlocal
pushd "%~dp0"
if "%~1"=="" (
    python -m src.main --config config.json
) else (
    python -m src.main %*
)
set "result=%errorlevel%"
popd
exit /b %result%
