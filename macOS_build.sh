echo ------------------------   Check Uncommitted Changes    ------------------------
echo If you see any lines below, there are uncommitted changes:
git status -s

echo ------------------------  Confirm Desktop Client Info   ------------------------
echo Have you updated the version info in desktop_client/package.json and made a
echo " commit? (y to proceed)"
read -r confirm
if [ "$confirm" != "y" ]
then
    echo Please update the version info first
    exit
fi

echo ------------------------     Build the Web Client       ------------------------
cd client || exit
npm run build
cd ..

echo ------------------------   Compile the Python Backend   ------------------------
source venv/bin/activate
pyinstaller --noconfirm --clean macOS_ictrl_be.spec

echo ----------------- Compile and Publish the Electron Frontend --------------------
cd desktop_client || exit
npm run publish
cd ..