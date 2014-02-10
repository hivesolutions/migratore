:: turns off the echo
@echo off

:: sets the temporary variables
set SCRIPT_NAME=migratore_pypi.py

:: executes the initial python script with
:: the provided arguments
python %~dp0/%SCRIPT_NAME% %*

:: exits the process
exit /b %ERRORLEVEL%
