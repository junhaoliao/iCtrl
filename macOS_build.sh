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
npm i --force
npm run build
cd ..

echo ------------------------   Compile the Python Backend   ------------------------
source venv/bin/activate
pyinstaller --noconfirm --clean macOS_ictrl_be.spec

echo ----------------- Compile the Electron Frontend --------------------
cd desktop_client || exit
npm i
npm run make
cd ..

echo ----------------- Publish the Application --------------------
cd  "./desktop_client/out/iCtrl Desktop-darwin-$(arch)" || exit
ditto -c -k --sequesterRsrc --keepParent --zlibCompressionLevel 9 "./iCtrl Desktop.app" "ictrl-desktop-darwin-$(arch).zip"
cd ../../..
node publish/mac_publish.js junhaoliao api_test \
 "./desktop_client/out/iCtrl Desktop-darwin-$(arch)/ictrl-desktop-darwin-$(arch).zip" "ictrl-desktop-darwin-$(arch).zip"
node publish/mac_publish.js junhaoliao api_test \
 "./desktop_client/out/make/ictrl-desktop-setup.dmg" "ictrl-desktop-darwin-$(arch).dmg"
