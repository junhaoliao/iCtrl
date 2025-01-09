#!/bin/zsh

#
# Copyright (c) 2025 iCtrl Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#

echo -------------------------   Check Build Environment    -------------------------
if [[ $(pwd) != *ictrl ]] | [[ $(pwd) != *iCtrl ]]; then
    echo This script should be run from the project root directory
    echo e.g. ./publish/macOS_build.sh
    exit
fi

echo pwd satisfies requirement

if [ "$(arch)" = "arm64" ]
then
  cpu_arch="arm64"
else
  cpu_arch="x64"
fi

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
npm i
DISABLE_ESLINT_PLUGIN=true npm run build
cd ..

echo ------------------------   Compile the Python Backend   ------------------------
source venv/bin/activate
pyinstaller --noconfirm --clean ./publish/ictrl_be.spec

echo ----------------- Compile the Electron Frontend --------------------
cd desktop_client || exit
npm i
npm run make
cd ..

echo ----------------- Publish the Application --------------------
cd  "./desktop_client/out/iCtrl Desktop-darwin-$cpu_arch" || exit
ditto -c -k --sequesterRsrc --keepParent --zlibCompressionLevel 9 "./iCtrl Desktop.app" "ictrl-desktop-darwin-$cpu_arch.zip"
cd ../../..
node ./publish/mac_publish.js junhaoliao iCtrl \
 "./desktop_client/out/iCtrl Desktop-darwin-$cpu_arch/ictrl-desktop-darwin-$cpu_arch.zip" "ictrl-desktop-darwin-$cpu_arch.zip"
node ./publish/mac_publish.js junhaoliao iCtrl \
 "./desktop_client/out/make/ictrl-desktop-setup.dmg" "ictrl-desktop-darwin-$cpu_arch.dmg"
