@echo off

echo ------------------------   Check Uncommitted Changes    ------------------------
echo If you see any lines below, there are uncommitted changes:
git status -s

echo ------------------------  Confirm Desktop Client Info   ------------------------
echo Have you updated the version info in desktop_client/package.json and made a
echo  commit? (y to proceed)
set /p confirm=""

if not "%confirm%"=="y" (
    echo Please update the version info first
    goto :EOF
)

@echo on
:: build the web client
cd client
call npm run build
cd ..

:: enable the virtual environment
call venv\Scripts\activate.bat

:: compile the Python backend
pyinstaller --noconfirm --clean win64_ictrl_be.spec

:: make the desktop client
cd desktop_client
call npm run publish