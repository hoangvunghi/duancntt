@echo off
echo Create Account Admin...
python create_admin.py
if %errorlevel% neq 0 (
    echo Error: Python script failed with exit code %errorlevel%.
) else (
    echo Create done!
)