@echo off
setlocal

if "%~1"=="" (
    echo ERROR: Provide the executable to sign.
    exit /b 1
)
if not exist "%~1" (
    echo ERROR: Signing target not found: %~1
    exit /b 1
)
if not defined WINDIAGKIT_SIGN_CERT_SHA1 (
    echo ERROR: WINDIAGKIT_SIGN_CERT_SHA1 is not set.
    exit /b 1
)

where signtool.exe >nul 2>&1
if errorlevel 1 (
    echo ERROR: signtool.exe was not found.
    exit /b 1
)

signtool.exe sign /sha1 "%WINDIAGKIT_SIGN_CERT_SHA1%" /fd SHA256 /tr "http://timestamp.digicert.com" /td SHA256 "%~1"
if errorlevel 1 (
    echo ERROR: Authenticode signing failed.
    exit /b 1
)

signtool.exe verify /pa /v "%~1"
if errorlevel 1 (
    echo ERROR: Authenticode verification failed.
    exit /b 1
)

echo Authenticode signature verified: %~1
