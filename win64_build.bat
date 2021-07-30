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
call npm run make