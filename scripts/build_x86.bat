@echo off
setlocal

pushd "%~dp0.."
if errorlevel 1 (
    echo ERROR: Could not open the WinDiagKit project directory.
    exit /b 1
)

echo Building WinDiagKit...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found on PATH.
    popd
    exit /b 1
)
echo Verifying 32-bit/x86 Python...
python -c "import struct, sys; sys.exit(0 if struct.calcsize('P') * 8 == 32 else 1)"
if errorlevel 1 (
    echo ERROR: This build requires a 32-bit/x86 Python installation.
    popd
    exit /b 1
)
echo.

python -m pip install -r requirements-x86.txt
if errorlevel 1 (
    popd
    exit /b 1
)

python -m PyInstaller --clean --noconfirm --noupx --onefile --windowed --paths src --version-file "scripts\windows_version_info.txt" --add-data "src\windiagkit\powershell\scripts;windiagkit\powershell\scripts" --name WinDiagKit src\gui_main.py
if errorlevel 1 (
    popd
    exit /b 1
)

if defined WINDIAGKIT_SIGN_CERT_SHA1 (
    call scripts\sign_release.bat "dist\WinDiagKit.exe"
    if errorlevel 1 (
        popd
        exit /b 1
    )
)

echo.
echo Build finished: dist\WinDiagKit.exe
echo.
echo Copy winddiagkit.ini.example to dist\winddiagkit.ini to customize it.
echo WinDiagKit itself does not export or persist collected diagnostic data.
echo SHA256:
certutil -hashfile dist\WinDiagKit.exe SHA256
popd
