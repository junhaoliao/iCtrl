@echo off

echo -------------------------   Check Build Environment    -------------------------
if "%cd:~-7%"=="publish"  (
    echo This script should be run from the project root directory
    echo e.g. .\publish\win64_build.bat
    exit
)

echo pwd satisfies requirement


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
call npm i --force
:: FIXME: remove this when all ESLint violations are addressed
set DISABLE_ESLINT_PLUGIN=true
call npm run build
cd ..

:: enable the virtual environment
call venv\Scripts\activate.bat

:: compile the Python backend
pyinstaller --noconfirm --clean .\publish\ictrl_be.spec

:: make the desktop client
cd desktop_client
call npm i
call npm run publish
cd ..