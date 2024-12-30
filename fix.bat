@echo off
setlocal enabledelayedexpansion

:: Check if Python 3.10.0 is installed and in PATH
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Installing Python 3.10.0...

    :: Download and install Python 3.10.0
    set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
    set "PYTHON_INSTALLER=python-3.10.0-amd64.exe"
    
    echo Downloading Python installer...
    powershell -Command "Invoke-WebRequest -Uri %PYTHON_INSTALLER_URL% -OutFile %PYTHON_INSTALLER%"
    
    :: Install Python silently and add to PATH
    echo Installing Python 3.10.0...
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1

    :: Clean up installer
    del %PYTHON_INSTALLER%

    echo Python 3.10.0 installation complete.
) else (
    echo Python is already installed.
)

:: Install required Python packages
echo Installing required Python packages...
pip install customtkinter
pip install keyboard
pip install mouse
pip install screeninfo
pip install configparser

:: Uninstall crypto and pycrypto if present
echo Uninstalling crypto and pycrypto (if installed)...
pip uninstall -y crypto
pip uninstall -y pycrypto

:: Install pycryptodome
echo Installing pycryptodome...
pip install pycryptodome

echo All tasks completed successfully.
pause
