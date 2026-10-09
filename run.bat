@echo off
setlocal
pushd "%~dp0"
set "launch_args=%*"
if "%~1"=="" set "launch_args=--config config.json"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m src.main %launch_args%
) else (
    where py >nul 2>nul
    if errorlevel 1 (
        python -m src.main %launch_args%
    ) else (
        py -3 -m src.main %launch_args%
    )
)
set "result=%errorlevel%"
if not "%result%"=="0" pause
popd
exit /b %result%
