@echo off
setlocal

 echo Building WinDiagKit...
 echo IMPORTANT: use a 32-bit/x86 Python installation for a 32-bit EXE.
 echo.

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

python -m PyInstaller --clean --onefile --console --name WinDiagKit main.py
if errorlevel 1 exit /b 1

 echo.
 echo Build finished: dist\WinDiagKit.exe
 echo.
 echo Note: PyInstaller --onefile extracts its runtime to a temporary directory.
 echo WinDiagKit itself does not export or persist collected diagnostic data.
