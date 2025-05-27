echo Starting FramePack-Studio...

REM Check if Python is installed (basic check)
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH. Cannot run studio.py.
    goto end
)

python studio.py